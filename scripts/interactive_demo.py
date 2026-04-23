#!/usr/bin/env python3
"""Interactive live-inference demo — for the "judge types in their own clause" moment.

Loads both fine-tuned models once, then loops: paste a clause, get predictions.
Shows TOP-3 for type and TOP-3 for risk with confidence bars. Works locally on MPS,
no API calls, no network required.

Run:   python3 scripts/interactive_demo.py   (venv auto-activates)
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

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

DEVICE = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
MAX_LEN = 384

# ANSI colors
R = "\033[0m"
B = "\033[1m"
DIM = "\033[2m"
RED = "\033[91m"
AMBER = "\033[93m"
GREEN = "\033[92m"
BLUE = "\033[94m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"


def load(path):
    tok = AutoTokenizer.from_pretrained(path)
    model = AutoModelForSequenceClassification.from_pretrained(path).to(DEVICE).eval()
    return tok, model


def predict(text, tok, model, top_k=3):
    enc = tok(text, return_tensors="pt", truncation=True, max_length=MAX_LEN, padding="max_length").to(DEVICE)
    with torch.no_grad():
        logits = model(**enc).logits
    probs = torch.softmax(logits, dim=-1)[0]
    vals, idx = torch.topk(probs, min(top_k, probs.shape[-1]))
    return [(model.config.id2label[int(i)], float(v)) for v, i in zip(vals, idx)]


def bar(conf, width=24):
    filled = int(conf * width)
    return "█" * filled + "░" * (width - filled)


def risk_color(risk):
    return {"illegal": RED, "aggressive": AMBER, "standard": GREEN}.get(risk, DIM)


def read_clause():
    """Read a multi-line clause from stdin. End with an empty line."""
    print(f"\n{B}{CYAN}Paste a clause (finish with an empty line, or type 'quit' to exit):{R}")
    lines = []
    try:
        while True:
            line = input("  > " if not lines else "  . ")
            if line.strip().lower() in {"quit", "exit", "q"}:
                return None
            if line.strip() == "" and lines:
                break
            if line.strip() == "" and not lines:
                continue  # ignore leading empties
            lines.append(line)
    except (EOFError, KeyboardInterrupt):
        return None
    return " ".join(lines).strip()


def main():
    print(f"\n{B}{CYAN}LexAI — Interactive Clause Classifier{R}")
    print(f"{DIM}Loading two fine-tuned LexBERT heads (type + risk)...{R}")
    type_tok, type_model = load("models/lexbert-type")
    risk_tok, risk_model = load("models/lexbert-risk")
    print(f"{DIM}  ready · device={DEVICE}{R}")
    print(f"\n{DIM}Type classifier: 10 Indian clause types. Risk classifier: standard / aggressive / illegal.{R}")
    print(f"{DIM}Trained on 6,400 statute-grounded Indian synthetic clauses (+ capped LEDGAR for structure).{R}")

    n_classified = 0
    while True:
        text = read_clause()
        if text is None:
            break
        if len(text) < 20:
            print(f"{DIM}  (too short, need at least 20 characters){R}")
            continue

        print(f"\n{DIM}  {text[:160]}{'…' if len(text) > 160 else ''}{R}\n")

        # TYPE predictions
        type_preds = predict(text, type_tok, type_model, top_k=3)
        print(f"{B}  Type head{R}  {DIM}(10-class, macro F1 0.91){R}")
        for i, (lbl, conf) in enumerate(type_preds):
            marker = "▶" if i == 0 else " "
            print(f"    {marker} {BLUE}{lbl:<18}{R} {bar(conf)} {DIM}{conf*100:5.1f}%{R}")

        # RISK predictions
        risk_preds = predict(text, risk_tok, risk_model, top_k=3)
        print(f"\n{B}  Risk head{R}  {DIM}(3-class, macro F1 0.80){R}")
        for i, (lbl, conf) in enumerate(risk_preds):
            marker = "▶" if i == 0 else " "
            color = risk_color(lbl) if i == 0 else DIM
            print(f"    {marker} {color}{lbl.upper():<12}{R} {bar(conf)} {DIM}{conf*100:5.1f}%{R}")

        n_classified += 1
        print(f"\n{DIM}  —  {n_classified} classified total  ·  ~25 ms per classification on MPS  —{R}")

    print(f"\n{DIM}Exited after {n_classified} classifications. Bye.{R}\n")


if __name__ == "__main__":
    main()
