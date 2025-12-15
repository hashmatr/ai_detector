# ensemble_training.py
import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

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
# 2️⃣ Define Models
# -------------------------

# KNN Pipeline (Scaling is crucial for KNN)
knn_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('knn', KNeighborsClassifier(n_neighbors=5, n_jobs=-1))
])

# Random Forest (Scaling not strictly necessary but good for consistency in voting)
rf_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)

# Ensemble (Voting Classifier)
# 'soft' voting predicts the class label based on the argmax of the sums of the predicted probabilities.
ensemble = VotingClassifier(
    estimators=[
        ('knn', knn_pipeline),
        ('rf', rf_model)
    ],
    voting='soft',
    n_jobs=-1
)

# -------------------------
# 3️⃣ Train and Evaluate
# -------------------------
print("Training Ensemble Model (KNN + Random Forest)...")
ensemble.fit(X_train, y_train)
# Training set evaluation
y_train_pred = ensemble.predict(X_train)
train_acc = accuracy_score(y_train, y_train_pred)
print(f"Training Accuracy: {train_acc:.4f}")

# Predict
y_pred = ensemble.predict(X_test)
y_proba = ensemble.predict_proba(X_test)[:, 1]

# Metrics
acc = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred)
rec = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_proba)

print("\nEnsemble Metrics:")
print(f"Accuracy: {acc:.4f}")
print(f"Precision: {prec:.4f}")
print(f"Recall: {rec:.4f}")
print(f"F1-Score: {f1:.4f}")
print(f"ROC-AUC: {roc_auc:.4f}")
cm = confusion_matrix(y_test, y_pred)
print("\nConfusion Matrix:")
print(cm)

# -------------------------
# 4️⃣ Save Model
# -------------------------
models_dir = os.path.join(base_dir, "../Models")
os.makedirs(models_dir, exist_ok=True)

model_save_path = os.path.join(models_dir, "ensemble_model.joblib")
joblib.dump(ensemble, model_save_path)

print(f"\nModel saved to {model_save_path}")
