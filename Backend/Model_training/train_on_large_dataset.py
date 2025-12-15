"""
Train on large dataset (100k-1M+ samples)
Uses incremental learning and sampling for efficiency
"""
import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier  # Supports partial_fit for large data
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import numpy as np

print("="*80)
print("TRAINING ON LARGE DATASET")
print("="*80)

# Load dataset
base_dir = os.path.dirname(__file__)
data_path = os.path.join(base_dir, "../../data.csv/large_ai_dataset.csv")

if not os.path.exists(data_path):
    print(f"\n❌ Large dataset not found at: {data_path}")
    print("\nPlease run first:")
    print("python download_large_dataset.py")
    exit(1)

print(f"\nLoading dataset info...")
# Get total rows without loading all data
df_sample = pd.read_csv(data_path, nrows=1000)
print(f"Sample loaded. Columns: {df_sample.columns.tolist()}")

# Count total rows
total_rows = sum(1 for _ in open(data_path)) - 1  # -1 for header
print(f"Total rows in dataset: {total_rows:,}")

# Decide on sample size
if total_rows > 500000:
    SAMPLE_SIZE = 100000  # Reduced from 200k for memory
    print(f"\n⚠️  Dataset is very large ({total_rows:,} rows)")
    print(f"Using {SAMPLE_SIZE:,} samples for faster training")
elif total_rows > 100000:
    SAMPLE_SIZE = 50000  # Reduced
    print(f"\nUsing {SAMPLE_SIZE:,} samples")
else:
    SAMPLE_SIZE = total_rows
    print(f"\nUsing all {SAMPLE_SIZE:,} samples")

# Load data in chunks and sample
print(f"\nLoading {SAMPLE_SIZE:,} balanced samples...")

chunk_size = 50000
human_samples = []
ai_samples = []
human_count = 0
ai_count = 0
target_per_class = SAMPLE_SIZE // 2

for chunk in pd.read_csv(data_path, chunksize=chunk_size):
    # Sample from this chunk
    chunk_human = chunk[chunk['label'] == 0]
    chunk_ai = chunk[chunk['label'] == 1]
    
    if human_count < target_per_class and len(chunk_human) > 0:
        needed = min(len(chunk_human), target_per_class - human_count)
        human_samples.append(chunk_human.sample(n=needed, random_state=42))
        human_count += needed
    
    if ai_count < target_per_class and len(chunk_ai) > 0:
        needed = min(len(chunk_ai), target_per_class - ai_count)
        ai_samples.append(chunk_ai.sample(n=needed, random_state=42))
        ai_count += needed
    
    print(f"  Progress: Human={human_count:,}/{target_per_class:,}, AI={ai_count:,}/{target_per_class:,}")
    
    if human_count >= target_per_class and ai_count >= target_per_class:
        break

df = pd.concat(human_samples + ai_samples).sample(frac=1, random_state=42).reset_index(drop=True)

print(f"\n✅ Loaded {len(df):,} samples")
print(f"   Human: {sum(df['label']==0):,}")
print(f"   AI: {sum(df['label']==1):,}")

# Split
texts = df['text'].values
labels = df['label'].values

X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.15, random_state=42, stratify=labels
)

print(f"\nTrain: {len(X_train):,} | Test: {len(X_test):,}")

# Feature extraction
print("\n" + "="*80)
print("FEATURE EXTRACTION")
print("="*80)

print("Extracting TF-IDF features (this may take a few minutes)...")
vectorizer = TfidfVectorizer(
    max_features=3000,  # Reduced from 5000 for memory
    ngram_range=(1, 2),  # Reduced from (1,3)
    min_df=5,
    max_df=0.8,
    sublinear_tf=True,
    strip_accents='unicode'
)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

print(f"✅ Feature matrix: {X_train_vec.shape}")

# Train model (SGD for large datasets)
print("\n" + "="*80)
print("TRAINING MODEL")
print("="*80)

print("Training SGD Classifier (optimized for large datasets)...")
model = SGDClassifier(
    loss='log_loss',  # Logistic regression
    penalty='l2',
    alpha=0.0001,
    max_iter=1000,
    random_state=42,
    n_jobs=-1,
    verbose=1
)

model.fit(X_train_vec, y_train)

# Evaluate
print("\n" + "="*80)
print("EVALUATION")
print("="*80)

y_pred = model.predict(X_test_vec)
y_proba = model.predict_proba(X_test_vec) if hasattr(model, 'predict_proba') else None

acc = accuracy_score(y_test, y_pred)

print(f"\n✅ Test Accuracy: {acc:.4f} ({acc*100:.2f}%)")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['Human', 'AI']))

cm = confusion_matrix(y_test, y_pred)
print("\nConfusion Matrix:")
print(f"              Predicted")
print(f"            Human    AI")
print(f"Actual Human {cm[0,0]:5d}  {cm[0,1]:5d}")
print(f"       AI    {cm[1,0]:5d}  {cm[1,1]:5d}")

# Test on Gemini sample
print("\n" + "="*80)
print("TESTING ON GEMINI SAMPLE")
print("="*80)

gemini_text = """Expansion (Enlargement): The push to integrate Western Balkan countries, Ukraine, and Moldova is not just a matter of economic inclusion but a profound geopolitical move to consolidate the democratic, liberal space of Europe against authoritarian influence."""

text_vec = vectorizer.transform([gemini_text])
pred = model.predict(text_vec)[0]

if hasattr(model, 'predict_proba'):
    proba = model.predict_proba(text_vec)[0]
    print(f"\nGemini Text Prediction:")
    print(f"  Label: {'AI' if pred == 1 else 'Human'}")
    print(f"  Confidence: Human={proba[0]:.2%}, AI={proba[1]:.2%}")
    
    if proba[1] > 0.75:
        print("  ✅ HIGH CONFIDENCE - Correctly identified as AI!")
    elif proba[1] > 0.6:
        print("  ⚠️  MODERATE CONFIDENCE - Identified as AI")
    else:
        print("  ❌ LOW CONFIDENCE")
else:
    print(f"\nGemini Text Prediction: {'AI' if pred == 1 else 'Human'}")

# Save
print("\n" + "="*80)
print("SAVING MODEL")
print("="*80)

models_dir = os.path.join(base_dir, "../Models")
os.makedirs(models_dir, exist_ok=True)

joblib.dump(model, os.path.join(models_dir, "large_dataset_model.joblib"))
joblib.dump(vectorizer, os.path.join(models_dir, "large_dataset_vectorizer.joblib"))

print("✅ Saved:")
print("   - large_dataset_model.joblib")
print("   - large_dataset_vectorizer.joblib")

print("\n" + "="*80)
print("TRAINING COMPLETE!")
print("="*80)
print(f"\nTrained on {len(df):,} samples from large dataset")
print(f"Test Accuracy: {acc*100:.2f}%")
print("\nTo use this model, update app.py or restart backend.")
print("="*80)
