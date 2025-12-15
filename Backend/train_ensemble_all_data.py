"""
Train Ensemble Model (Random Forest + KNN) on All Available Datasets
This model will be used alongside RoBERTa for final predictions
"""
import os
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import re

def extract_text_features(text):
    """Extract linguistic features from text"""
    if not isinstance(text, str):
        text = str(text)
    
    words = text.split()
    word_count = len(words)
    
    features = {
        'text_length': len(text),
        'word_count': word_count,
        'avg_word_length': np.mean([len(w) for w in words]) if words else 0,
        'unique_word_ratio': len(set(words)) / word_count if word_count > 0 else 0,
        'upper_case_ratio': sum(1 for c in text if c.isupper()) / len(text) if text else 0,
        'digit_freq': sum(1 for c in text if c.isdigit()) / len(text) if text else 0,
        'punc_freq': sum(1 for c in text if c in '.,!?;:') / len(text) if text else 0,
        'exclamation_count': text.count('!'),
        'question_count': text.count('?'),
        'comma_count': text.count(','),
        'period_count': text.count('.'),
        'avg_sentence_length': word_count / max(text.count('.') + text.count('!') + text.count('?'), 1),
    }
    return features

print("=" * 60)
print("TRAINING ENSEMBLE MODEL ON ALL DATASETS")
print("=" * 60)

# -------------------------
# 1️⃣ Load and Combine All Datasets
# -------------------------
base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir, "../data.csv")

datasets = []
dataset_files = [
    'data_with_features.csv',
    'large_ai_dataset.csv', 
    'modern_ai_dataset.csv'
]

for filename in dataset_files:
    filepath = os.path.join(data_dir, filename)
    if os.path.exists(filepath):
        print(f"\n📂 Loading {filename}...")
        df = pd.read_csv(filepath)
        print(f"   Shape: {df.shape}")
        datasets.append(df)
    else:
        print(f"⚠️  {filename} not found, skipping...")

if not datasets:
    print("❌ No datasets found! Exiting...")
    exit(1)

# Combine all datasets
print("\n🔗 Combining datasets...")
combined_df = pd.concat(datasets, ignore_index=True)
print(f"Combined dataset shape: {combined_df.shape}")

# Ensure we have required columns
if 'text' not in combined_df.columns or 'label' not in combined_df.columns:
    print("❌ Required columns 'text' and 'label' not found!")
    exit(1)

# Clean data
combined_df = combined_df.dropna(subset=['text', 'label'])
combined_df['text'] = combined_df['text'].astype(str)

# Balance dataset (prevent bias)
print("\n⚖️  Balancing dataset...")
ai_samples = combined_df[combined_df['label'] == 1]
human_samples = combined_df[combined_df['label'] == 0]

min_samples = min(len(ai_samples), len(human_samples))
# Use up to 50k samples from each class for training efficiency
max_samples_per_class = min(50000, min_samples)

ai_samples = ai_samples.sample(n=max_samples_per_class, random_state=42)
human_samples = human_samples.sample(n=max_samples_per_class, random_state=42)

balanced_df = pd.concat([ai_samples, human_samples], ignore_index=True)
balanced_df = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"Balanced dataset: {len(balanced_df)} samples ({max_samples_per_class} AI, {max_samples_per_class} Human)")

# -------------------------
# 2️⃣ Feature Engineering
# -------------------------
print("\n🔧 Extracting features...")

# Extract linguistic features
feature_dicts = balanced_df['text'].apply(extract_text_features)
feature_df = pd.DataFrame(feature_dicts.tolist())

# TF-IDF features (limited to 100 features for efficiency)
print("   Creating TF-IDF features...")
tfidf_vectorizer = TfidfVectorizer(max_features=100, ngram_range=(1, 2), min_df=5)
tfidf_features = tfidf_vectorizer.fit_transform(balanced_df['text']).toarray()
tfidf_df = pd.DataFrame(tfidf_features, columns=[f'tfidf_{i}' for i in range(tfidf_features.shape[1])])

# Combine all features
X = pd.concat([feature_df, tfidf_df], axis=1)
y = balanced_df['label'].values

print(f"Feature matrix shape: {X.shape}")
print(f"Features: {X.columns.tolist()[:10]}... (showing first 10)")

# -------------------------
# 3️⃣ Train/Test Split
# -------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\nTraining set: {X_train.shape[0]} samples")
print(f"Test set: {X_test.shape[0]} samples")

# -------------------------
# 4️⃣ Build Ensemble Model
# -------------------------
print("\n🤖 Building ensemble model...")

# Scale features for KNN
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Random Forest (doesn't need scaling but we'll use scaled data for consistency)
rf_model = RandomForestClassifier(
    n_estimators=50,  # Reduced for faster training
    max_depth=20,
    random_state=42,
    n_jobs=-1,
    class_weight='balanced'
)

# KNN
knn_model = KNeighborsClassifier(
    n_neighbors=7,
    weights='distance',
    n_jobs=-1
)

# Train individual models
print("\n📚 Training Random Forest...")
rf_model.fit(X_train_scaled, y_train)
rf_train_acc = accuracy_score(y_train, rf_model.predict(X_train_scaled))
rf_test_acc = accuracy_score(y_test, rf_model.predict(X_test_scaled))
print(f"   Train Accuracy: {rf_train_acc:.4f}")
print(f"   Test Accuracy: {rf_test_acc:.4f}")

print("\n📚 Training KNN...")
knn_model.fit(X_train_scaled, y_train)
knn_train_acc = accuracy_score(y_train, knn_model.predict(X_train_scaled))
knn_test_acc = accuracy_score(y_test, knn_model.predict(X_test_scaled))
print(f"   Train Accuracy: {knn_train_acc:.4f}")
print(f"   Test Accuracy: {knn_test_acc:.4f}")

# Create ensemble with voting
print("\n🎯 Creating ensemble (soft voting)...")
ensemble = VotingClassifier(
    estimators=[
        ('rf', rf_model),
        ('knn', knn_model)
    ],
    voting='soft',
    n_jobs=-1
)

ensemble.fit(X_train_scaled, y_train)

# -------------------------
# 5️⃣ Evaluate Ensemble
# -------------------------
print("\n📊 Evaluating ensemble model...")

y_train_pred = ensemble.predict(X_train_scaled)
y_test_pred = ensemble.predict(X_test_scaled)
y_test_proba = ensemble.predict_proba(X_test_scaled)[:, 1]

train_acc = accuracy_score(y_train, y_train_pred)
test_acc = accuracy_score(y_test, y_test_pred)
precision = precision_score(y_test, y_test_pred)
recall = recall_score(y_test, y_test_pred)
f1 = f1_score(y_test, y_test_pred)

print("\n" + "=" * 60)
print("ENSEMBLE MODEL PERFORMANCE")
print("=" * 60)
print(f"Training Accuracy:   {train_acc:.4f}")
print(f"Test Accuracy:       {test_acc:.4f}")
print(f"Precision:           {precision:.4f}")
print(f"Recall:              {recall:.4f}")
print(f"F1-Score:            {f1:.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_test_pred, target_names=['Human', 'AI']))

# -------------------------
# 6️⃣ Save Models and Artifacts
# -------------------------
models_dir = os.path.join(base_dir, "Models")
os.makedirs(models_dir, exist_ok=True)

print("\n💾 Saving models...")

# Save ensemble model
ensemble_path = os.path.join(models_dir, "ml_ensemble_model.joblib")
joblib.dump(ensemble, ensemble_path)
print(f"   ✅ Ensemble model: {ensemble_path}")

# Save scaler
scaler_path = os.path.join(models_dir, "ml_ensemble_scaler.joblib")
joblib.dump(scaler, scaler_path)
print(f"   ✅ Scaler: {scaler_path}")

# Save TF-IDF vectorizer
tfidf_path = os.path.join(models_dir, "ml_ensemble_tfidf.joblib")
joblib.dump(tfidf_vectorizer, tfidf_path)
print(f"   ✅ TF-IDF vectorizer: {tfidf_path}")

# Save feature names for reference
feature_names_path = os.path.join(models_dir, "ml_ensemble_features.txt")
with open(feature_names_path, 'w') as f:
    f.write('\n'.join(X.columns.tolist()))
print(f"   ✅ Feature names: {feature_names_path}")

print("\n" + "=" * 60)
print("✅ TRAINING COMPLETE!")
print("=" * 60)
print(f"\nModel saved with {test_acc:.2%} test accuracy")
print("Ready to be integrated with RoBERTa model in app.py")
