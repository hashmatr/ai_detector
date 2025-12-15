"""
Lightweight TF-IDF + Logistic Regression with n-grams
This is faster than transformers but more accurate than simple statistics
"""
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import joblib

print("="*60)
print("Training TF-IDF + Logistic Regression Model")
print("="*60)

# -------------------------
# Load and prepare data
# -------------------------
base_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_dir, "../../data.csv/processed_data.csv")

print("\nLoading data...")
SAMPLES_PER_CLASS = 10000  # Reduced to avoid memory issues

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
    
    print(f"  Progress: Human={human_count}/{SAMPLES_PER_CLASS}, AI={ai_count}/{SAMPLES_PER_CLASS}")

df_human = pd.concat(human_samples) if human_samples else pd.DataFrame()
df_ai = pd.concat(ai_samples) if ai_samples else pd.DataFrame()
df = pd.concat([df_human, df_ai]).sample(frac=1, random_state=42).reset_index(drop=True)

print(f"\n✅ Loaded {len(df)} samples (Human: {len(df_human)}, AI: {len(df_ai)})")

# Split data
texts = df['text'].values
labels = df['label'].values

X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.2, random_state=42, stratify=labels
)

print(f"Train: {len(X_train)}, Test: {len(X_test)}")

# -------------------------
# Feature extraction with TF-IDF
# -------------------------
print("\nExtracting TF-IDF features...")
print("Using character n-grams (1-4) and word n-grams (1-3)")

vectorizer = TfidfVectorizer(
    max_features=5000,  # Reduced from 10000
    ngram_range=(1, 2),  # Reduced from (1,3)
    analyzer='word',
    min_df=3,
    max_df=0.9,
    sublinear_tf=True
)

# Also add character n-grams for style detection
char_vectorizer = TfidfVectorizer(
    max_features=2000,  # Reduced from 5000
    ngram_range=(2, 3),  # Reduced from (2,4)
    analyzer='char',
    min_df=3,
    max_df=0.9
)

print("  Fitting word vectorizer...")
X_train_word = vectorizer.fit_transform(X_train)
X_test_word = vectorizer.transform(X_test)

print("  Fitting character vectorizer...")
X_train_char = char_vectorizer.fit_transform(X_train)
X_test_char = char_vectorizer.transform(X_test)

# Combine features
from scipy.sparse import hstack
X_train_combined = hstack([X_train_word, X_train_char])
X_test_combined = hstack([X_test_word, X_test_char])

print(f"  Feature matrix shape: {X_train_combined.shape}")

# -------------------------
# Train model
# -------------------------
print("\nTraining Logistic Regression...")
model = LogisticRegression(
    C=1.0,
    max_iter=1000,
    solver='saga',
    random_state=42,
    verbose=1,
    n_jobs=-1
)

model.fit(X_train_combined, y_train)

# -------------------------
# Evaluate
# -------------------------
print("\nEvaluating...")
y_pred = model.predict(X_test_combined)
y_proba = model.predict_proba(X_test_combined)

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print("\n" + "="*60)
print("Model Performance:")
print("="*60)
print(f"Accuracy:  {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1-Score:  {f1:.4f}")
print("="*60)

print("\nDetailed Classification Report:")
print(classification_report(y_test, y_pred, target_names=['Human', 'AI']))

# -------------------------
# Save model
# -------------------------
models_dir = os.path.join(base_dir, "../Models")
os.makedirs(models_dir, exist_ok=True)

model_path = os.path.join(models_dir, "tfidf_model.joblib")
word_vec_path = os.path.join(models_dir, "word_vectorizer.joblib")
char_vec_path = os.path.join(models_dir, "char_vectorizer.joblib")

print(f"\nSaving models...")
joblib.dump(model, model_path)
joblib.dump(vectorizer, word_vec_path)
joblib.dump(char_vectorizer, char_vec_path)

print(f"✅ Model saved to: {model_path}")
print(f"✅ Word vectorizer saved to: {word_vec_path}")
print(f"✅ Char vectorizer saved to: {char_vec_path}")
print("\n" + "="*60)
print("Training Complete!")
print("="*60)
