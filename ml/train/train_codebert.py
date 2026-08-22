import json
import torch
import wandb
import numpy as np
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer
)
from sklearn.metrics import f1_score, classification_report
from sklearn.model_selection import train_test_split

# ── Config ──
MODEL_NAME = "microsoft/codebert-base"
LABELS = ["critical", "medium", "low"]
LABEL2ID = {l: i for i, l in enumerate(LABELS)}
ID2LABEL = {i: l for i, l in enumerate(LABELS)}

# ── Load dataset ──
print("Loading dataset...")
with open("datasets/bug_dataset.json") as f:
    data = json.load(f)

texts = [d["code"] for d in data]
labels = [LABEL2ID[d["label"]] for d in data]

# ── Split ──
train_texts, temp_texts, train_labels, temp_labels = train_test_split(
    texts, labels, test_size=0.2, random_state=42, stratify=labels
)
val_texts, test_texts, val_labels, test_labels = train_test_split(
    temp_texts, temp_labels, test_size=0.5, random_state=42, stratify=temp_labels
)

print(f"Train: {len(train_texts)} | Val: {len(val_texts)} | Test: {len(test_texts)}")

# ── Tokenizer ──
print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

def tokenize(texts, labels):
    encodings = tokenizer(
        texts,
        truncation=True,
        padding=True,
        max_length=512,
        return_tensors="pt"
    )
    return Dataset.from_dict({
        "input_ids": encodings["input_ids"],
        "attention_mask": encodings["attention_mask"],
        "labels": torch.tensor(labels)
    })

train_dataset = tokenize(train_texts, train_labels)
val_dataset = tokenize(val_texts, val_labels)
test_dataset = tokenize(test_texts, test_labels)

# ── Model ──
print("Loading CodeBERT model...")
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=len(LABELS),
    id2label=ID2LABEL,
    label2id=LABEL2ID
)

# ── Metrics ──
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    f1 = f1_score(labels, predictions, average="weighted")
    return {"f1": f1}

# ── W&B init ──
wandb.init(
    project="codereview-ai",
    name="codebert-finetune",
    config={
        "model": MODEL_NAME,
        "epochs": 3,
        "batch_size": 8,
        "lr": 2e-5
    }
)

from torch.nn import CrossEntropyLoss
import torch

# Calculate class weights to handle imbalance
label_counts = [344, 222, 222]
total = sum(label_counts)
class_weights = torch.tensor([total/c for c in label_counts], dtype=torch.float)
class_weights = class_weights / class_weights.sum()
print(f"Class weights: {class_weights}")

# ── Training args ──
training_args = TrainingArguments(
    output_dir="models/codebert-finetuned",
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    learning_rate=2e-5,
    weight_decay=0.01,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="f1",
    report_to="wandb",
    logging_steps=10,
    fp16=True
)

# ── Trainer ──
# ── Custom Trainer with class weights ──
from transformers import Trainer as HFTrainer

class WeightedTrainer(HFTrainer):
    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.get("labels")
        outputs = model(**inputs)
        logits = outputs.get("logits")
        loss_fct = CrossEntropyLoss(weight=class_weights.to(model.device))
        loss = loss_fct(logits, labels)
        return (loss, outputs) if return_outputs else loss

trainer = WeightedTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    compute_metrics=compute_metrics
)

# ── Train ──
print("Starting training...")
print(f"GPU: {torch.cuda.get_device_name(0)}")
print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB")
trainer.train()

# ── Evaluate on test set ──
print("\nEvaluating on test set...")
predictions = trainer.predict(test_dataset)
preds = np.argmax(predictions.predictions, axis=-1)
print(classification_report(test_labels, preds, target_names=LABELS))

# ── Save model ──
print("Saving model...")
trainer.save_model("models/codebert-finetuned")
tokenizer.save_pretrained("models/codebert-finetuned")
print("Model saved to models/codebert-finetuned")

wandb.finish()
print("DONE. Check W&B dashboard for training curves.")