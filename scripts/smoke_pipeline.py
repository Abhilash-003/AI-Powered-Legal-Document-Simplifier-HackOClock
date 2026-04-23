#!/usr/bin/env python3
"""End-to-end smoke test — runs the full pipeline on a real Indian PDF.

Bypasses Streamlit UI. Directly calls pipeline.analyze() and prints what comes
back. Use this FIRST to debug integration issues before launching the UI.

Exit 0 if everything worked, 1 if anything broke. Prints timing per stage.
"""
# auto-activate venv
import os
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_VENV_DIR = _REPO_ROOT / ".venv"
_VENV_PY = _VENV_DIR / "bin" / "python3"
if _VENV_PY.exists() and not sys.executable.startswith(str(_VENV_DIR)):
    os.execv(str(_VENV_PY), [str(_VENV_PY), *sys.argv])

sys.path.insert(0, str(_REPO_ROOT))  # so `from src import …` works from scripts/
os.chdir(_REPO_ROOT)  # pipeline paths are relative to repo root

import time
import traceback

from src import pipeline

PDF_PATH = Path("data/raw/templates/keyushnisar_legal_docu.pdf")
MAX_CLAUSES_TO_SHOW = 5

R = "\033[0m"
B = "\033[1m"
DIM = "\033[2m"
G = "\033[92m"
RED = "\033[91m"
Y = "\033[93m"
C = "\033[96m"


def header(s):
    print(f"\n{B}{C}── {s} ──{R}")


def ok(s):
    print(f"  {G}✓{R} {s}")


def fail(s):
    print(f"  {RED}✗{R} {s}")


def main():
    header("Phase 1 — check prerequisites")
    if not PDF_PATH.exists():
        fail(f"PDF not found at {PDF_PATH}")
        sys.exit(1)
    size = PDF_PATH.stat().st_size
    ok(f"PDF ready at {PDF_PATH} ({size:,} bytes)")

    if not Path("models/lexbert-type/label_map.json").exists():
        fail("models/lexbert-type/ not finalized — run scripts/finalize_type_model.py")
        sys.exit(1)
    ok("models/lexbert-type/ ready")

    if not Path("models/lexbert-risk/label_map.json").exists():
        fail("models/lexbert-risk/ not finalized — run scripts/finalize_risk_model.py")
        sys.exit(1)
    ok("models/lexbert-risk/ ready")

    if not Path("data/processed/reference_embeddings.npz").exists():
        fail("reference_embeddings.npz missing — run scripts/build_reference_embeddings.py")
        sys.exit(1)
    ok("reference_embeddings.npz present")

    if not os.environ.get("ANTHROPIC_API_KEY", ""):
        fail("ANTHROPIC_API_KEY not in env — make sure .env is populated")
        sys.exit(1)
    ok("ANTHROPIC_API_KEY loaded")

    # Phase 2 — run the pipeline
    header("Phase 2 — run pipeline.analyze() end-to-end")
    t0 = time.time()

    try:
        with open(PDF_PATH, "rb") as f:
            pdf_bytes = f.read()
        result = pipeline.analyze(pdf_bytes=pdf_bytes)
        elapsed = time.time() - t0
        ok(f"pipeline completed in {elapsed:.1f}s")
    except Exception as e:
        elapsed = time.time() - t0
        fail(f"pipeline raised {type(e).__name__} after {elapsed:.1f}s")
        print(f"\n{DIM}{traceback.format_exc()}{R}")
        sys.exit(1)

    # Phase 3 — inspect the result
    header("Phase 3 — inspect the result")

    if "error" in result:
        fail(f"pipeline returned an error: {result['error']}")
        sys.exit(1)

    clauses = result.get("clauses", [])
    page_images = result.get("page_images", [])
    summary = result.get("summary")
    risk_counts = result.get("risk_counts", {})

    ok(f"clauses extracted: {len(clauses)}")
    ok(f"page images rendered: {len(page_images)}")
    ok(f"risk counts: high={risk_counts.get('high',0)} med={risk_counts.get('medium',0)} low={risk_counts.get('low',0)}")
    if summary:
        ok(f"summary produced: doc_type={summary.doc_type!r}, posture={summary.risk_posture!r}")
        print(f"    {DIM}{summary.summary_line[:140]}{R}")

    # Show first N clauses
    print(f"\n{B}First {min(MAX_CLAUSES_TO_SHOW, len(clauses))} clauses:{R}")
    for c in clauses[:MAX_CLAUSES_TO_SHOW]:
        risk_color = {"High": RED, "Medium": Y, "Low": G}.get(c.get("final_risk"), DIM)
        print(f"\n  {B}Clause {c['clause_id']}{R} ({risk_color}{c.get('final_risk','?')}{R}) · type={c['clause_type']} · conf={c.get('type_confidence',0):.2f}")
        print(f"  {DIM}text: {c['text'][:120]}...{R}")
        print(f"  {DIM}statute: {c.get('statute','?')} · {c.get('section','?')}{R}")
        if c.get("plain_english"):
            print(f"  {G}plain_english: {c['plain_english'][:140]}...{R}")
        if c.get("negotiation_script"):
            print(f"  {Y}negotiation: {c['negotiation_script'][:140]}...{R}")

    print(f"\n{G}{B}smoke test PASSED — pipeline works end-to-end{R}\n")


if __name__ == "__main__":
    main()
