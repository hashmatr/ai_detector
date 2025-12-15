"""
Train a transformer-based AI text detector using DistilBERT
This approach learns contextual patterns rather than surface statistics
"""
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, get_linear_schedule_with_warmup
from torch.optim import AdamW
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# Check for GPU
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# -------------------------
# Configuration
# -------------------------
MAX_LENGTH = 256  # Reduced for memory efficiency
BATCH_SIZE = 8  # Smaller batch size
EPOCHS = 2
LEARNING_RATE = 2e-5
SAMPLES_PER_CLASS = 1500  # Reduced for faster training on CPU

# -------------------------
# Load and prepare data
# -------------------------
base_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_dir, "../../data.csv/processed_data.csv")

print("Loading data...")
print(f"Sampling {SAMPLES_PER_CLASS} samples per class...")

# Read data in chunks and balance
human_samples = []
ai_samples = []
human_count = 0
ai_count = 0

for chunk in pd.read_csv(data_path, chunksize=10000):
    if 'label' not in chunk.columns:
        chunk['label'] = chunk['source'].apply(lambda s: 0 if str(s).lower() == 'human' else 1)
    
    if human_count < SAMPLES_PER_CLASS:
        h = chunk[chunk['label'] == 0].head(SAMPLES_PER_CLASS - human_count)
        if not h.empty:
            human_samples.append(h)
            human_count += len(h)
    
    if ai_count < SAMPLES_PER_CLASS:
        a = chunk[chunk['label'] == 1].head(SAMPLES_PER_CLASS - ai_count)
        if not a.empty:
            ai_samples.append(a)
            ai_count += len(a)
    
    if human_count >= SAMPLES_PER_CLASS and ai_count >= SAMPLES_PER_CLASS:
        break

df_human = pd.concat(human_samples) if human_samples else pd.DataFrame()
df_ai = pd.concat(ai_samples) if ai_samples else pd.DataFrame()
df = pd.concat([df_human, df_ai]).sample(frac=1, random_state=42).reset_index(drop=True)

print(f"Loaded {len(df)} samples (Human: {len(df_human)}, AI: {len(df_ai)})")

# Split data
texts = df['text'].values
labels = df['label'].values

X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.2, random_state=42, stratify=labels
)

print(f"Train: {len(X_train)}, Test: {len(X_test)}")

# -------------------------
# Dataset class
# -------------------------
class TextDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        encoding = self.tokenizer(
            text,
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'label': torch.tensor(label, dtype=torch.long)
        }

# -------------------------
# Initialize model and tokenizer
# -------------------------
print("\nInitializing DistilBERT model...")
tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
model = DistilBertForSequenceClassification.from_pretrained(
    'distilbert-base-uncased',
    num_labels=2
).to(device)

# Create datasets
train_dataset = TextDataset(X_train, y_train, tokenizer, MAX_LENGTH)
test_dataset = TextDataset(X_test, y_test, tokenizer, MAX_LENGTH)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE)

# -------------------------
# Training setup
# -------------------------
optimizer = AdamW(model.parameters(), lr=LEARNING_RATE)
total_steps = len(train_loader) * EPOCHS
scheduler = get_linear_schedule_with_warmup(
    optimizer,
    num_warmup_steps=0,
    num_training_steps=total_steps
)

# -------------------------
# Training loop
# -------------------------
print("\nStarting training...")
for epoch in range(EPOCHS):
    print(f"\n{'='*60}")
    print(f"Epoch {epoch + 1}/{EPOCHS}")
    print(f"{'='*60}")
    
    # Training
    model.train()
    train_loss = 0
    train_correct = 0
    train_total = 0
    
    for batch_idx, batch in enumerate(train_loader):
        try:
            optimizer.zero_grad()
            
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['label'].to(device)
            
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )
            
            loss = outputs.loss
            logits = outputs.logits
            
            loss.backward()
            optimizer.step()
            scheduler.step()
            
            train_loss += loss.item()
            predictions = torch.argmax(logits, dim=1)
            train_correct += (predictions == labels).sum().item()
            train_total += labels.size(0)
            
            if batch_idx % 100 == 0:
                print(f"  Batch {batch_idx}/{len(train_loader)} - Loss: {loss.item():.4f}, Acc: {train_correct/train_total:.4f}")
        except Exception as e:
            print(f"Error in batch {batch_idx}: {e}")
            continue
    
    avg_train_loss = train_loss / len(train_loader)
    train_accuracy = train_correct / train_total
    
    print(f"\nTrain Loss: {avg_train_loss:.4f}, Train Accuracy: {train_accuracy:.4f}")
    
    # Evaluation
    model.eval()
    test_predictions = []
    test_labels = []
    
    with torch.no_grad():
        for batch_idx, batch in enumerate(test_loader):
            if batch_idx % 50 == 0:
                print(f"  Evaluating batch {batch_idx}/{len(test_loader)}")
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['label'].to(device)
            
            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask
            )
            
            predictions = torch.argmax(outputs.logits, dim=1)
            test_predictions.extend(predictions.cpu().numpy())
            test_labels.extend(labels.cpu().numpy())
    
    # Metrics
    accuracy = accuracy_score(test_labels, test_predictions)
    precision = precision_score(test_labels, test_predictions)
    recall = recall_score(test_labels, test_predictions)
    f1 = f1_score(test_labels, test_predictions)
    
    print(f"\nTest Metrics:")
    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1-Score:  {f1:.4f}")

# -------------------------
# Final evaluation
# -------------------------
print("\n" + "="*60)
print("Final Classification Report:")
print("="*60)
print(classification_report(test_labels, test_predictions, 
                          target_names=['Human', 'AI']))

# -------------------------
# Save model
# -------------------------
models_dir = os.path.join(base_dir, "../Models")
os.makedirs(models_dir, exist_ok=True)

model_save_path = os.path.join(models_dir, "distilbert_model")
tokenizer_save_path = os.path.join(models_dir, "distilbert_tokenizer")

print(f"\nSaving model to {model_save_path}...")
model.save_pretrained(model_save_path)
tokenizer.save_pretrained(tokenizer_save_path)

print("\n✅ Training complete!")
print(f"Model saved to: {model_save_path}")
