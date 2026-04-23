"""Merge LEDGAR (5 covered classes, downsampled) + Indian synthetic (5 Indian-only classes)
into unified training splits for the type classifier and risk classifier.

Outputs:
  data/processed/type_{train,val,test}.parquet   -- 10-class clause type head
  data/processed/risk_{train,val,test}.parquet   -- 3-class risk head (synthetic only)
"""
import json
from pathlib import Path

import pandas as pd

PROCESSED = Path("data/processed")
PROCESSED.mkdir(parents=True, exist_ok=True)

# --- Load LEDGAR + label mapping ---
LABELS = json.load(open("data/raw/ledgar/labels.json"))
label2name = {int(k): v for k, v in LABELS.items()}
MAPPING = json.load(open("data/processed/ledgar_label_mapping.json"))

LEDGAR_PER_CLASS = 500  # cap per split to balance against synthetic

def load_ledgar_split(split):
    df = pd.read_parquet(f"data/raw/ledgar/{split}.parquet")
    df["ledgar_name"] = df["label"].map(label2name)
    df["clause_type"] = df["ledgar_name"].map(MAPPING)
    df = df[df["clause_type"].notna()].copy()
    # downsample per class
    sampled = (
        df.groupby("clause_type", group_keys=False)
        .apply(lambda g: g.sample(min(len(g), LEDGAR_PER_CLASS), random_state=42))
    )
    sampled = sampled[["text", "clause_type"]].rename(columns={"text": "clause_text"})
    sampled["source"] = "ledgar"
    sampled["risk_level"] = None  # LEDGAR has no risk labels
    return sampled.reset_index(drop=True)

ledgar_train = load_ledgar_split("train")
ledgar_val = load_ledgar_split("validation")
ledgar_test = load_ledgar_split("test")

print(f"LEDGAR train: {len(ledgar_train)} | val: {len(ledgar_val)} | test: {len(ledgar_test)}")

# --- Load Indian synthetic ---
synth_rows = []
for fp in sorted(Path("data/synthetic").glob("*.jsonl")):
    with open(fp) as f:
        for line in f:
            synth_rows.append(json.loads(line))
synth_df = pd.DataFrame(synth_rows)[["clause_text", "clause_type", "risk_level", "source"]]
print(f"Synthetic total: {len(synth_df)}")
print("Synthetic per class:"); print(synth_df["clause_type"].value_counts().to_string())

# --- Split synthetic 80/10/10 per class (stratified) ---
from sklearn.model_selection import train_test_split

synth_train_parts = []
synth_val_parts = []
synth_test_parts = []
for ct, g in synth_df.groupby("clause_type"):
    # stratify on risk_level within each class so val/test see all risk levels
    tv, te = train_test_split(g, test_size=0.1, random_state=42, stratify=g["risk_level"])
    tr, vl = train_test_split(tv, test_size=1/9, random_state=42, stratify=tv["risk_level"])
    synth_train_parts.append(tr)
    synth_val_parts.append(vl)
    synth_test_parts.append(te)
synth_train = pd.concat(synth_train_parts).reset_index(drop=True)
synth_val = pd.concat(synth_val_parts).reset_index(drop=True)
synth_test = pd.concat(synth_test_parts).reset_index(drop=True)
print(f"Synthetic train/val/test: {len(synth_train)}/{len(synth_val)}/{len(synth_test)}")

# --- Build TYPE classifier dataset (LEDGAR + synthetic, 10 classes) ---
type_train = pd.concat([ledgar_train, synth_train], ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)
type_val = pd.concat([ledgar_val, synth_val], ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)
type_test = pd.concat([ledgar_test, synth_test], ignore_index=True).sample(frac=1, random_state=42).reset_index(drop=True)

type_train.to_parquet(PROCESSED / "type_train.parquet")
type_val.to_parquet(PROCESSED / "type_val.parquet")
type_test.to_parquet(PROCESSED / "type_test.parquet")
print(f"\n=== TYPE dataset (10 classes) ===")
print(f"train: {len(type_train)} | val: {len(type_val)} | test: {len(type_test)}")
print("train per class:"); print(type_train["clause_type"].value_counts().to_string())

# --- Build RISK classifier dataset (synthetic only, 3 classes) ---
risk_train = synth_train[["clause_text", "clause_type", "risk_level"]].copy()
risk_val = synth_val[["clause_text", "clause_type", "risk_level"]].copy()
risk_test = synth_test[["clause_text", "clause_type", "risk_level"]].copy()
risk_train.to_parquet(PROCESSED / "risk_train.parquet")
risk_val.to_parquet(PROCESSED / "risk_val.parquet")
risk_test.to_parquet(PROCESSED / "risk_test.parquet")
print(f"\n=== RISK dataset (3 classes, synthetic only) ===")
print(f"train: {len(risk_train)} | val: {len(risk_val)} | test: {len(risk_test)}")
print("train risk dist:"); print(risk_train["risk_level"].value_counts().to_string())
