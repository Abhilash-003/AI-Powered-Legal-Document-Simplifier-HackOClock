"""Q&A over clauses via embedding retrieval + Claude answer (with Advisor tool-use).

Two retrieval sources:
  1. The user's uploaded contract — retrieve top-3 clauses by cosine-sim over
     their per-clause embeddings (done upfront, passed as grounding).
  2. Our Indian legal reference corpus — Claude may consult via
     `consult_lexbert_advisor` to ground its answer in Indian statute references.
"""
import json
import re
from dataclasses import dataclass

import numpy as np
from anthropic import Anthropic
from dotenv import load_dotenv

from . import embedder, legal_advisor
from .claude_analyzer import ADVISOR_TOOL

load_dotenv()

import os as _os_for_model
MODEL = _os_for_model.environ.get("LEXAI_MODEL", "claude-sonnet-4-6")
MAX_TOKENS = 900
TOP_K = 3
MAX_TOOL_TURNS = 2


@dataclass
class RetrievedClause:
    clause_id: int
    clause_type: str
    text: str
    statute: str
    section: str
    similarity: float


QA_PROMPT = """You are an Indian legal advisor answering a user's question about a contract they are reviewing.

USER QUESTION: {question}

RETRIEVED CLAUSES from the user's own contract (top-3 most relevant to the question):
{clauses_block}

CONVERSATION SO FAR:
{history_block}

TOOLS:
  You have access to `consult_lexbert_advisor`. Use it to retrieve Indian legal references from our corpus when you need to verify an Indian statute citation. Call it at most twice.

TASK: Answer the user's question grounded in the retrieved clauses and any Indian statute references returned by the Advisor. Cite clause IDs like "Clause 4" or "Clauses 2 and 7". Plain-spoken, no legalese. If the answer depends on facts not in the clauses, say so. 2-5 sentences.

Final response should be only the answer text (no JSON, no code fences)."""


# Anchor on the word "clause[s]" (word boundary on both sides), then capture the
# following comma/"and"-joined list of numbers. Lets us handle "clause 5",
# "Clauses 2 and 7", "clauses #3, 9, 11", etc.
CLAUSE_REF_RE = re.compile(
    r"\bclauses?\b\s*((?:#?\s*\d+\s*(?:(?:,|and|&)\s*)?)+)",
    re.IGNORECASE,
)
NUM_RE = re.compile(r"\d+")


def _extract_clause_refs(query: str) -> list[int]:
    out: list[int] = []
    for chunk in CLAUSE_REF_RE.findall(query):
        for n in NUM_RE.findall(chunk):
            cid = int(n)
            if cid not in out:
                out.append(cid)
    return out


def retrieve(query: str, clauses: list[dict]) -> list[RetrievedClause]:
    if not clauses:
        return []
    q_emb = embedder.embed_one(query)
    emb_matrix = np.vstack([c["embedding"] for c in clauses])
    sims = emb_matrix @ q_emb

    id_to_pos = {c["clause_id"]: i for i, c in enumerate(clauses)}
    forced_positions: list[int] = []
    for cid in _extract_clause_refs(query):
        if cid in id_to_pos:
            forced_positions.append(id_to_pos[cid])

    # Forced refs first (preserve user-typed order), then fill with semantic top-K
    seen = set(forced_positions)
    order = list(forced_positions)
    for i in np.argsort(-sims):
        i = int(i)
        if i in seen:
            continue
        order.append(i)
        seen.add(i)
        if len(order) >= max(TOP_K, len(forced_positions) + TOP_K):
            break

    # Cap at TOP_K unless explicit refs push us higher
    cap = max(TOP_K, len(forced_positions))
    order = order[:cap]

    return [
        RetrievedClause(
            clause_id=clauses[i]["clause_id"],
            clause_type=clauses[i]["clause_type"],
            text=clauses[i]["text"],
            statute=clauses[i].get("statute", ""),
            section=clauses[i].get("section", ""),
            similarity=float(sims[i]),
        )
        for i in order
    ]


def _extract_text(blocks) -> str:
    parts = []
    for b in blocks:
        if hasattr(b, "type") and b.type == "text":
            parts.append(b.text)
        elif hasattr(b, "text"):
            parts.append(b.text)
    return "\n".join(parts).strip()


def answer(question: str, clauses: list[dict], history: list[dict], model: str = MODEL) -> dict:
    """Q&A with Advisor consultation available.
    history format: list of {'role': 'user'|'assistant', 'content': str}
    Returns {answer, retrieved}.
    """
    retrieved = retrieve(question, clauses)
    if not retrieved:
        return {"answer": "Upload a document first so I have something to reference.", "retrieved": []}

    clauses_block = "\n".join(
        f"  [Clause {r.clause_id} · {r.clause_type} · {r.statute} {r.section}]\n  {r.text}"
        for r in retrieved
    )
    history_block = (
        "\n".join(f"  {h['role']}: {h['content']}" for h in history[-6:]) if history else "  (none)"
    )
    prompt = QA_PROMPT.format(
        question=question, clauses_block=clauses_block, history_block=history_block
    )

    client = Anthropic()
    messages = [{"role": "user", "content": prompt}]

    for turn in range(MAX_TOOL_TURNS + 1):
        resp = client.messages.create(
            model=model,
            max_tokens=MAX_TOKENS,
            tools=[ADVISOR_TOOL],
            messages=messages,
        )

        if resp.stop_reason != "tool_use":
            return {"answer": _extract_text(resp.content), "retrieved": retrieved}

        # Handle tool call(s)
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

    return {"answer": "(answer unavailable — max tool turns exceeded)", "retrieved": retrieved}
