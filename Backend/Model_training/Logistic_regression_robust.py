# logistic_regression_training.py
import os
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, roc_curve
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

# -------------------------
# 1️⃣ Load dataset
# -------------------------
base_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_dir, "../../data.csv/data_with_features.csv")

if not os.path.exists(data_path):
    print(f"Error: Data file not found at {data_path}")
    exit(1)

df = pd.read_csv(data_path)

# Drop non-numeric columns and label
X = df.drop(columns=['label', 'text', 'source', 'prompt_id', 'cleaned_text'], errors='ignore')
y = df['label']  # 0 = Human, 1 = AI

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# -------------------------
# 2️⃣ Train Logistic Regression (Robust Baseline)
# -------------------------
# Logistic Regression is often less prone to overfitting on simple features than Random Forest
# We use a Pipeline to ensure scaling is handled correctly
lr_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('lr', LogisticRegression(random_state=42, max_iter=1000, class_weight='balanced'))
])

print("Training Logistic Regression Model...")
lr_pipeline.fit(X_train, y_train)

# Predict
y_pred = lr_pipeline.predict(X_test)
y_proba = lr_pipeline.predict_proba(X_test)[:, 1]

# Metrics
acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred)
rec = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_proba)

print("\nLogistic Regression Metrics:")
print(f"Accuracy: {acc:.4f}")
print(f"Precision: {prec:.4f}")
print(f"Recall: {rec:.4f}")
print(f"F1-Score: {f1:.4f}")
print(f"ROC-AUC: {roc_auc:.4f}")

# -------------------------
# 3️⃣ Save Model
# -------------------------
models_dir = os.path.join(base_dir, "../Models")
os.makedirs(models_dir, exist_ok=True)

model_save_path = os.path.join(models_dir, "logistic_regression_model.joblib")
joblib.dump(lr_pipeline, model_save_path)

print(f"\nModel saved to {model_save_path}")
