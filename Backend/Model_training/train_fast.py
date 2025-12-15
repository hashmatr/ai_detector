"""
FAST training on modern AI dataset (optimized for speed)
Uses smaller subset and faster algorithms
"""
import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

print("="*80)
print("FAST TRAINING ON MODERN AI DATASET")
print("="*80)

# Load dataset
base_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_dir, "../../data.csv/modern_ai_dataset.csv")

print(f"\nLoading data...")
df = pd.read_csv(data_path)

print(f"✅ Total samples: {len(df):,}")

# Use a manageable subset for faster training
SAMPLE_SIZE = 20000  # 10k per class
print(f"\nSampling {SAMPLE_SIZE:,} balanced samples for faster training...")

df_human = df[df['label'] == 0].sample(n=min(SAMPLE_SIZE//2, sum(df['label']==0)), random_state=42)
df_ai = df[df['label'] == 1].sample(n=min(SAMPLE_SIZE//2, sum(df['label']==1)), random_state=42)

df_sampled = pd.concat([df_human, df_ai]).sample(frac=1, random_state=42).reset_index(drop=True)

print(f"✅ Using {len(df_sampled):,} samples")
print(f"   Human: {sum(df_sampled['label']==0):,}")
print(f"   AI: {sum(df_sampled['label']==1):,}")

# Split
texts = df_sampled['text'].values
labels = df_sampled['label'].values

X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.2, random_state=42, stratify=labels
)

print(f"\nTrain: {len(X_train):,} | Test: {len(X_test):,}")

# Feature extraction (optimized)
print("\n" + "="*80)
print("FEATURE EXTRACTION")
print("="*80)

vectorizer = TfidfVectorizer(
    max_features=3000,  # Reduced for speed
    ngram_range=(1, 2),  # Unigrams and bigrams only
    min_df=3,
    max_df=0.85,
    sublinear_tf=True
)

print("Extracting features...")
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

print(f"✅ Feature matrix: {X_train_vec.shape}")

# Train single fast model
print("\n" + "="*80)
print("TRAINING MODEL")
print("="*80)

print("Training Logistic Regression with L2 regularization...")
model = LogisticRegression(
    C=1.0,
    max_iter=300,
    solver='saga',
    random_state=42,
    n_jobs=-1,
    verbose=1
)

model.fit(X_train_vec, y_train)

# Evaluate
print("\n" + "="*80)
print("EVALUATION")
print("="*80)

y_pred = model.predict(X_test_vec)
y_proba = model.predict_proba(X_test_vec)

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

# Test on your Gemini sample
print("\n" + "="*80)
print("TESTING ON YOUR GEMINI SAMPLE")
print("="*80)

gemini_text = """Expansion (Enlargement): The push to integrate Western Balkan countries, Ukraine, and Moldova is not just a matter of economic inclusion but a profound geopolitical move to consolidate the democratic, liberal space of Europe against authoritarian influence. This process will inevitably add complexity and divergence to the Union."""

text_vec = vectorizer.transform([gemini_text])
pred = model.predict(text_vec)[0]
proba = model.predict_proba(text_vec)[0]

print(f"\nGemini Text Prediction:")
print(f"  Label: {'AI' if pred == 1 else 'Human'}")
print(f"  Confidence: Human={proba[0]:.2%}, AI={proba[1]:.2%}")

if proba[1] > 0.7:
    print("  ✅ Correctly identified as AI with high confidence!")
else:
    print("  ⚠️  Low confidence - may need more training data")

# Save
print("\n" + "="*80)
print("SAVING MODEL")
print("="*80)

models_dir = os.path.join(base_dir, "../Models")
os.makedirs(models_dir, exist_ok=True)

joblib.dump(model, os.path.join(models_dir, "modern_ai_model.joblib"))
joblib.dump(vectorizer, os.path.join(models_dir, "modern_vectorizer.joblib"))

print("✅ Saved:")
print("   - modern_ai_model.joblib")
print("   - modern_vectorizer.joblib")

print("\n" + "="*80)
print("TRAINING COMPLETE!")
print("="*80)
print("\nRestart your backend with: python app.py")
print("The app will automatically use the new model.")
print("="*80)
