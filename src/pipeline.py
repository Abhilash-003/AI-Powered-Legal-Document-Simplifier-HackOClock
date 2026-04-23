"""Orchestrate the full upload-flow pipeline.

Stages (see design doc):
  1. parse      — PDF/text → ParsedDoc
  2. segment    — Claude → list[Clause]
  3. classify   — LexBERT → {clause_type, risk_level_ml, confidences}
  4. embed      — InLegalBERT base → 768-dim per clause
  5. score      — cosine-sim + composite → final_risk, percentile
  6. law lookup — dict → statute + section + flag
  7. render     — pymupdf + overlays → list[PIL.Image]
  8. analyze    — N parallel Claude calls → plain_english + negotiation + jurisdiction
  9. summarize  — 1 Claude call → doc-level summary

Returns a state dict the Streamlit app stores in st.session_state.
"""
import asyncio
from typing import Optional

from . import claude_analyzer, embedder, lexbert, parser, pdf_renderer, scorer, segmenter, summarizer


def _build_highlight(clause_id: int, page_num: int, bbox: tuple, final_risk: str):
    return pdf_renderer.ClauseHighlight(clause_id=clause_id, page_num=page_num, bbox=bbox, final_risk=final_risk)


async def _run_analyzer(clauses_with_context: list[dict]) -> list:
    return await claude_analyzer.analyze_all(clauses_with_context)


def analyze(pdf_bytes: Optional[bytes] = None, text: Optional[str] = None) -> dict:
    """Run the full pipeline. Exactly one of pdf_bytes or text must be non-None."""
    assert (pdf_bytes is None) ^ (text is None), "Provide exactly one of pdf_bytes or text"

    # Stage 1: parse
    doc = parser.parse(pdf_bytes if pdf_bytes is not None else text)

    # Stage 2: segment (1 Claude call)
    raw_clauses = segmenter.segment(doc.full_text)
    if not raw_clauses:
        return {"error": "No clauses extracted — try text paste instead.", "doc": doc}

    # Stage 3: classify (LexBERT)
    texts = [c.text for c in raw_clauses]
    predictions = lexbert.classify_batch(texts)

    # Stage 4: embed (shared InLegalBERT base)
    embeddings = embedder.embed_texts(texts)

    # Stage 5: score (ML risk + similarity → final_risk) per clause
    # (Statute citation now happens inside claude_analyzer — no separate law_engine step)
    clauses: list[dict] = []
    highlights: list = []
    for clause, pred, emb in zip(raw_clauses, predictions, embeddings):
        sc = scorer.score(emb, pred.clause_type, pred.risk_level_ml, pred.risk_confidence)
        bbox_pairs = parser.bboxes_for_char_range(doc, clause.char_start, clause.char_end)
        clauses.append({
            "clause_id": clause.id,
            "text": clause.text,
            "char_start": clause.char_start,
            "char_end": clause.char_end,
            "page_bboxes": bbox_pairs,  # list of (page_num, bbox)
            "clause_type": pred.clause_type,
            "type_confidence": pred.type_confidence,
            "risk_level_ml": pred.risk_level_ml,
            "risk_confidence": pred.risk_confidence,
            "similarity": sc["similarity"],
            "percentile": sc["percentile"],
            "final_risk": sc["final_risk"],
            "embedding": emb,
            # statute/section/flag filled by Claude analyzer below
        })
        # Only create highlights for risky clauses (Medium/High) — keep Low subtle/skipped
        for page_num, bbox in bbox_pairs:
            highlights.append(_build_highlight(clause.id, page_num, bbox, sc["final_risk"]))

    # Stage 7: render PDF with overlays (PDF input only)
    page_images = pdf_renderer.render_pages(pdf_bytes, highlights) if pdf_bytes else []

    # Stage 8: analyze (N parallel Claude calls — Executor, also produces statute citation)
    analyzer_input = [
        {
            "clause_text": c["text"],
            "clause_type": c["clause_type"],
            "risk_level": c["risk_level_ml"],
        }
        for c in clauses
    ]
    analyses = asyncio.run(_run_analyzer(analyzer_input))
    for c, a in zip(clauses, analyses):
        c["statute"] = a.statute
        c["section"] = a.section
        c["flag"] = a.flag
        c["plain_english"] = a.plain_english
        c["negotiation_script"] = a.negotiation_script
        c["jurisdiction_flag"] = a.jurisdiction_flag

    # Stage 9: document-level summary
    try:
        summary = summarizer.summarize([
            {"clause_id": c["clause_id"], "clause_type": c["clause_type"], "final_risk": c["final_risk"],
             "statute": c["statute"], "text": c["text"]}
            for c in clauses
        ])
    except Exception as e:
        summary = summarizer.DocSummary(
            doc_type="Contract", risk_posture="medium", top_concerns=[],
            summary_line=f"(summary unavailable: {e})",
        )

    risk_counts = {
        "high": sum(1 for c in clauses if c["final_risk"] == "High"),
        "medium": sum(1 for c in clauses if c["final_risk"] == "Medium"),
        "low": sum(1 for c in clauses if c["final_risk"] == "Low"),
    }

    return {
        "clauses": clauses,
        "page_images": page_images,
        "summary": summary,
        "risk_counts": risk_counts,
        "source": doc.source,
    }
