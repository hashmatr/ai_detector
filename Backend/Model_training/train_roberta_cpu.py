"""
RoBERTa Fine-Tuning Script - Fast CPU Version
Trains on 10,000 samples using CPU
Estimated time: 2-4 hours
"""

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import RobertaTokenizer, RobertaForSequenceClassification, get_linear_schedule_with_warmup
from torch.optim import AdamW
from tqdm import tqdm
import warnings
import time
import gc
import json

warnings.filterwarnings('ignore')

# =========================================
# CONFIGURATION - FAST CPU VERSION
# =========================================
MAX_LENGTH = 128          # Very short for speed
BATCH_SIZE = 8            # Reasonable for CPU
EPOCHS = 3                # 3 epochs
LEARNING_RATE = 2e-5
SAMPLES_PER_CLASS = 5000  # 5k per class = 10k total
MODEL_NAME = "Hello-SimpleAI/chatgpt-detector-roberta"

# Force CPU
device = torch.device('cpu')
print("=" * 60)
print("🚀 RoBERTa Fine-Tuning - Fast CPU Version")
print("=" * 60)
print(f"🔧 Device: {device}")
print(f"📊 Samples: {SAMPLES_PER_CLASS * 2:,} total ({SAMPLES_PER_CLASS:,} per class)")
print(f"⏱️  Estimated time: 2-4 hours")
print("=" * 60)

# =========================================
# LOAD DATA
# =========================================
base_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_dir, "../../data.csv/processed_data.csv")

print(f"\n📚 Loading data...")

human_samples = []
ai_samples = []
human_count = 0
ai_count = 0

chunk_size = 20000
start_time = time.time()

try:
    for i, chunk in enumerate(pd.read_csv(data_path, chunksize=chunk_size)):
        if 'label' not in chunk.columns:
            if 'source' in chunk.columns:
                chunk['label'] = chunk['source'].apply(lambda s: 0 if str(s).lower() == 'human' else 1)
            else:
                continue
        
        text_col = 'cleaned_text' if 'cleaned_text' in chunk.columns else 'text'
        
        # Human samples
        if human_count < SAMPLES_PER_CLASS:
            h = chunk[chunk['label'] == 0]
            if len(h) > 0:
                take_h = min(len(h), SAMPLES_PER_CLASS - human_count)
                chunk_subset = h.iloc[:take_h][[text_col, 'label']].copy()
                chunk_subset.columns = ['text', 'label']
                chunk_subset['text'] = chunk_subset['text'].astype(str).str.slice(0, 1000)
                human_samples.append(chunk_subset)
                human_count += take_h
        
        # AI samples  
        if ai_count < SAMPLES_PER_CLASS:
            a = chunk[chunk['label'] == 1]
            if len(a) > 0:
                take_a = min(len(a), SAMPLES_PER_CLASS - ai_count)
                chunk_subset = a.iloc[:take_a][[text_col, 'label']].copy()
                chunk_subset.columns = ['text', 'label']
                chunk_subset['text'] = chunk_subset['text'].astype(str).str.slice(0, 1000)
                ai_samples.append(chunk_subset)
                ai_count += take_a
        
        print(f"   Progress: Human={human_count:,}, AI={ai_count:,}")
        
        if human_count >= SAMPLES_PER_CLASS and ai_count >= SAMPLES_PER_CLASS:
            break
            
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

if not human_samples or not ai_samples:
    print("❌ Could not load data")
    exit(1)

df_human = pd.concat(human_samples)
df_ai = pd.concat(ai_samples)
df = pd.concat([df_human, df_ai]).sample(frac=1, random_state=42).reset_index(drop=True)

del human_samples, ai_samples, df_human, df_ai
gc.collect()

print(f"\n✅ Loaded {len(df):,} samples in {time.time()-start_time:.1f}s")

# =========================================
# PREPARE DATA
# =========================================
texts = df['text'].values.astype(str)
labels = df['label'].values.astype(int)

X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.1, random_state=42, stratify=labels
)

print(f"   Train: {len(X_train):,}, Test: {len(X_test):,}")

del df, texts, labels
gc.collect()

# =========================================
# DATASET
# =========================================
class TextDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        encoding = self.tokenizer(
            str(self.texts[idx]),
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'label': torch.tensor(self.labels[idx], dtype=torch.long)
        }

# =========================================
# LOAD MODEL
# =========================================
print(f"\n🤖 Loading model...")

try:
    tokenizer = RobertaTokenizer.from_pretrained(MODEL_NAME)
    model = RobertaForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=2)
    print(f"   ✅ Loaded {MODEL_NAME}")
except Exception as e:
    print(f"   ⚠️ Fallback to roberta-base")
    tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
    model = RobertaForSequenceClassification.from_pretrained('roberta-base', num_labels=2)

model = model.to(device)

# =========================================
# DATA LOADERS
# =========================================
train_dataset = TextDataset(X_train, y_train, tokenizer, MAX_LENGTH)
test_dataset = TextDataset(X_test, y_test, tokenizer, MAX_LENGTH)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE * 2)

print(f"   Batches: {len(train_loader):,} train, {len(test_loader):,} test")

# =========================================
# OPTIMIZER
# =========================================
optimizer = AdamW(model.parameters(), lr=LEARNING_RATE)
total_steps = len(train_loader) * EPOCHS
scheduler = get_linear_schedule_with_warmup(
    optimizer,
    num_warmup_steps=int(total_steps * 0.1),
    num_training_steps=total_steps
)

best_f1 = 0
best_model_state = None
history = {'train_loss': [], 'train_acc': [], 'val_acc': [], 'val_f1': []}

# =========================================
# TRAINING
# =========================================
print("\n" + "=" * 60)
print("🚀 TRAINING STARTED")
print("=" * 60)

training_start = time.time()

for epoch in range(EPOCHS):
    epoch_start = time.time()
    print(f"\n📍 EPOCH {epoch + 1}/{EPOCHS}")
    
    # Train
    model.train()
    train_loss = 0
    train_correct = 0
    train_total = 0
    
    pbar = tqdm(train_loader, desc="Training", ncols=80)
    for batch in pbar:
        optimizer.zero_grad()
        
        outputs = model(
            input_ids=batch['input_ids'].to(device),
            attention_mask=batch['attention_mask'].to(device),
            labels=batch['label'].to(device)
        )
        
        loss = outputs.loss
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()
        
        train_loss += loss.item()
        preds = torch.argmax(outputs.logits, dim=1)
        train_correct += (preds == batch['label'].to(device)).sum().item()
        train_total += batch['label'].size(0)
        
        pbar.set_postfix({'loss': f'{loss.item():.3f}', 'acc': f'{train_correct/train_total:.3f}'})
    
    avg_loss = train_loss / len(train_loader)
    train_acc = train_correct / train_total
    history['train_loss'].append(avg_loss)
    history['train_acc'].append(train_acc)
    
    print(f"   Train: Loss={avg_loss:.4f}, Acc={train_acc:.4f}")
    
    # Evaluate
    model.eval()
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for batch in tqdm(test_loader, desc="Evaluating", ncols=80):
            outputs = model(
                input_ids=batch['input_ids'].to(device),
                attention_mask=batch['attention_mask'].to(device)
            )
            preds = torch.argmax(outputs.logits, dim=1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(batch['label'].numpy())
    
    acc = accuracy_score(all_labels, all_preds)
    f1 = f1_score(all_labels, all_preds, average='weighted')
    history['val_acc'].append(acc)
    history['val_f1'].append(f1)
    
    epoch_time = time.time() - epoch_start
    print(f"   Valid: Acc={acc:.4f}, F1={f1:.4f}")
    print(f"   ⏱️ Time: {epoch_time/60:.1f} min")
    
    if f1 > best_f1:
        best_f1 = f1
        best_model_state = model.state_dict().copy()
        print(f"   ⭐ Best model! F1={best_f1:.4f}")

total_time = time.time() - training_start

if best_model_state:
    model.load_state_dict(best_model_state)

# =========================================
# FINAL REPORT
# =========================================
print("\n" + "=" * 60)
print("📋 FINAL RESULTS")
print("=" * 60)
print(classification_report(all_labels, all_preds, target_names=['Human', 'AI']))

# =========================================
# SAVE MODEL
# =========================================
models_dir = os.path.join(base_dir, "../Models")
os.makedirs(models_dir, exist_ok=True)

model_path = os.path.join(models_dir, "roberta_finetuned")
tokenizer_path = os.path.join(models_dir, "roberta_finetuned_tokenizer")

print(f"\n💾 Saving model...")
model.save_pretrained(model_path)
tokenizer.save_pretrained(tokenizer_path)

# Save training info
with open(os.path.join(models_dir, 'training_info.json'), 'w') as f:
    json.dump({
        'config': {'samples': SAMPLES_PER_CLASS * 2, 'epochs': EPOCHS, 'batch_size': BATCH_SIZE},
        'final_metrics': {'accuracy': float(acc), 'f1_score': float(f1), 'best_f1': float(best_f1)},
        'training_time_minutes': total_time / 60,
        'history': {k: [float(v) for v in vals] for k, vals in history.items()}
    }, f, indent=2)

print("\n" + "=" * 60)
print("🎉 TRAINING COMPLETE!")
print("=" * 60)
print(f"   📊 Best F1: {best_f1:.4f} ({best_f1*100:.1f}%)")
print(f"   ⏱️ Time: {total_time/60:.1f} minutes")
print(f"   💾 Saved to: {model_path}")
print("=" * 60)
print("\n✅ Restart your Flask backend to use the fine-tuned model!")
