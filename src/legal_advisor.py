"""LexBERT Advisor — Indian legal retrieval service.

Claude (the Executor) consults this Advisor via tool-use. The Advisor:
  1. Embeds the query using base InLegalBERT
  2. Cosine-similarity-searches a pre-embedded corpus of 6,400 Indian legal
     reference clauses (our hand-built statute-grounded synthetic corpus)
  3. Returns the top-k most semantically similar references, each tagged with
     its Indian statute + section + risk level + doc type

This is the legitimate Advisor-Executor round-trip: Claude asks LexBERT for
Indian legal context, LexBERT retrieves grounded evidence, Claude cites what
LexBERT found — not what Claude remembers.
"""
import json
from functools import lru_cache
from pathlib import Path

import numpy as np

from . import embedder

CORPUS_DIR = Path("data/synthetic")
INDEX_PATH = Path("data/processed/legal_advisor_index.npz")


@lru_cache(maxsize=1)
def _load_index():
    """Load cached index, or build it from the synth corpus on first call."""
    if INDEX_PATH.exists():
        with np.load(INDEX_PATH, allow_pickle=True) as z:
            return z["texts"].tolist(), z["meta"].tolist(), z["embeddings"]

    # Build from scratch
    rows = []
    for f in sorted(CORPUS_DIR.glob("*.jsonl")):
        with open(f) as fh:
            for line in fh:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    texts = [r["clause_text"] for r in rows]
    meta = [
        {
            "clause_type": r.get("clause_type", ""),
            "risk_level": r.get("risk_level", ""),
            "indian_law": r.get("indian_law", ""),
            "doc_type": r.get("doc_type", ""),
        }
        for r in rows
    ]

    print(f"[legal_advisor] building index over {len(texts)} Indian reference clauses...")
    emb = embedder.embed_texts(texts, batch_size=32)

    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(INDEX_PATH, texts=np.array(texts, dtype=object),
                        meta=np.array(meta, dtype=object), embeddings=emb.astype(np.float32))
    print(f"[legal_advisor] index saved → {INDEX_PATH} ({emb.shape[0]} × {emb.shape[1]})")
    return texts, meta, emb


def consult(query: str, k: int = 3) -> list[dict]:
    """Retrieve top-k Indian legal references most semantically similar to `query`.

    Returns a list of dicts (length k), each with:
      - similarity: float in [-1, 1] (cosine)
      - text: verbatim clause text from the reference corpus
      - clause_type, risk_level, indian_law, doc_type
    """
    texts, meta, index_emb = _load_index()
    q_emb = embedder.embed_one(query)  # already L2-normalized
    # index_emb also L2-normalized from embedder.embed_texts → cosine = dot product
    with np.errstate(all="ignore"):  # suppress cosmetic matmul fp warnings
        sims = index_emb @ q_emb
    top_idx = np.argsort(-sims)[:k]
    return [
        {
            "similarity": round(float(sims[i]), 3),
            "text": texts[i],
            "clause_type": meta[i]["clause_type"],
            "risk_level": meta[i]["risk_level"],
            "indian_law": meta[i]["indian_law"],
            "doc_type": meta[i]["doc_type"],
        }
        for i in top_idx
    ]


def format_for_claude(refs: list[dict]) -> str:
    """Render a list of consultation results as plain text for Claude to read."""
    lines = []
    for i, r in enumerate(refs, 1):
        lines.append(
            f"[Reference {i}]  similarity={r['similarity']:.2f}  "
            f"type={r['clause_type']}  risk={r['risk_level']}\n"
            f"  statute: {r['indian_law']}\n"
            f"  text: {r['text']}"
        )
    return "\n\n".join(lines)
