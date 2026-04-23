"""Evaluate fine-tuned LexBERT on the test split + compute baselines.

Runs 3 things:
1. Fine-tuned model on test set → per-class F1 + confusion matrix
2. Baseline A: InLegalBERT zero-shot via [CLS]-embedding nearest-neighbour over train set
3. Baseline B (optional, --with-indian-slice): metrics restricted to Indian-synth test rows only

Outputs:
  docs/eval/{head}_metrics.json
  docs/eval/{head}_confusion_matrix.png
  docs/eval/{head}_report.md
"""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import torch
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
)
from transformers import AutoModel, AutoModelForSequenceClassification, AutoTokenizer

MODEL_NAME = "law-ai/InLegalBERT"
CACHE_DIR = "models/.hf_cache"
DEVICE = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
EVAL_DIR = Path("docs/eval")
EVAL_DIR.mkdir(parents=True, exist_ok=True)


def mean_pool(last_hidden, attention_mask):
    mask = attention_mask.unsqueeze(-1).float()
    summed = (last_hidden * mask).sum(1)
    counted = mask.sum(1).clamp(min=1e-9)
    return summed / counted


def embed_texts(texts, tokenizer, model, batch_size=16):
    model.eval()
    embs = []
    with torch.no_grad():
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            enc = tokenizer(batch, truncation=True, max_length=512, padding=True, return_tensors="pt").to(DEVICE)
            out = model(**enc)
            pooled = mean_pool(out.last_hidden_state, enc["attention_mask"])
            pooled = torch.nn.functional.normalize(pooled, p=2, dim=1)
            embs.append(pooled.cpu().numpy())
    return np.vstack(embs)


def zero_shot_knn_baseline(train_texts, train_labels, test_texts, labels):
    """InLegalBERT zero-shot nearest-neighbour classification."""
    print("[baseline] Loading InLegalBERT for zero-shot embeddings...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR)
    model = AutoModel.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR).to(DEVICE)
    print(f"  embedding {len(train_texts)} train clauses...")
    train_emb = embed_texts(train_texts, tokenizer, model)
    print(f"  embedding {len(test_texts)} test clauses...")
    test_emb = embed_texts(test_texts, tokenizer, model)
    # cosine similarity (already L2-normalized → dot product)
    sims = test_emb @ train_emb.T
    top_idx = sims.argmax(axis=1)
    preds = [train_labels[i] for i in top_idx]
    return preds


def finetuned_predict(test_texts, model_dir):
    print(f"[finetune] Loading {model_dir}...")
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir).to(DEVICE)
    model.eval()
    preds = []
    with torch.no_grad():
        for i in range(0, len(test_texts), 16):
            batch = test_texts[i:i + 16]
            enc = tokenizer(batch, truncation=True, max_length=512, padding=True, return_tensors="pt").to(DEVICE)
            logits = model(**enc).logits
            pred_ids = logits.argmax(dim=-1).cpu().numpy().tolist()
            preds.extend([model.config.id2label[i] for i in pred_ids])
    return preds


def save_confusion_matrix(y_true, y_pred, labels, path):
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    plt.figure(figsize=(max(8, len(labels)), max(6, len(labels) * 0.7)))
    sns.heatmap(cm, annot=True, fmt="d", xticklabels=labels, yticklabels=labels, cmap="Blues")
    plt.xlabel("Predicted"); plt.ylabel("True")
    plt.title(f"Confusion matrix ({len(y_true)} test samples)")
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()


def write_report(head, finetune_metrics, baseline_metrics, labels, path):
    lines = [f"# {head.capitalize()} classifier — evaluation", ""]
    lines.append("## Headline numbers\n")
    lines.append("| Metric | Fine-tuned InLegalBERT (LoRA) | InLegalBERT zero-shot kNN |")
    lines.append("|---|---|---|")
    lines.append(f"| Macro F1 | **{finetune_metrics['macro_f1']:.4f}** | {baseline_metrics['macro_f1']:.4f} |")
    lines.append(f"| Weighted F1 | **{finetune_metrics['weighted_f1']:.4f}** | {baseline_metrics['weighted_f1']:.4f} |")
    lines.append("")
    lines.append("## Per-class F1 (fine-tuned vs baseline)\n")
    lines.append("| Class | Fine-tuned | Zero-shot | Delta |")
    lines.append("|---|---|---|---|")
    for lbl in labels:
        ft = finetune_metrics["per_class"].get(lbl, 0.0)
        bl = baseline_metrics["per_class"].get(lbl, 0.0)
        delta = ft - bl
        flag = "✅" if delta > 0.02 else ("⚠️" if delta < -0.02 else "≈")
        lines.append(f"| {lbl} | {ft:.3f} | {bl:.3f} | {delta:+.3f} {flag} |")
    lines.append("")
    lines.append(f"![Confusion matrix]({head}_confusion_matrix.png)")
    path.write_text("\n".join(lines))


def metrics_dict(y_true, y_pred, labels):
    macro = f1_score(y_true, y_pred, average="macro", zero_division=0, labels=labels)
    weighted = f1_score(y_true, y_pred, average="weighted", zero_division=0, labels=labels)
    per = f1_score(y_true, y_pred, average=None, zero_division=0, labels=labels)
    return {"macro_f1": float(macro), "weighted_f1": float(weighted),
            "per_class": {lbl: float(f) for lbl, f in zip(labels, per)}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--head", choices=["type", "risk"], required=True)
    parser.add_argument("--model_dir", default=None)
    args = parser.parse_args()

    model_dir = args.model_dir or f"models/lexbert-{args.head}"
    label_col = "clause_type" if args.head == "type" else "risk_level"

    train = pd.read_parquet(f"data/processed/{args.head}_train.parquet").dropna(subset=["clause_text", label_col])
    test = pd.read_parquet(f"data/processed/{args.head}_test.parquet").dropna(subset=["clause_text", label_col])
    labels = sorted(train[label_col].unique().tolist())

    train_texts = train["clause_text"].tolist()
    train_labels = train[label_col].tolist()
    test_texts = test["clause_text"].tolist()
    y_true = test[label_col].tolist()

    # finetuned
    y_ft = finetuned_predict(test_texts, model_dir)
    ft_m = metrics_dict(y_true, y_ft, labels)
    # baseline
    y_bl = zero_shot_knn_baseline(train_texts, train_labels, test_texts, labels)
    bl_m = metrics_dict(y_true, y_bl, labels)

    # Save outputs
    with open(EVAL_DIR / f"{args.head}_metrics.json", "w") as f:
        json.dump({"finetuned": ft_m, "baseline_zeroshot_knn": bl_m}, f, indent=2)
    save_confusion_matrix(y_true, y_ft, labels, EVAL_DIR / f"{args.head}_confusion_matrix.png")
    write_report(args.head, ft_m, bl_m, labels, EVAL_DIR / f"{args.head}_report.md")
    print(f"\n=== {args.head} head ===")
    print(f"Fine-tuned macro-F1: {ft_m['macro_f1']:.4f} | Zero-shot kNN: {bl_m['macro_f1']:.4f}")
    print(classification_report(y_true, y_ft, labels=labels, zero_division=0))


if __name__ == "__main__":
    main()
