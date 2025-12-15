# gradient_boosting_training.py
import os
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import joblib
import numpy as np

# -------------------------
# Load dataset
# -------------------------
base_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_dir, "../../data.csv/data_with_features.csv")

if not os.path.exists(data_path):
    print(f"Error: Data file not found at {data_path}")
    exit(1)

df = pd.read_csv(data_path)

# Drop non-numeric columns, label, and length-based features
X = df.drop(columns=['label', 'text', 'source', 'prompt_id', 'cleaned_text', 
                     'text_length', 'word_count', 'has_min_words'], errors='ignore')
y = df['label']  # 0 = Human, 1 = AI

print(f"Dataset shape: {X.shape}")
print(f"Features: {list(X.columns)}")
print(f"Class distribution: Human={sum(y==0)}, AI={sum(y==1)}")

# Handle Class Imbalance
count_human = sum(y==0)
count_ai = sum(y==1)
min_count = min(count_human, count_ai)

print(f"\nBalancing classes (undersampling majority)...")
print(f"   Human: {count_human}, AI: {count_ai} -> Target: {min_count} each")

if min_count < 10:
    print("❌ Critical Error: Not enough samples for one class to train.")
    exit(1)

# Downsample majority
df_0 = df[df['label'] == 0].sample(n=min_count, random_state=42)
df_1 = df[df['label'] == 1].sample(n=min_count, random_state=42)
df_balanced = pd.concat([df_0, df_1]).sample(frac=1, random_state=42) # Shuffle

# Drop non-numeric columns, label, and length-based features
# Removing 'ttr' because it is strongly correlated with text length (short text = high TTR)
X = df_balanced.drop(columns=['label', 'text', 'source', 'prompt_id', 'cleaned_text', 
                     'text_length', 'word_count', 'has_min_words', 'ttr'], errors='ignore')
y = df_balanced['label']  # 0 = Human, 1 = AI

print(f"Balanced Dataset shape: {X.shape}")

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# -------------------------
# Train Gradient Boosting (More robust than RF)
# -------------------------
print("\nTraining Gradient Boosting Model...")
print("This may take a few minutes...")

gb = GradientBoostingClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=3,
    random_state=42,
    subsample=0.8,
    verbose=1
)

gb.fit(X_train, y_train)

# Predict
y_pred = gb.predict(X_test)
y_proba = gb.predict_proba(X_test)[:, 1]

# Metrics
acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred)
rec = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_proba)

print("\n" + "="*50)
print("Gradient Boosting Metrics:")
print("="*50)
print(f"Accuracy:  {acc:.4f}")
print(f"Precision: {prec:.4f}")
print(f"Recall:    {rec:.4f}")
print(f"F1-Score:  {f1:.4f}")
print(f"ROC-AUC:   {roc_auc:.4f}")
print("="*50)

# Cross-validation score
print("\nPerforming 5-fold cross-validation...")
cv_scores = cross_val_score(gb, X_train, y_train, cv=5, scoring='roc_auc')
print(f"CV ROC-AUC: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")

# Feature importance
print("\nTop 5 Most Important Features:")
feature_importance = sorted(zip(X.columns, gb.feature_importances_), 
                           key=lambda x: x[1], reverse=True)
for i, (feat, imp) in enumerate(feature_importance[:5], 1):
    print(f"{i}. {feat}: {imp:.4f}")

# -------------------------
# Save Model
# -------------------------
models_dir = os.path.join(base_dir, "../Models")
os.makedirs(models_dir, exist_ok=True)

model_save_path = os.path.join(models_dir, "gradient_boosting_model.joblib")
joblib.dump(gb, model_save_path)

print(f"\nModel saved to {model_save_path}")
