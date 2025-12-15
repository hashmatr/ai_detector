"""
SIMPLE K-FOLD TRAINING (Manual Implementation)
Works around scipy compatibility issues
"""
import pandas as pd
import numpy as np
import os
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

print("="*80)
print("K-FOLD CROSS VALIDATION TRAINING")
print("="*80)

# Load dataset
base_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_dir, "../../data.csv/large_ai_dataset.csv")

print("\nLoading 50,000 balanced samples...")
chunk_size = 20000
human_samples = []
ai_samples = []
human_count = 0
ai_count = 0
target = 25000

for chunk in pd.read_csv(data_path, chunksize=chunk_size):
    if human_count < target:
        h = chunk[chunk['label'] == 0].sample(n=min(target-human_count, len(chunk[chunk['label']==0])), random_state=42)
        if len(h) > 0:
            human_samples.append(h)
            human_count += len(h)
    
    if ai_count < target:
        a = chunk[chunk['label'] == 1].sample(n=min(target-ai_count, len(chunk[chunk['label']==1])), random_state=42)
        if len(a) > 0:
            ai_samples.append(a)
            ai_count += len(a)
    
    if human_count >= target and ai_count >= target:
        break

df = pd.concat(human_samples + ai_samples).sample(frac=1, random_state=42).reset_index(drop=True)

print(f"✅ Loaded {len(df):,} samples ({sum(df['label']==0):,} Human, {sum(df['label']==1):,} AI)")

# Extract features
print("\nExtracting TF-IDF features...")
vectorizer = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 3),
    min_df=2,
    max_df=0.85,
    sublinear_tf=True
)

X = vectorizer.fit_transform(df['text'])
y = df['label'].values

print(f"✅ Features: {X.shape}")

# Manual K-Fold
print("\n" + "="*80)
print("10-FOLD CROSS VALIDATION")
print("="*80)

kfold = StratifiedKFold(n_splits=10, shuffle=True, random_state=42)
fold_scores = []

for fold, (train_idx, val_idx) in enumerate(kfold.split(X, y), 1):
    X_train_fold = X[train_idx]
    X_val_fold = X[val_idx]
    y_train_fold = y[train_idx]
    y_val_fold = y[val_idx]
    
    model = LogisticRegression(max_iter=1000, C=1.0, solver='saga', random_state=42, n_jobs=-1)
    model.fit(X_train_fold, y_train_fold)
    
    y_pred = model.predict(X_val_fold)
    score = accuracy_score(y_val_fold, y_pred)
    fold_scores.append(score)
    
    print(f"Fold {fold:2d}/10: Accuracy = {score:.4f} ({score*100:.2f}%)")

mean_cv_score = np.mean(fold_scores)
std_cv_score = np.std(fold_scores)

print(f"\n{'='*80}")
print(f"CROSS-VALIDATION RESULTS")
print(f"{'='*80}")
print(f"Mean Accuracy: {mean_cv_score:.4f} ({mean_cv_score*100:.2f}%)")
print(f"Std Deviation: {std_cv_score:.4f}")
print(f"Min: {min(fold_scores):.4f}, Max: {max(fold_scores):.4f}")

# Train final model
print(f"\n{'='*80}")
print("TRAINING FINAL MODEL")
print(f"{'='*80}")

print("Training on full dataset...")
final_model = LogisticRegression(max_iter=1000, C=1.0, solver='saga', random_state=42, n_jobs=-1)
final_model.fit(X, y)

# Test set evaluation
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
y_pred = final_model.predict(X_test)
test_acc = accuracy_score(y_test, y_pred)

print(f"\n✅ Test Set Accuracy: {test_acc:.4f} ({test_acc*100:.2f}%)")

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['Human', 'AI']))

cm = confusion_matrix(y_test, y_pred)
print("\nConfusion Matrix:")
print(f"              Predicted")
print(f"            Human    AI")
print(f"Actual Human {cm[0,0]:5d}  {cm[0,1]:5d}")
print(f"       AI    {cm[1,0]:5d}  {cm[1,1]:5d}")

# Test Gemini
print(f"\n{'='*80}")
print("GEMINI SAMPLE TEST")
print(f"{'='*80}")

gemini = """Expansion (Enlargement): The push to integrate Western Balkan countries, Ukraine, and Moldova is not just a matter of economic inclusion but a profound geopolitical move to consolidate the democratic, liberal space of Europe against authoritarian influence."""

vec = vectorizer.transform([gemini])
pred = final_model.predict(vec)[0]
proba = final_model.predict_proba(vec)[0]

print(f"\nPrediction: {'AI' if pred == 1 else 'Human'}")
print(f"Confidence: AI={proba[1]:.2%}, Human={proba[0]:.2%}")

if proba[1] >= 0.75:
    print("✅ HIGH CONFIDENCE!")
elif proba[1] >= 0.65:
    print("✓ Good confidence")

# Save
print(f"\n{'='*80}")
print("SAVING MODEL")
print(f"{'='*80}")

models_dir = os.path.join(base_dir, "../Models")
joblib.dump(final_model, os.path.join(models_dir, "best_kfold_model.joblib"))
joblib.dump(vectorizer, os.path.join(models_dir, "best_kfold_vectorizer.joblib"))

print("✅ Saved!")

print(f"\n{'='*80}")
print("COMPLETE!")
print(f"{'='*80}")
print(f"CV Accuracy: {mean_cv_score*100:.2f}%")
print(f"Test Accuracy: {test_acc*100:.2f}%")
print(f"Samples: {len(df):,}")
print(f"{'='*80}")
