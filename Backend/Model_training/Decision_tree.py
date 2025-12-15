# decision_tree_training.py
import os
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, roc_curve
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

# -------------------------
# 1️⃣ Load dataset (already preprocessed and numeric)
# -------------------------
# Construct absolute path to the data file
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
# 2️⃣ Function to train and evaluate Decision Tree
# -------------------------
def train_decision_tree(X_train, X_test, y_train, y_test):
    # Train model
    dt = DecisionTreeClassifier(random_state=42)
    dt.fit(X_train, y_train)

    # Predict
    y_pred = dt.predict(X_test)
    y_proba = dt.predict_proba(X_test)[:, 1]

    # Metrics
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_proba)

    print("Decision Tree Metrics:")
    print(f"Accuracy: {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall: {rec:.4f}")
    print(f"F1-Score: {f1:.4f}")
    print(f"ROC-AUC: {roc_auc:.4f}")

    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6,5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=["Human","AI"], yticklabels=["Human","AI"])
    plt.title("Confusion Matrix - Decision Tree")
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.show()

    # ROC Curve
    fpr, tpr, thresholds = roc_curve(y_test, y_proba)
    plt.figure(figsize=(6,5))
    plt.plot(fpr, tpr, label=f"ROC Curve (AUC = {roc_auc:.4f})")
    plt.plot([0,1], [0,1], 'k--')
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("ROC Curve - Decision Tree")
    plt.legend()
    plt.show()

    return dt  # trained model

# -------------------------
# 3️⃣ Train and evaluate
# -------------------------
best_dt = train_decision_tree(X_train, X_test, y_train, y_test)

# -------------------------
# 4️⃣ Save the model
# -------------------------
models_dir = os.path.join(base_dir, "../Models")
os.makedirs(models_dir, exist_ok=True)
model_save_path = os.path.join(models_dir, "decision_tree_model.joblib")
joblib.dump(best_dt, model_save_path)
print(f"Model saved to {model_save_path}")
