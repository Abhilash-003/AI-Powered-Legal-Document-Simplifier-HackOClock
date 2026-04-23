"""Merge LoRA adapter from the best risk-head checkpoint into models/lexbert-risk/ root.

Mirrors scripts/finalize_type_model.py — different checkpoint + different labels.
Best checkpoint per val macro F1 is epoch 7 (checkpoint-1120, F1 0.843).
"""
import json
from pathlib import Path

import pandas as pd
import torch
from peft import PeftModel
from transformers import AutoModelForSequenceClassification, AutoTokenizer

BEST_CKPT = Path("models/lexbert-risk/checkpoint-1120")  # epoch 7, macro F1 0.843
OUT = Path("models/lexbert-risk")
BASE_MODEL = "law-ai/InLegalBERT"
HF_CACHE = "models/.hf_cache"

assert BEST_CKPT.exists(), f"{BEST_CKPT} missing"

# 1. Label map — from risk training parquet
df = pd.read_parquet("data/processed/risk_train.parquet")
labels = sorted(df["risk_level"].unique().tolist())  # alphabetical: aggressive, illegal, standard
label2id = {l: i for i, l in enumerate(labels)}
id2label = {i: l for i, l in enumerate(labels)}
print(f"Labels ({len(labels)}): {labels}")

# 2. Load base with correct head size
print("Loading base InLegalBERT...")
base = AutoModelForSequenceClassification.from_pretrained(
    BASE_MODEL,
    cache_dir=HF_CACHE,
    num_labels=len(labels),
    id2label=id2label,
    label2id=label2id,
)

# 3. Apply LoRA adapter
print(f"Loading LoRA adapter from {BEST_CKPT}...")
model = PeftModel.from_pretrained(base, str(BEST_CKPT))

# 4. Merge → plain BertForSequenceClassification
print("Merging adapter...")
merged = model.merge_and_unload()

# 5. Clean OUT root (keep checkpoint dirs for safety)
for f in OUT.iterdir():
    if f.is_file():
        f.unlink()

# 6. Save merged model
merged.save_pretrained(OUT)

# 7. Save tokenizer
tok = AutoTokenizer.from_pretrained(BASE_MODEL, cache_dir=HF_CACHE)
tok.save_pretrained(OUT)

# 8. Save label_map.json (lexbert.py depends on this)
with open(OUT / "label_map.json", "w") as f:
    json.dump({
        "labels": labels,
        "label2id": label2id,
        "id2label": {str(k): v for k, v in id2label.items()}
    }, f, indent=2)
print(f"✓ risk model finalized → {OUT}")

# 9. Load verification
reload = AutoModelForSequenceClassification.from_pretrained(str(OUT))
print(f"  class: {type(reload).__name__}, num_labels: {reload.config.num_labels}")
print(f"  id2label: {reload.config.id2label}")

# 10. Sanity prediction on three clauses (one per risk level)
samples = [
    ("The rent shall be escalated by 5% annually, with written notice served 60 days prior.", "expected: standard"),
    ("The Landlord may, at his sole discretion and without prior notice, increase the rent by any amount at any time.", "expected: aggressive"),
    ("The Tenant hereby waives any right to statutory notice of eviction under Section 106 of the Transfer of Property Act.", "expected: illegal"),
]
reload.eval()
print(f"\n  sanity predictions:")
for txt, note in samples:
    inputs = tok(txt, return_tensors="pt", truncation=True, max_length=384, padding="max_length")
    with torch.no_grad():
        logits = reload(**inputs).logits
    probs = torch.softmax(logits, dim=-1)[0]
    top = probs.argmax().item()
    conf = float(probs.max())
    print(f"    [{note}]")
    print(f"    → {id2label[top]} ({conf:.2f})   {txt[:70]}...")
