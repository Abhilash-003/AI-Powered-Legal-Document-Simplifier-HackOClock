"""Shared InLegalBERT base embedder (pre-fine-tune [CLS] pooling).

Used by:
  - lexbert.py (embeds clauses at upload time for similarity scoring + RAG)
  - rag.py      (embeds the user's query at chat time)
  - build_reference_embeddings.py (offline pre-compute of standard-clause anchors)

Kept separate from the fine-tuned classifier on purpose: embeddings come from
the ORIGINAL InLegalBERT, so they live in the same semantic space regardless
of our task fine-tuning.
"""
from functools import lru_cache

import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer

MODEL_NAME = "law-ai/InLegalBERT"
CACHE_DIR = "models/.hf_cache"
DEVICE = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
MAX_LEN = 384


@lru_cache(maxsize=1)
def _load():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR)
    model = AutoModel.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR).to(DEVICE).eval()
    return tokenizer, model


def _mean_pool(last_hidden: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
    mask = attention_mask.unsqueeze(-1).float()
    summed = (last_hidden * mask).sum(1)
    counted = mask.sum(1).clamp(min=1e-9)
    return summed / counted


def embed_texts(texts: list[str], batch_size: int = 16) -> np.ndarray:
    tokenizer, model = _load()
    embs: list[np.ndarray] = []
    with torch.no_grad():
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            enc = tokenizer(
                batch, truncation=True, max_length=MAX_LEN, padding="longest", return_tensors="pt"
            ).to(DEVICE)
            out = model(**enc)
            pooled = _mean_pool(out.last_hidden_state, enc["attention_mask"])
            pooled = torch.nn.functional.normalize(pooled, p=2, dim=1)
            embs.append(pooled.cpu().numpy())
    return np.vstack(embs)


def embed_one(text: str) -> np.ndarray:
    return embed_texts([text])[0]
