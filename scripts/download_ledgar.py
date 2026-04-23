"""Download LEDGAR (LexGLUE config) and save splits as parquet."""
import json
import os

from datasets import load_dataset

OUT = "data/raw/ledgar"
os.makedirs(OUT, exist_ok=True)

ds = load_dataset("coastalcph/lex_glue", "ledgar")
for split in ds:
    df = ds[split].to_pandas()
    df.to_parquet(f"{OUT}/{split}.parquet")
    print(f"{split}: {len(df)} rows")

labels = ds["train"].features["label"].names
with open(f"{OUT}/labels.json", "w") as f:
    json.dump({i: n for i, n in enumerate(labels)}, f, indent=2)
print(f"{len(labels)} labels saved to {OUT}/labels.json")
