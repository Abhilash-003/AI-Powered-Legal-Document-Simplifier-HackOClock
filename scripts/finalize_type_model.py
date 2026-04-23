"""Merge LoRA adapter from the best checkpoint into a single plain model in models/lexbert-type/.

Training was stopped mid-schedule, so trainer.save_model() didn't run. We take the
best epoch's LoRA checkpoint and merge it into the InLegalBERT base, producing a
plain BertForSequenceClassification that loads without PEFT at inference time.
"""
import json
import shutil
from pathlib import Path

import pandas as pd
import torch
from peft import PeftModel
from transformers import AutoModelForSequenceClassification, AutoTokenizer

BEST_CKPT = Path("models/lexbert-type/checkpoint-952")  # epoch 4, macro F1 0.909
OUT = Path("models/lexbert-type")
BASE_MODEL = "law-ai/InLegalBERT"
HF_CACHE = "models/.hf_cache"

assert BEST_CKPT.exists(), f"{BEST_CKPT} missing"

# 1. Label map (need num_labels to load base model correctly)
df = pd.read_parquet("data/processed/type_train.parquet")
labels = sorted(df["clause_type"].unique().tolist())
label2id = {l: i for i, l in enumerate(labels)}
id2label = {i: l for i, l in enumerate(labels)}
print(f"Labels ({len(labels)}): {labels}")

# 2. Load base model with correct head size
print("Loading base InLegalBERT...")
base = AutoModelForSequenceClassification.from_pretrained(
    BASE_MODEL,
    cache_dir=HF_CACHE,
    num_labels=len(labels),
    id2label=id2label,
    label2id=label2id,
)

# 3. Apply LoRA adapter from best checkpoint
print(f"Loading LoRA adapter from {BEST_CKPT}...")
model = PeftModel.from_pretrained(base, str(BEST_CKPT))

# 4. Merge adapter into base weights → plain BertForSequenceClassification
print("Merging adapter into base weights...")
merged = model.merge_and_unload()

# 5. Clean destination — remove old adapter/config files, keep checkpoints for now
for f in OUT.iterdir():
    if f.is_file():
        f.unlink()

# 6. Save the merged model
merged.save_pretrained(OUT)
print(f"✓ merged model saved to {OUT}")

# 7. Save tokenizer (uses base model tokenizer)
tok = AutoTokenizer.from_pretrained(BASE_MODEL, cache_dir=HF_CACHE)
tok.save_pretrained(OUT)

# 8. Save label_map.json for lexbert.py
with open(OUT / "label_map.json", "w") as f:
    json.dump({
        "labels": labels,
        "label2id": label2id,
        "id2label": {str(k): v for k, v in id2label.items()}
    }, f, indent=2)
print(f"✓ label_map saved")

# 9. Verification: load it back using the same API as lexbert.py
print("\n--- Load verification ---")
reload = AutoModelForSequenceClassification.from_pretrained(str(OUT))
print(f"  model class: {type(reload).__name__}")
print(f"  num labels:  {reload.config.num_labels}")
print(f"  id2label:    {reload.config.id2label}")

# 10. Run a quick sanity prediction
test_text = "The Employee shall not, for a period of 24 months after termination, engage in any competing business anywhere in India."
inputs = tok(test_text, return_tensors="pt", truncation=True, max_length=384, padding="max_length")
reload.eval()
with torch.no_grad():
    logits = reload(**inputs).logits
probs = torch.softmax(logits, dim=-1)[0]
top = torch.topk(probs, 3)
print(f"\n  test clause: {test_text[:80]}...")
print(f"  top predictions:")
for p, i in zip(top.values, top.indices):
    print(f"    {id2label[int(i)]:18} {float(p):.3f}")

print("\n✓ models/lexbert-type/ ready for inference")
