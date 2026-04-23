"""Fine-tuned LexBERT wrapper — type head + risk head inference.

Loads:
  models/lexbert-type/  (LoRA-adapted InLegalBERT, 10-class clause_type head)
  models/lexbert-risk/  (LoRA-adapted InLegalBERT, 3-class risk_level head)

Exposes classify_batch() which returns, per clause:
  clause_type, type_confidence, risk_level_ml, risk_confidence
"""
import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

DEVICE = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
TYPE_DIR = Path("models/lexbert-type")
RISK_DIR = Path("models/lexbert-risk")
MAX_LEN = 384


@dataclass
class Prediction:
    clause_type: str
    type_confidence: float
    risk_level_ml: str
    risk_confidence: float


@lru_cache(maxsize=1)
def _load_type():
    if not TYPE_DIR.exists():
        raise FileNotFoundError(
            f"{TYPE_DIR} not found — train the type head first via scripts/train_lexbert.py --head type"
        )
    tok = AutoTokenizer.from_pretrained(TYPE_DIR)
    model = AutoModelForSequenceClassification.from_pretrained(TYPE_DIR).to(DEVICE).eval()
    id2label = {int(k): v for k, v in json.load(open(TYPE_DIR / "label_map.json"))["id2label"].items()}
    return tok, model, id2label


@lru_cache(maxsize=1)
def _load_risk():
    if not RISK_DIR.exists():
        raise FileNotFoundError(
            f"{RISK_DIR} not found — train the risk head first via scripts/train_lexbert.py --head risk"
        )
    tok = AutoTokenizer.from_pretrained(RISK_DIR)
    model = AutoModelForSequenceClassification.from_pretrained(RISK_DIR).to(DEVICE).eval()
    id2label = {int(k): v for k, v in json.load(open(RISK_DIR / "label_map.json"))["id2label"].items()}
    return tok, model, id2label


def _predict(texts: list[str], tok, model, id2label: dict, batch_size: int = 16):
    preds: list[tuple[str, float]] = []
    with torch.no_grad():
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            enc = tok(batch, truncation=True, max_length=MAX_LEN, padding="longest", return_tensors="pt").to(DEVICE)
            logits = model(**enc).logits
            probs = torch.softmax(logits, dim=-1)
            ids = probs.argmax(dim=-1).cpu().numpy().tolist()
            confs = probs.max(dim=-1).values.cpu().numpy().tolist()
            preds.extend([(id2label[i], float(c)) for i, c in zip(ids, confs)])
    return preds


def classify_batch(clause_texts: list[str]) -> list[Prediction]:
    type_tok, type_model, type_id2label = _load_type()
    risk_tok, risk_model, risk_id2label = _load_risk()
    type_preds = _predict(clause_texts, type_tok, type_model, type_id2label)
    risk_preds = _predict(clause_texts, risk_tok, risk_model, risk_id2label)
    return [
        Prediction(
            clause_type=t[0], type_confidence=t[1], risk_level_ml=r[0], risk_confidence=r[1]
        )
        for t, r in zip(type_preds, risk_preds)
    ]
