"""Pre-compute reference (standard-clause) embeddings per clause_type for scorer.py.

Standard clauses only → embeddings represent the 'typical' anchor for each type.
At inference time, scorer.py cosine-sims a new clause against these anchors.

Output: data/processed/reference_embeddings.npz  (one array per clause_type)
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import embedder  # noqa: E402

OUT = Path("data/processed/reference_embeddings.npz")
SYNTH_DIR = Path("data/synthetic")


def main():
    frames = []
    for f in sorted(SYNTH_DIR.glob("*.jsonl")):
        df = pd.read_json(f, lines=True)
        frames.append(df)
    all_synth = pd.concat(frames, ignore_index=True)
    standard = all_synth[all_synth["risk_level"] == "standard"].copy()
    print(f"Loaded {len(all_synth)} synth rows; {len(standard)} 'standard' used as anchors.")

    per_type: dict[str, np.ndarray] = {}
    for clause_type, g in standard.groupby("clause_type"):
        texts = g["clause_text"].tolist()
        print(f"  {clause_type}: embedding {len(texts)} anchor clauses...")
        emb = embedder.embed_texts(texts, batch_size=16)
        per_type[clause_type] = emb.astype(np.float32)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(OUT, **per_type)
    print(f"\nSaved {len(per_type)} reference-embedding arrays → {OUT}")
    for k, v in per_type.items():
        print(f"  {k:20} shape={v.shape}")


if __name__ == "__main__":
    main()
