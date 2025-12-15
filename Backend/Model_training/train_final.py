"""
FINAL SOLUTION: Properly shuffle and sample the dataset, then train
"""
import pandas as pd
import os
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
from scipy.sparse import hstack

print("="*70)
print("AI DETECTOR - FINAL TRAINING WITH PROPER DATA HANDLING")
print("="*70)

base_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_dir, "../../data.csv/processed_data.csv")

# -------------------------
# Step 1: Load and properly sample data
# -------------------------
print("\n[Step 1] Loading and sampling data properly...")

SAMPLE_SIZE = 16000  # 8k per class - reduced for memory
chunk_size = 20000

human_samples = []
ai_samples = []
human_count = 0
ai_count = 0
target_per_class = SAMPLE_SIZE // 2

print(f"Target: {target_per_class} samples per class")

for i, chunk in enumerate(pd.read_csv(data_path, chunksize=chunk_size)):
    if 'label' not in chunk.columns:
        chunk['label'] = chunk['source'].apply(lambda s: 0 if str(s).lower() == 'human' else 1)
    
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
    
    print(f"  Chunk {i+1}: Human={human_count}/{target_per_class}, AI={ai_count}/{target_per_class}")
    
    if human_count >= target_per_class and ai_count >= target_per_class:
        print("  ✅ Reached target for both classes!")
        break

if human_count == 0 or ai_count == 0:
    print("❌ CRITICAL ERROR: Could not find samples for one class!")
    exit(1)

# Combine and shuffle
df_human = pd.concat(human_samples)
df_ai = pd.concat(ai_samples)

print(f"\n✅ Collected: {len(df_human)} Human, {len(df_ai)} AI")

# Combine and shuffle thoroughly
df = pd.concat([df_human, df_ai])
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"Final dataset: {len(df)} samples")
print(f"Label distribution:\n{df['label'].value_counts()}")

# -------------------------
# Step 2: Split data
# -------------------------
print("\n[Step 2] Splitting data...")

texts = df['text'].values
labels = df['label'].values

X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.25, random_state=42, stratify=labels
)

print(f"Train: {len(X_train)} ({sum(y_train==0)} Human, {sum(y_train==1)} AI)")
print(f"Test:  {len(X_test)} ({sum(y_test==0)} Human, {sum(y_test==1)} AI)")

# -------------------------
# Step 3: Feature extraction
# -------------------------
print("\n[Step 3] Extracting features...")

# Word-level TF-IDF
word_vec = TfidfVectorizer(
    max_features=3000,  # Reduced
    ngram_range=(1, 2),
    min_df=5,
    max_df=0.8,
    sublinear_tf=True,
    strip_accents='unicode'
)

# Character-level TF-IDF
char_vec = TfidfVectorizer(
    max_features=1000,  # Reduced
    analyzer='char',
    ngram_range=(2, 3),
    min_df=5,
    max_df=0.8
)

print("  Fitting word vectorizer...")
X_train_word = word_vec.fit_transform(X_train)
X_test_word = word_vec.transform(X_test)

print("  Fitting char vectorizer...")
X_train_char = char_vec.fit_transform(X_train)
X_test_char = char_vec.transform(X_test)

# Combine
X_train_combined = hstack([X_train_word, X_train_char])
X_test_combined = hstack([X_test_word, X_test_char])

print(f"  Feature shape: {X_train_combined.shape}")

# -------------------------
# Step 4: Train model
# -------------------------
print("\n[Step 4] Training Logistic Regression...")

model = LogisticRegression(
    C=0.5,
    max_iter=500,
    solver='saga',
    random_state=42,
    class_weight='balanced',  # Handle any remaining imbalance
    verbose=1,
    n_jobs=-1
)

model.fit(X_train_combined, y_train)

# -------------------------
# Step 5: Evaluate
# -------------------------
print("\n[Step 5] Evaluating...")

y_pred_train = model.predict(X_train_combined)
y_pred_test = model.predict(X_test_combined)

train_acc = accuracy_score(y_train, y_pred_train)
test_acc = accuracy_score(y_test, y_pred_test)

print("\n" + "="*70)
print("RESULTS:")
print("="*70)
print(f"Train Accuracy: {train_acc:.4f}")
print(f"Test Accuracy:  {test_acc:.4f}")
print("\nTest Set Classification Report:")
print(classification_report(y_test, y_pred_test, target_names=['Human', 'AI']))

print("\nConfusion Matrix (Test Set):")
cm = confusion_matrix(y_test, y_pred_test)
print(f"                Predicted")
print(f"              Human    AI")
print(f"Actual Human  {cm[0,0]:5d}  {cm[0,1]:5d}")
print(f"       AI     {cm[1,0]:5d}  {cm[1,1]:5d}")

# -------------------------
# Step 6: Save model
# -------------------------
print("\n[Step 6] Saving model...")

models_dir = os.path.join(base_dir, "../Models")
os.makedirs(models_dir, exist_ok=True)

joblib.dump(model, os.path.join(models_dir, "tfidf_model.joblib"))
joblib.dump(word_vec, os.path.join(models_dir, "word_vectorizer.joblib"))
joblib.dump(char_vec, os.path.join(models_dir, "char_vectorizer.joblib"))

print("✅ Model saved successfully!")
print("\n" + "="*70)
print("TRAINING COMPLETE!")
print("="*70)
