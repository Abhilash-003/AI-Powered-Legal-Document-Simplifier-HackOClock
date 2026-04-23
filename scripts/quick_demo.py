#!/usr/bin/env python3
"""Quick live-inference demo for mid-review.

Loads both fine-tuned models, classifies 6 sample Indian contract clauses,
prints type + risk + confidence. Takes ~10 seconds end-to-end.

Run:   python3 scripts/quick_demo.py   (venv auto-activates)
"""
# ---- auto-activate venv ----
import os
import sys
from pathlib import Path

_VENV_DIR = Path(__file__).resolve().parents[1] / ".venv"
_VENV_PY = _VENV_DIR / "bin" / "python3"
# Compare raw path, NOT resolved (venv python is a symlink to system python)
if _VENV_PY.exists() and not sys.executable.startswith(str(_VENV_DIR)):
    os.execv(str(_VENV_PY), [str(_VENV_PY), *sys.argv])
# ---- end auto-venv ----

import time

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

DEVICE = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
MAX_LEN = 384

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[91m"
AMBER = "\033[93m"
GREEN = "\033[92m"
BLUE = "\033[94m"
CYAN = "\033[96m"

# six real-style Indian contract clauses, varied across types and risk levels
SAMPLES = [
    ("Upon any default by the Lessee, the Licensor shall have the absolute right to enter the "
     "said premises and resume physical possession without any prior notice or legal process, "
     "notwithstanding any provisions of the Transfer of Property Act, 1882, or any other law in force.",
     "expected: eviction · illegal"),
    ("The Consultant hereby covenants that upon cessation of this engagement for any reason, he "
     "shall not, for the remainder of his natural working life, engage in or render services to "
     "any enterprise competing with the Company's business anywhere in India or abroad.",
     "expected: non_compete · illegal"),
    ("The monthly rent of Rs. 35,000/- shall be escalated annually by seven per cent (7%) on the "
     "anniversary date of this Agreement, in accordance with the provisions of the Karnataka "
     "Rent Control Act, 2001, with thirty (30) days' prior written notice to the Lessee.",
     "expected: rent_escalation · standard"),
    ("The Company shall deduct twelve per cent (12%) of the Employee's basic wages as employee "
     "contribution towards the Employees' Provident Fund and make a matching employer "
     "contribution of twelve per cent (12%), in compliance with Section 6 of the Employees' "
     "Provident Funds and Miscellaneous Provisions Act, 1952.",
     "expected: pf_esic · standard"),
    ("All disputes arising out of this Agreement shall be referred to arbitration before a sole "
     "arbitrator appointed exclusively by the Managing Director of the Company, whose decision "
     "shall be final, binding and not subject to any challenge in any court of law.",
     "expected: arbitration · aggressive"),
    ("The Employee shall serve a probation period of six (6) months from the Date of Joining, "
     "extendable once by a further period not exceeding three (3) months with reasons recorded "
     "in writing, in accordance with Standing Order 14 of the Industrial Employment (Standing "
     "Orders) Act, 1946.",
     "expected: probation · standard"),
]


def load_head(path):
    tok = AutoTokenizer.from_pretrained(path)
    model = AutoModelForSequenceClassification.from_pretrained(path).to(DEVICE).eval()
    return tok, model


def classify(text, tok, model):
    enc = tok(text, return_tensors="pt", truncation=True, max_length=MAX_LEN, padding="max_length").to(DEVICE)
    with torch.no_grad():
        logits = model(**enc).logits
    probs = torch.softmax(logits, dim=-1)[0]
    top = probs.argmax().item()
    conf = float(probs.max())
    return model.config.id2label[top], conf


def risk_color(risk):
    return {"illegal": RED, "aggressive": AMBER, "standard": GREEN}.get(risk, DIM)


def main():
    print(f"\n{BOLD}{CYAN}LexAI — Live Inference Demo{RESET}")
    print(f"{DIM}Loading fine-tuned LexBERT (InLegalBERT + LoRA, 0.28% params trained)...{RESET}")
    t0 = time.time()
    type_tok, type_model = load_head("models/lexbert-type")
    risk_tok, risk_model = load_head("models/lexbert-risk")
    load_t = time.time() - t0
    print(f"{DIM}  loaded in {load_t:.1f}s · device={DEVICE}{RESET}\n")

    print(f"{BOLD}Classifying 6 sample Indian contract clauses…{RESET}\n")
    t0 = time.time()
    for i, (text, note) in enumerate(SAMPLES, 1):
        ct, ctc = classify(text, type_tok, type_model)
        rl, rlc = classify(text, risk_tok, risk_model)
        rc = risk_color(rl)
        print(f"{BOLD}[{i}]{RESET} {DIM}{note}{RESET}")
        print(f"    {DIM}{text[:120]}…{RESET}")
        print(f"    type  ─▶ {BLUE}{ct}{RESET}  {DIM}({ctc*100:.1f}% conf){RESET}")
        print(f"    risk  ─▶ {rc}{rl.upper()}{RESET}  {DIM}({rlc*100:.1f}% conf){RESET}\n")
    infer_t = time.time() - t0
    print(f"{DIM}  6 clauses × 2 heads = 12 classifications in {infer_t:.2f}s  ({(infer_t/12)*1000:.0f} ms/classification){RESET}")
    print(f"{DIM}  each LoRA adapter: 1.2 MB · merged base: 421 MB · both models load in {load_t:.1f}s{RESET}\n")


if __name__ == "__main__":
    main()
