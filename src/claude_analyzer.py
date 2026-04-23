"""Parallel Claude analysis with LexBERT tool-use.

Per clause, Claude (the Executor) may emit a `consult_lexbert_advisor` tool call
to retrieve grounded Indian legal references before producing its final analysis.
This implements the Advisor-Executor pattern as a round-trip, not a one-shot.

N parallel Claude conversations via asyncio.gather — each may include up to 2
tool-use turns before producing the final JSON.
"""
import asyncio
import json
import re
from dataclasses import dataclass
from typing import Optional

from anthropic import AsyncAnthropic
from dotenv import load_dotenv

from . import legal_advisor

load_dotenv()

import os as _os_for_model
MODEL = _os_for_model.environ.get("LEXAI_MODEL", "claude-sonnet-4-6")
MAX_TOKENS = 1000
MAX_CONCURRENCY = 20
MAX_TOOL_TURNS = 2  # Claude may consult the Advisor at most 2×/clause


@dataclass
class ClauseAnalysis:
    statute: str
    section: str
    flag: str
    plain_english: str
    negotiation_script: str
    jurisdiction_flag: Optional[str]


# ------------- Tool definition -------------
ADVISOR_TOOL = {
    "name": "consult_lexbert_advisor",
    "description": (
        "Consult LexBERT Advisor. Retrieves the top-3 most semantically similar Indian legal "
        "reference clauses from a curated corpus of 6,400 statute-grounded Indian contract clauses. "
        "Each reference comes tagged with its Indian Act + section + risk level. "
        "Use this tool whenever you want to ground your Indian statute citation in retrieved evidence "
        "— especially if uncertain about which Indian Act applies or the exact section number. "
        "You may call this up to 2 times per clause."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": (
                    "A short description of the Indian legal topic or clause pattern to look up. "
                    "E.g., 'eviction clause waiving 15-day notice under Transfer of Property Act', "
                    "'post-employment non-compete restraint', 'PF waiver in employment contract'."
                ),
            }
        },
        "required": ["query"],
    },
}

# ------------- Prompt -------------
ANALYZE_PROMPT = """You are an Indian legal advisor helping an ordinary person understand a clause they are about to sign.

CLAUSE:
<<<
{clause_text}
>>>

CONTEXT (from our fine-tuned InLegalBERT classifier):
  clause_type: {clause_type}
  risk_level: {risk_level}

TOOLS:
  You have access to `consult_lexbert_advisor`. Use it to retrieve 3 similar Indian legal references from our corpus, each tagged with the applicable Indian Act + section. Call it at the start to ground your statute citation — especially helpful when you're not sure of the exact section number.

TASK: After consulting the Advisor (if useful), return ONE JSON object with exactly these keys:

  "statute": Canonical Indian Act name (e.g. "Indian Contract Act 1872", "Transfer of Property Act 1882", "Industrial Disputes Act 1947", "Employees' Provident Fund and Miscellaneous Provisions Act 1952", "Employees' State Insurance Act 1948", "Industrial Employment (Standing Orders) Act 1946", "Copyright Act 1957", "Arbitration and Conciliation Act 1996", "Consumer Protection Act 2019", "State Rent Control Act"). Ground this in what the Advisor returned when possible.

  "section": Specific section number (e.g. "Section 27", "Section 106", "Section 25F", "Section 6", "Section 39", "Section 17", "Section 11"). Never invent a section. If the Advisor's references disagree, pick the most-cited one. If unsure, write "General provisions".

  "flag": One short sentence naming the legal concern. E.g. "Post-employment non-competes are void under Section 27" or "Waiver of statutory eviction notice is void".

  "plain_english": 2-3 sentence rewrite in plain English that an ordinary Indian adult can understand. No legalese.

  "negotiation_script": Exact counter-language the user can send to the other party. 1-3 sentences, polite but firm, first person ("I would request...", "I respectfully cannot agree to..."). If the clause is standard-risk, a brief acknowledgement is fine.

  "jurisdiction_flag": null if the clause applies Indian law normally, OR a short string if the clause tries to apply non-Indian law / foreign court / foreign arbitration seat.

Final output must be ONLY the JSON object. No preamble, no markdown fences, no commentary after."""


def _strip_code_fence(s: str) -> str:
    s = s.strip()
    m = re.match(r"^```(?:json)?\s*(.*?)\s*```$", s, re.DOTALL)
    return m.group(1).strip() if m else s


def _extract_text(content_blocks) -> str:
    """Extract text from assistant content blocks (skipping tool_use blocks)."""
    parts = []
    for b in content_blocks:
        if hasattr(b, "type") and b.type == "text":
            parts.append(b.text)
        elif hasattr(b, "text"):
            parts.append(b.text)
    return "\n".join(parts).strip()


def _parse_analysis(text: str) -> ClauseAnalysis:
    raw = _strip_code_fence(text)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # last-ditch: try to find the first {...} block
        m = re.search(r"\{[\s\S]*\}", raw)
        if m:
            try:
                data = json.loads(m.group(0))
            except json.JSONDecodeError:
                data = {}
        else:
            data = {}
    return ClauseAnalysis(
        statute=(data.get("statute") or "").strip() or "Indian Contract Act 1872",
        section=(data.get("section") or "").strip() or "General provisions",
        flag=(data.get("flag") or "").strip(),
        plain_english=(data.get("plain_english") or "").strip(),
        negotiation_script=(data.get("negotiation_script") or "").strip(),
        jurisdiction_flag=data.get("jurisdiction_flag"),
    )


async def _analyze_one(client: AsyncAnthropic, sem: asyncio.Semaphore,
                       clause_text: str, clause_type: str, risk_level: str,
                       model: str) -> ClauseAnalysis:
    messages = [
        {"role": "user", "content": ANALYZE_PROMPT.format(
            clause_text=clause_text, clause_type=clause_type, risk_level=risk_level
        )}
    ]
    async with sem:
        for turn in range(MAX_TOOL_TURNS + 1):
            resp = await client.messages.create(
                model=model,
                max_tokens=MAX_TOKENS,
                tools=[ADVISOR_TOOL],
                messages=messages,
            )

            if resp.stop_reason != "tool_use":
                return _parse_analysis(_extract_text(resp.content))

            # Collect every tool_use block from this turn; run them; return tool_results
            messages.append({"role": "assistant", "content": resp.content})
            tool_results = []
            for block in resp.content:
                if hasattr(block, "type") and block.type == "tool_use":
                    if block.name == "consult_lexbert_advisor":
                        q = block.input.get("query", "") if hasattr(block, "input") else ""
                        try:
                            refs = legal_advisor.consult(q, k=3)
                            result_text = legal_advisor.format_for_claude(refs)
                        except Exception as e:
                            result_text = f"(advisor error: {e})"
                    else:
                        result_text = f"(unknown tool: {block.name})"
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_text,
                    })
            messages.append({"role": "user", "content": tool_results})

    # Hit max turns without final response — fallback
    return ClauseAnalysis(
        statute="(unresolved)", section="(unresolved)", flag="",
        plain_english="(analysis unavailable — max tool turns exceeded)",
        negotiation_script="", jurisdiction_flag=None,
    )


async def analyze_all(clauses_with_context: list[dict], model: str = MODEL) -> list[ClauseAnalysis]:
    """N parallel Claude conversations, each may include LexBERT tool calls.
    Each input dict: clause_text, clause_type, risk_level.
    """
    client = AsyncAnthropic()
    sem = asyncio.Semaphore(MAX_CONCURRENCY)
    tasks = [
        _analyze_one(client, sem, c["clause_text"], c["clause_type"], c["risk_level"], model)
        for c in clauses_with_context
    ]
    return await asyncio.gather(*tasks)


def analyze_all_sync(clauses_with_context: list[dict], model: str = MODEL) -> list[ClauseAnalysis]:
    return asyncio.run(analyze_all(clauses_with_context, model))
