"""Generate Indian contract clauses via Claude, statute-grounded, 10 classes + risk.

Resumable: skips clauses already in output file.
Output: data/synthetic/indian_clauses.jsonl
"""
import json
import os
import random
import sys
import time
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

OUT = Path("data/synthetic/indian_clauses.jsonl")
OUT.parent.mkdir(parents=True, exist_ok=True)

MODEL = "claude-sonnet-4-6"
PER_CLASS = 80
RISK_MIX = [("standard", 0.45), ("aggressive", 0.35), ("illegal", 0.20)]

CLAUSES = {
    "termination": {
        "statute": "Industrial Disputes Act 1947 (Section 25F on retrenchment); Industrial Employment (Standing Orders) Act 1946",
        "doc_types": ["employment contract", "service agreement"],
    },
    "arbitration": {
        "statute": "Arbitration and Conciliation Act 1996 (Section 11 on arbitrator appointment; seat and venue)",
        "doc_types": ["commercial contract", "services agreement", "employment contract"],
    },
    "non_compete": {
        "statute": "Indian Contract Act 1872 Section 27 (post-employment non-competes are void; only enforceable during employment or on sale of goodwill)",
        "doc_types": ["employment contract", "founder agreement"],
    },
    "liability": {
        "statute": "Indian Contract Act 1872 (Sections 73-74 on damages); Consumer Protection Act 2019 Section 2(47) on unfair contract terms",
        "doc_types": ["services agreement", "consumer terms-of-service", "supply contract"],
    },
    "notice_period": {
        "statute": "Industrial Employment (Standing Orders) Act 1946 (Schedule Item 9); state-specific Shops and Establishments Acts",
        "doc_types": ["employment contract"],
    },
    "ip_ownership": {
        "statute": "Copyright Act 1957 Section 17 (work-for-hire); Patents Act 1970 (inventor rights assignment)",
        "doc_types": ["employment contract", "services agreement", "founder agreement"],
    },
    "rent_escalation": {
        "statute": "State Rent Control Acts (e.g., Delhi Rent Act 1995, Maharashtra Rent Control Act 1999); Transfer of Property Act 1882",
        "doc_types": ["leave and license agreement", "lease deed", "rental agreement"],
    },
    "eviction": {
        "statute": "Transfer of Property Act 1882 Section 106 (15-day notice for month-to-month tenancy); state Rent Control Acts on grounds for eviction",
        "doc_types": ["leave and license agreement", "lease deed", "rental agreement"],
    },
    "pf_esic": {
        "statute": "Employees Provident Fund and Miscellaneous Provisions Act 1952 Section 6; Employees State Insurance Act 1948 Section 39 (mandatory contributions, cannot be contracted out)",
        "doc_types": ["employment contract", "contract labour agreement"],
    },
    "probation": {
        "statute": "Industrial Employment (Standing Orders) Act 1946 (Standing Order 14 — reasonable probation, typically 3-6 months); state Shops and Establishments Acts",
        "doc_types": ["employment contract"],
    },
}

RISK_DESCRIPTIONS = {
    "standard": "lawful, fair, balanced — reflects standard Indian market practice",
    "aggressive": "legally valid but pushes boundaries — one-sided in favor of drafter, tests enforceability limits",
    "illegal": "violates the applicable Indian statute — void, unenforceable, or against public policy",
}


def already_done():
    """Return dict of (clause_type) -> count already generated."""
    counts = {}
    if OUT.exists():
        for line in OUT.open():
            try:
                rec = json.loads(line)
                counts[rec["clause_type"]] = counts.get(rec["clause_type"], 0) + 1
            except Exception:
                pass
    return counts


def pick_risk():
    r = random.random()
    acc = 0.0
    for level, p in RISK_MIX:
        acc += p
        if r <= acc:
            return level
    return "standard"


def prompt_for(clause_type, risk, doc_type):
    meta = CLAUSES[clause_type]
    return f"""You are drafting a clause for a real Indian {doc_type}. Write ONE {clause_type} clause at a "{risk}" risk level.

Risk level meaning: {RISK_DESCRIPTIONS[risk]}.
Applicable Indian law: {meta['statute']}.

Requirements:
- Use authentic Indian legal English (e.g., "Lessor/Lessee", "WHEREAS", "shall", "Rs."/"INR", "said premises", specific statute references).
- India-specific context: Indian states, Indian parties (Pvt Ltd / LLP / sole proprietorship), Indian currency, Indian statutes.
- For "aggressive": include one-sided terms, short deadlines, broad discretion for drafter.
- For "illegal": explicitly contradict the applicable statute (e.g., post-employment non-compete beyond Contract Act Section 27; termination without §25F notice; waiver of PF contribution).
- Length: 2-8 sentences. Realistic, not a whole contract.
- Output ONLY the clause text. No preamble, no explanation, no markdown, no quotes around the clause.

Write the clause now."""


def main():
    client = Anthropic()
    done = already_done()
    print(f"Already done: {done}", flush=True)

    total_target = PER_CLASS * len(CLAUSES)
    total_done = sum(done.values())
    print(f"Target: {total_target}, Done: {total_done}, Remaining: {total_target - total_done}", flush=True)

    for clause_type, meta in CLAUSES.items():
        needed = PER_CLASS - done.get(clause_type, 0)
        if needed <= 0:
            print(f"[skip] {clause_type}: already have {done[clause_type]}", flush=True)
            continue
        print(f"[start] {clause_type}: need {needed}", flush=True)
        for i in range(needed):
            risk = pick_risk()
            doc_type = random.choice(meta["doc_types"])
            try:
                resp = client.messages.create(
                    model=MODEL,
                    max_tokens=600,
                    messages=[{"role": "user", "content": prompt_for(clause_type, risk, doc_type)}],
                )
                text = resp.content[0].text.strip()
                if text.startswith('"') and text.endswith('"'):
                    text = text[1:-1]
                record = {
                    "clause_text": text,
                    "clause_type": clause_type,
                    "risk_level": risk,
                    "indian_law": meta["statute"],
                    "doc_type": doc_type,
                    "source": "claude_synth_v1",
                }
                with OUT.open("a") as f:
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
                print(f"  {clause_type} [{risk}] {i+1}/{needed}", flush=True)
            except Exception as e:
                print(f"  ERROR {clause_type} #{i}: {e}", flush=True)
                time.sleep(2)


if __name__ == "__main__":
    main()
