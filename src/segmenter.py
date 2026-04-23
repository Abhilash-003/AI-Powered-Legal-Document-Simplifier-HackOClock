"""Claude-based clause segmentation.

One API call per document. Takes full_text, returns clauses with approximate
character offsets. Downstream maps these to per-page bboxes via parser.
"""
import json
import re
from dataclasses import dataclass

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

import os as _os_for_model
MODEL = _os_for_model.environ.get("LEXAI_MODEL", "claude-sonnet-4-6")
MAX_TOKENS = 8000


@dataclass
class Clause:
    id: int
    text: str
    char_start: int
    char_end: int


SEGMENT_PROMPT = """You are segmenting an Indian legal contract into its individual clauses for downstream risk analysis.

CONTRACT TEXT:
<<<
{full_text}
>>>

TASK: Return a JSON array of clauses. Include every substantive clause as a separate entry. Preserve nested sub-clauses as separate entries (e.g. clause 5, 5(a), 5(b) are three entries). Skip pure boilerplate like the WHEREAS preamble unless it imposes actual obligations. Include schedules/annexures clauses if they are operative.

Each entry MUST have exactly these keys:
  "id": 0-indexed sequential integer
  "text": the verbatim clause text as it appears in the contract
  "approx_start": approximate character offset where this clause begins in the input
  "approx_end": approximate character offset where this clause ends

OUTPUT FORMAT: ONLY the JSON array. No preamble, no markdown fences, no explanation. The response must parse as JSON directly.

Example:
[
  {{"id": 0, "text": "The Lessee shall pay a monthly rent of Rs. 25,000...", "approx_start": 412, "approx_end": 567}},
  {{"id": 1, "text": "This Agreement shall commence on...", "approx_start": 568, "approx_end": 698}}
]"""


def _strip_code_fence(s: str) -> str:
    s = s.strip()
    m = re.match(r"^```(?:json)?\s*(.*?)\s*```$", s, re.DOTALL)
    return m.group(1).strip() if m else s


def segment(full_text: str, model: str = MODEL) -> list[Clause]:
    """One Claude call → list of clauses with approximate char offsets."""
    client = Anthropic()
    resp = client.messages.create(
        model=model,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": SEGMENT_PROMPT.format(full_text=full_text)}],
    )
    raw = resp.content[0].text
    raw = _strip_code_fence(raw)
    data = json.loads(raw)
    clauses: list[Clause] = []
    for item in data:
        text = item.get("text", "").strip()
        if not text:
            continue
        start = _resolve_offset(full_text, text, item.get("approx_start", 0))
        end = start + len(text)
        clauses.append(Clause(id=len(clauses), text=text, char_start=start, char_end=end))
    return clauses


def _resolve_offset(full_text: str, clause_text: str, approx_start: int) -> int:
    """Claude's approx offsets are inexact — snap to the actual substring location."""
    # try near the approx offset first
    window_start = max(0, approx_start - 200)
    hit = full_text.find(clause_text, window_start)
    if hit != -1:
        return hit
    # fallback: find first occurrence anywhere
    hit = full_text.find(clause_text)
    if hit != -1:
        return hit
    # last resort: find first 80 chars of the clause (handles minor Claude paraphrase)
    needle = clause_text[:80]
    hit = full_text.find(needle)
    return hit if hit != -1 else approx_start
