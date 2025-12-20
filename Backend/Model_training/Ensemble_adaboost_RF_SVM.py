"""
Ensemble Model Training Script (Local Compatible)
==================================================
Trains: SVM, AdaBoost, Random Forest, CatBoost
Uses: CPU, .joblib format, saves to Models folder
"""

import pandas as pd
import numpy as np
import joblib
import time
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix


# --- CONFIGURATION ---
DATA_PATH = r"e:\Machine Learning Project\ai_detector\data.csv\processed_data.csv"
MODELS_DIR = r"e:\Machine Learning Project\ai_detector\Backend\Models"

# Create models directory if not exists
os.makedirs(MODELS_DIR, exist_ok=True)

# --- STEP 1: LOAD AND SPLIT DATA ---
print("=" * 60)
print("🚀 ENSEMBLE MODEL TRAINING (Local Compatible)")
print("=" * 60)
print("Models: SVM + AdaBoost + Random Forest")
print("Format: .joblib | Mode: CPU")
print("=" * 60)

print("\n⏳ [1/6] Loading Dataset...")
start_time = time.time()
df = pd.read_csv(DATA_PATH).dropna(subset=['cleaned_text', 'source'])
print(f"   📊 Total samples: {len(df):,}")

y = df['source'].apply(lambda x: 0 if str(x).lower() == 'human' else 1).values

# 60/20/20 Split
X_train_val, X_test_text, y_train_val, y_test = train_test_split(
    df['cleaned_text'], y, test_size=0.20, random_state=42, stratify=y
)
X_train_text, X_val_text, y_train, y_val = train_test_split(
    X_train_val, y_train_val, test_size=0.25, random_state=42, stratify=y_train_val
)
print(f"✅ Data Split Complete.")
print(f"   Train: {len(y_train):,} | Val: {len(y_val):,} | Test: {len(y_test):,}")

# --- STEP 2: TF-IDF VECTORIZATION ---
print("\n⏳ [2/6] Starting TF-IDF Vectorization...")
tfidf = TfidfVectorizer(max_features=10000, stop_words='english')
X_train = tfidf.fit_transform(X_train_text.astype(str))
X_val = tfidf.transform(X_val_text.astype(str))
X_test = tfidf.transform(X_test_text.astype(str))

# Save TF-IDF Vectorizer
tfidf_path = os.path.join(MODELS_DIR, 'tfidf_vectorizer.joblib')
joblib.dump(tfidf, tfidf_path)
print(f"✅ Vectorization Done. Features: {X_train.shape[1]:,}")
print(f"   💾 Saved: {tfidf_path}")

# --- STEP 3: INITIALIZE MODELS (CPU MODE) ---
print("\n" + "=" * 60)
print("📊 TRAINING MODELS")
print("=" * 60)

models = {
    "svm": SGDClassifier(loss='hinge', class_weight='balanced', random_state=42, n_jobs=-1),
    "adaboost": AdaBoostClassifier(
        estimator=DecisionTreeClassifier(max_depth=1, class_weight='balanced'),
        n_estimators=50, random_state=42
    ),
    "random_forest": RandomForestClassifier(n_estimators=100, max_depth=15, n_jobs=-1, random_state=42)
}

# --- STEP 4: TRAIN AND VALIDATE ---
results = {}
for name, model in models.items():
    save_path = os.path.join(MODELS_DIR, f'{name}_model.joblib')
    
    print(f"\n🧠 Training {name.upper()}...")
    m_start = time.time()
    
    try:
        model.fit(X_train, y_train)
        
        # Save the model immediately after training
        joblib.dump(model, save_path)
        
        val_acc = accuracy_score(y_val, model.predict(X_val))
        results[name] = {'model': model, 'accuracy': val_acc, 'path': save_path}
        
        print(f"✅ {name.upper()} Training Finished in {time.time() - m_start:.2f}s")
        print(f"   📈 Val Accuracy: {val_acc:.4%}")
        print(f"   💾 Saved: {save_path}")
        
    except Exception as e:
        print(f"❌ Failed to train {name}: {e}")

# --- STEP 5: FINAL EVALUATION ON UNSEEN TEST SET ---
print("\n" + "=" * 60)
print("🏆 FINAL PERFORMANCE ON UNSEEN TEST DATA")
print("=" * 60)

for name, data in results.items():
    model = data['model']
    preds = model.predict(X_test)
    test_acc = accuracy_score(y_test, preds)
    print(f"\n📊 {name.upper()}:")
    print(f"   Test Accuracy: {test_acc:.4%}")
    print(classification_report(y_test, preds, target_names=['Human', 'AI']))

# --- STEP 6: SUMMARY ---
print("\n" + "=" * 60)
print("📋 TRAINING SUMMARY")
print("=" * 60)
print(f"\n✅ Total Execution Time: {(time.time() - start_time)/60:.2f} minutes")
print("\n📁 Models saved to:")
for name, data in results.items():
    print(f"   ✅ {name.upper()}: {data['path']}")
print(f"   ✅ TF-IDF: {tfidf_path}")
print("\n✨ All models are now compatible with your local environment!")
print("=" * 60)