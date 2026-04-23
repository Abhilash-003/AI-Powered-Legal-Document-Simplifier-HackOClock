"""Document-level summary: one Claude call after all clause analyses complete.

Produces the top-of-page banner: doc type, overall risk posture, top 3 concerns.
"""
import json
import re
from dataclasses import dataclass

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

import os as _os_for_model
MODEL = _os_for_model.environ.get("LEXAI_MODEL", "claude-sonnet-4-6")
MAX_TOKENS = 600


@dataclass
class DocSummary:
    doc_type: str       # e.g. "Residential rental agreement (Mumbai)"
    risk_posture: str   # "low" | "medium" | "high"
    top_concerns: list  # list of strings, up to 3
    summary_line: str   # single-sentence headline


SUMMARY_PROMPT = """You are summarizing an Indian legal contract after clause-by-clause risk analysis.

PER-CLAUSE RISK SUMMARY:
{clause_list}

TASK: Return ONE JSON object with exactly these keys:
  "doc_type": one-phrase description of what kind of contract this is, with location if inferrable (e.g. "Residential leave-and-license agreement, Mumbai" or "IT services employment contract, India")
  "risk_posture": "low" if mostly standard, "medium" if some aggressive, "high" if any illegal clauses present
  "top_concerns": array of up to 3 short strings — each names the single most important concern, referencing the clause index (e.g. "Clause 4 waives statutory 15-day eviction notice under TP Act Section 106")
  "summary_line": one sentence a user would hear first — headline style (e.g. "This rental agreement has 3 high-risk clauses that conflict with Maharashtra Rent Control Act protections.")

OUTPUT: ONLY the JSON. No preamble, no markdown fences."""


def _strip_code_fence(s: str) -> str:
    s = s.strip()
    m = re.match(r"^```(?:json)?\s*(.*?)\s*```$", s, re.DOTALL)
    return m.group(1).strip() if m else s


def summarize(clauses: list[dict], model: str = MODEL) -> DocSummary:
    """clauses: list of dicts with clause_id, clause_type, final_risk, statute, text (short)."""
    clause_list = "\n".join(
        f"  [{c['clause_id']}] {c['clause_type']} · {c['final_risk']} · {c.get('statute','')} · "
        f"{(c.get('text','') or '')[:120]}..."
        for c in clauses
    )
    client = Anthropic()
    resp = client.messages.create(
        model=model,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": SUMMARY_PROMPT.format(clause_list=clause_list)}],
    )
    raw = _strip_code_fence(resp.content[0].text)
    try:
        data = json.loads(raw)
        return DocSummary(
            doc_type=data.get("doc_type", "Contract"),
            risk_posture=data.get("risk_posture", "medium"),
            top_concerns=data.get("top_concerns", []) or [],
            summary_line=data.get("summary_line", "").strip(),
        )
    except json.JSONDecodeError:
        return DocSummary(doc_type="Contract", risk_posture="medium", top_concerns=[],
                          summary_line="(summary unavailable)")
