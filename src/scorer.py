"""Composite risk scoring: ML risk head + cosine-similarity vs standard-clause anchors.

Given a clause's embedding and predicted clause_type, produces:
  - similarity: mean cosine-sim vs standard-clause anchors for that type
  - percentile: 0-100 "more unusual than X%" framing
  - final_risk: Low | Medium | High (composite of ML risk + similarity)

Relies on data/processed/reference_embeddings.npz produced offline by
scripts/build_reference_embeddings.py (standard-risk synthetic clauses only).
"""
from functools import lru_cache
from pathlib import Path
from typing import Optional

import numpy as np

REF_PATH = Path("data/processed/reference_embeddings.npz")


@lru_cache(maxsize=1)
def _reference():
    if not REF_PATH.exists():
        return {}
    with np.load(REF_PATH, allow_pickle=True) as z:
        # z contains one array per clause_type, named by the type
        return {name: z[name] for name in z.files}


def score(embedding: np.ndarray, clause_type: str, ml_risk: str, ml_conf: float) -> dict:
    """Compute similarity-based percentile and compose final risk with ML head."""
    refs = _reference().get(clause_type)
    if refs is None or len(refs) == 0:
        # no reference — fall back to ML risk alone
        return {
            "similarity": None,
            "percentile": None,
            "final_risk": _ml_to_final(ml_risk),
        }
    # embedding expected L2-normalized; refs same
    sims = refs @ embedding  # dot = cosine when both normalized
    mean_sim = float(np.mean(sims))
    # percentile framing: lower similarity → more unusual → higher percentile
    percentile = int(round((1.0 - mean_sim) * 100))
    percentile = max(0, min(100, percentile))
    return {
        "similarity": mean_sim,
        "percentile": percentile,
        "final_risk": _compose(ml_risk, mean_sim),
    }


def _compose(ml_risk: str, sim: float) -> str:
    """Fuse ML risk head + similarity-to-standard into a displayed risk level."""
    if ml_risk == "illegal":
        return "High"
    if ml_risk == "aggressive":
        return "High" if sim < 0.70 else "Medium"
    # ml_risk == "standard"
    return "Medium" if sim < 0.60 else "Low"


def _ml_to_final(ml_risk: str) -> str:
    return {"illegal": "High", "aggressive": "Medium", "standard": "Low"}.get(ml_risk, "Medium")
