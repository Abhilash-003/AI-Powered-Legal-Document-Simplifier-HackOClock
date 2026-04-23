"""Fine-tune InLegalBERT with LoRA for two heads: clause type (10-class) and risk (3-class).

Usage:
    python scripts/train_lexbert.py --head type
    python scripts/train_lexbert.py --head risk

Safety defaults (from Paul et al. paper + standard practice):
- LoRA rank 8, alpha 16 → ~0.3% of params train (base encoder frozen → no catastrophic forgetting)
- Per-layer LR: head 1e-3, encoder 1e-5
- Dropout 0.2 in head, weight decay 0.01, label smoothing 0.1
- Weighted cross-entropy (inverse-frequency class weights) for imbalance
- Max 8 epochs, early stopping on val macro-F1 (patience 3)
- Saves best checkpoint by val F1 (not last epoch)
"""
import argparse
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from datasets import Dataset
from peft import LoraConfig, TaskType, get_peft_model
from sklearn.metrics import classification_report, f1_score
from sklearn.utils.class_weight import compute_class_weight
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    EarlyStoppingCallback,
    Trainer,
    TrainingArguments,
)

MODEL_NAME = "law-ai/InLegalBERT"
CACHE_DIR = "models/.hf_cache"
DEVICE = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")


def load_data(head: str):
    data_dir = Path("data/processed")
    train = pd.read_parquet(data_dir / f"{head}_train.parquet")
    val = pd.read_parquet(data_dir / f"{head}_val.parquet")
    test = pd.read_parquet(data_dir / f"{head}_test.parquet")
    label_col = "clause_type" if head == "type" else "risk_level"
    for df in (train, val, test):
        df.dropna(subset=["clause_text", label_col], inplace=True)
    return train, val, test, label_col


def build_label_map(train_df, label_col):
    labels = sorted(train_df[label_col].unique().tolist())
    label2id = {l: i for i, l in enumerate(labels)}
    id2label = {i: l for i, l in enumerate(labels)}
    return labels, label2id, id2label


def tokenize_factory(tokenizer, label_col, label2id, max_length=384):
    """Fixed max_length padding → every batch has identical shape → MPS kernel cache hits."""
    def _fn(batch):
        enc = tokenizer(batch["clause_text"], truncation=True, max_length=max_length, padding="max_length")
        enc["labels"] = [label2id[x] for x in batch[label_col]]
        return enc
    return _fn


class WeightedTrainer(Trainer):
    """Trainer with class-weighted cross-entropy + label smoothing."""
    def __init__(self, class_weights, label_smoothing=0.1, **kwargs):
        super().__init__(**kwargs)
        self.class_weights = class_weights
        self.label_smoothing = label_smoothing

    def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits
        weights = self.class_weights.to(logits.device)
        loss_fn = nn.CrossEntropyLoss(weight=weights, label_smoothing=self.label_smoothing)
        loss = loss_fn(logits.view(-1, logits.size(-1)), labels.view(-1))
        return (loss, outputs) if return_outputs else loss


def compute_metrics_factory(id2label):
    def _fn(eval_pred):
        logits, labels = eval_pred
        preds = np.argmax(logits, axis=1)
        macro_f1 = f1_score(labels, preds, average="macro", zero_division=0)
        weighted_f1 = f1_score(labels, preds, average="weighted", zero_division=0)
        per_class = f1_score(labels, preds, average=None, zero_division=0, labels=list(id2label.keys()))
        out = {"macro_f1": macro_f1, "weighted_f1": weighted_f1}
        for i, f1 in enumerate(per_class):
            out[f"f1_{id2label[i]}"] = float(f1)
        return out
    return _fn


def layered_optimizer(model, lr_head: float, lr_encoder: float, weight_decay: float):
    """Per-layer learning rates: higher on classification head, lower on LoRA-adapted encoder."""
    head_params, encoder_params = [], []
    for n, p in model.named_parameters():
        if not p.requires_grad:
            continue
        if "classifier" in n or "score" in n:
            head_params.append(p)
        else:
            encoder_params.append(p)
    return torch.optim.AdamW(
        [
            {"params": head_params, "lr": lr_head, "weight_decay": weight_decay},
            {"params": encoder_params, "lr": lr_encoder, "weight_decay": weight_decay},
        ]
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--head", choices=["type", "risk"], required=True)
    parser.add_argument("--epochs", type=int, default=8)
    parser.add_argument("--batch_size", type=int, default=16)
    parser.add_argument("--output_dir", default=None)
    parser.add_argument("--smoke", action="store_true", help="Run 1 epoch on a tiny slice")
    args = parser.parse_args()

    output_dir = args.output_dir or f"models/lexbert-{args.head}"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    print(f"Device: {DEVICE}")
    print(f"Head: {args.head} | output_dir: {output_dir}")

    train_df, val_df, test_df, label_col = load_data(args.head)
    if args.smoke:
        train_df = train_df.groupby(label_col).head(8).reset_index(drop=True)
        val_df = val_df.groupby(label_col).head(4).reset_index(drop=True)
        args.epochs = 1
        print("SMOKE MODE: 8 train, 4 val per class, 1 epoch")

    labels, label2id, id2label = build_label_map(train_df, label_col)
    print(f"Labels ({len(labels)}): {labels}")
    print(f"Train: {len(train_df)} | Val: {len(val_df)} | Test: {len(test_df)}")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, cache_dir=CACHE_DIR)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        cache_dir=CACHE_DIR,
        num_labels=len(labels),
        id2label=id2label,
        label2id=label2id,
        classifier_dropout=0.2,
    )

    lora_cfg = LoraConfig(
        task_type=TaskType.SEQ_CLS,
        r=8, lora_alpha=16, lora_dropout=0.1,
        target_modules=["query", "value"],
        bias="none",
    )
    model = get_peft_model(model, lora_cfg)
    model.print_trainable_parameters()

    tok_fn = tokenize_factory(tokenizer, label_col, label2id)
    train_ds = Dataset.from_pandas(train_df[["clause_text", label_col]]).map(tok_fn, batched=True, remove_columns=["clause_text", label_col])
    val_ds = Dataset.from_pandas(val_df[["clause_text", label_col]]).map(tok_fn, batched=True, remove_columns=["clause_text", label_col])

    # class weights from train distribution
    train_labels_int = [label2id[x] for x in train_df[label_col]]
    class_weights = compute_class_weight("balanced", classes=np.arange(len(labels)), y=train_labels_int)
    class_weights = torch.tensor(class_weights, dtype=torch.float32)
    print(f"Class weights: {dict(zip(labels, class_weights.tolist()))}")

    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size * 2,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="macro_f1",
        greater_is_better=True,
        logging_steps=20,
        save_total_limit=2,
        report_to="none",
        warmup_ratio=0.1,
        seed=42,
        dataloader_pin_memory=False,  # MPS compat
    )

    collator = DataCollatorWithPadding(tokenizer, padding="longest")

    # custom optimizer with layered LRs (created lazily via callback hook)
    trainer = WeightedTrainer(
        class_weights=class_weights,
        label_smoothing=0.1,
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        tokenizer=tokenizer,
        data_collator=collator,
        compute_metrics=compute_metrics_factory(id2label),
        callbacks=[EarlyStoppingCallback(early_stopping_patience=3)],
    )
    # override optimizer
    trainer.optimizer = layered_optimizer(model, lr_head=1e-3, lr_encoder=1e-5, weight_decay=0.01)

    trainer.train()
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)

    # save label map for downstream inference
    with open(f"{output_dir}/label_map.json", "w") as f:
        json.dump({"labels": labels, "label2id": label2id, "id2label": id2label}, f, indent=2)

    # final eval on VAL (test deferred to eval script)
    metrics = trainer.evaluate(val_ds)
    with open(f"{output_dir}/val_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\nFinal val metrics: macro_f1={metrics['eval_macro_f1']:.4f}, weighted_f1={metrics['eval_weighted_f1']:.4f}")


if __name__ == "__main__":
    main()
