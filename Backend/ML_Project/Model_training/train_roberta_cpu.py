import os
import pandas as pd
import numpy as np
import torch
from datasets import Dataset
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification, 
    TrainingArguments, 
    Trainer, 
    DataCollatorWithPadding,
    logging as transformers_logging
)
from sklearn.metrics import accuracy_score, f1_score

# 1. Configuration 
MODEL_NAME = "Hello-SimpleAI/chatgpt-detector-roberta"
DATA_PATH = "/kaggle/input/machine-learning-preprocessed-data/processed_data.csv"
MAX_LENGTH = 128 

# 2. Load Data
print("Loading dataset...")
df = pd.read_csv(DATA_PATH).dropna(subset=['cleaned_text', 'source'])
df['label'] = df['source'].apply(lambda x: 0 if str(x).lower() == 'human' else 1)

full_dataset = Dataset.from_pandas(df[['cleaned_text', 'label']])
full_dataset = full_dataset.rename_column("cleaned_text", "text")
dataset_dict = full_dataset.train_test_split(test_size=0.1, seed=42)

# 3. Tokenization
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

def tokenize_function(examples):
    return tokenizer(examples["text"], truncation=True, padding=False, max_length=MAX_LENGTH)

print("Tokenizing dataset...")
tokenized_datasets = dataset_dict.map(tokenize_function, batched=True, remove_columns=["text"])

# 4. Model & Metrics
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    return {"accuracy": accuracy_score(labels, predictions), "f1": f1_score(labels, predictions)}

# 5. Training Arguments (FIXED DEPRECATIONS & ADDED PROGRESS LOGS)
training_args = TrainingArguments(
    output_dir="./roberta_full_dataset",
    # Evaluation and Logging
    eval_strategy="steps",
    eval_steps=500,           # Evaluate every 500 steps to see progress
    logging_strategy="steps", # Ensure logging happens by steps
    logging_steps=50,         # Log loss every 50 steps (shows up every ~2-3 mins)
    save_strategy="steps",
    save_steps=1000,
    save_total_limit=2,
    # Hyperparameters
    learning_rate=2e-5,
    per_device_train_batch_size=32, 
    gradient_accumulation_steps=2, 
    num_train_epochs=1,
    weight_decay=0.01,
    fp16=True,                
    # Visuals
    disable_tqdm=False,       # Ensure progress bar is enabled
    report_to="none",         # Keeps console clean
    run_name="roberta_full_run"
)

# 6. Initialize Trainer (FIXED: replaced 'tokenizer' with 'processing_class')
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["test"],
    processing_class=tokenizer, # This removes the deprecation warning
    data_collator=DataCollatorWithPadding(tokenizer),
    compute_metrics=compute_metrics,
)

# 7. Start Training with clear output
print("\n" + "="*30)
print("TRAINING STARTED")
print("="*30)
trainer.train()

# 8. Save
trainer.save_model("./final_roberta_gold")
print("\nTraining Complete! Model saved to ./final_roberta_gold")