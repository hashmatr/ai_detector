"""
Train MACHINE LEARNING model on modern AI dataset
Uses ensemble of TF-IDF + Multiple ML algorithms
"""
import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import numpy as np

print("="*80)
print("TRAINING MACHINE LEARNING MODEL ON MODERN AI DATA")
print("="*80)

# Load dataset
base_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_dir, "../../data.csv/modern_ai_dataset.csv")

if not os.path.exists(data_path):
    print(f"\n❌ Dataset not found at: {data_path}")
    print("\nPlease run one of these first:")
    print("1. python download_modern_dataset.py")
    print("2. python create_demo_dataset.py")
    exit(1)

print(f"\nLoading data from: {data_path}")
df = pd.read_csv(data_path)

print(f"✅ Loaded {len(df):,} samples")
print(f"   Human: {sum(df['label']==0):,}")
print(f"   AI: {sum(df['label']==1):,}")

# Split data
texts = df['text'].values
labels = df['label'].values

X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.2, random_state=42, stratify=labels
)

print(f"\nTrain: {len(X_train):,} | Test: {len(X_test):,}")

# Feature extraction
print("\n" + "="*80)
print("FEATURE EXTRACTION")
print("="*80)

print("\nExtracting TF-IDF features...")
vectorizer = TfidfVectorizer(
    max_features=5000,
    ngram_range=(1, 3),  # Unigrams, bigrams, trigrams
    min_df=2,
    max_df=0.9,
    sublinear_tf=True,
    strip_accents='unicode'
)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

print(f"✅ Feature matrix shape: {X_train_vec.shape}")

# Train ensemble of models
print("\n" + "="*80)
print("TRAINING ENSEMBLE MODEL")
print("="*80)

print("\nTraining individual models...")

# Model 1: Logistic Regression
print("  [1/3] Logistic Regression...")
lr = LogisticRegression(C=1.0, max_iter=500, random_state=42, n_jobs=-1)
lr.fit(X_train_vec, y_train)

# Model 2: Random Forest
print("  [2/3] Random Forest...")
rf = RandomForestClassifier(n_estimators=100, max_depth=20, random_state=42, n_jobs=-1)
rf.fit(X_train_vec, y_train)

# Model 3: Gradient Boosting
print("  [3/3] Gradient Boosting...")
gb = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
gb.fit(X_train_vec, y_train)

# Create voting ensemble
print("\nCreating voting ensemble...")
ensemble = VotingClassifier(
    estimators=[
        ('lr', lr),
        ('rf', rf),
        ('gb', gb)
    ],
    voting='soft',  # Use probability voting
    n_jobs=-1
)

ensemble.fit(X_train_vec, y_train)

# Evaluate
print("\n" + "="*80)
print("EVALUATION")
print("="*80)

y_pred = ensemble.predict(X_test_vec)
y_proba = ensemble.predict_proba(X_test_vec)

acc = accuracy_score(y_test, y_pred)

print(f"\n✅ Test Accuracy: {acc:.4f} ({acc*100:.2f}%)")
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['Human', 'AI']))

cm = confusion_matrix(y_test, y_pred)
print("\nConfusion Matrix:")
print(f"              Predicted")
print(f"            Human    AI")
print(f"Actual Human {cm[0,0]:4d}  {cm[0,1]:4d}")
print(f"       AI    {cm[1,0]:4d}  {cm[1,1]:4d}")

# Save models
print("\n" + "="*80)
print("SAVING MODELS")
print("="*80)

models_dir = os.path.join(base_dir, "../Models")
os.makedirs(models_dir, exist_ok=True)

joblib.dump(ensemble, os.path.join(models_dir, "ml_ensemble_model.joblib"))
joblib.dump(vectorizer, os.path.join(models_dir, "ml_vectorizer.joblib"))

print("✅ Saved:")
print(f"   - ml_ensemble_model.joblib")
print(f"   - ml_vectorizer.joblib")

print("\n" + "="*80)
print("TRAINING COMPLETE!")
print("="*80)
print("\nTo use this model, update app.py to load:")
print("  - Models/ml_ensemble_model.joblib")
print("  - Models/ml_vectorizer.joblib")
print("="*80)
