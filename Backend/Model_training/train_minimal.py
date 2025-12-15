"""
Minimal memory footprint - word TF-IDF only
"""
import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

print("="*70)
print("MINIMAL MEMORY AI DETECTOR TRAINING")
print("="*70)

base_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_dir, "../../data.csv/processed_data.csv")

# Load balanced data
print("\nLoading balanced data...")
SAMPLE_SIZE = 12000
chunk_size = 20000

human_samples = []
ai_samples = []
human_count = 0
ai_count = 0
target_per_class = SAMPLE_SIZE // 2

for i, chunk in enumerate(pd.read_csv(data_path, chunksize=chunk_size)):
    if 'label' not in chunk.columns:
        chunk['label'] = chunk['source'].apply(lambda s: 0 if str(s).lower() == 'human' else 1)
    
    chunk_human = chunk[chunk['label'] == 0]
    chunk_ai = chunk[chunk['label'] == 1]
    
    if human_count < target_per_class and len(chunk_human) > 0:
        needed = min(len(chunk_human), target_per_class - human_count)
        human_samples.append(chunk_human[['text', 'label']].sample(n=needed, random_state=42))
        human_count += needed
    
    if ai_count < target_per_class and len(chunk_ai) > 0:
        needed = min(len(chunk_ai), target_per_class - ai_count)
        ai_samples.append(chunk_ai[['text', 'label']].sample(n=needed, random_state=42))
        ai_count += needed
    
    print(f"  Chunk {i+1}: Human={human_count}/{target_per_class}, AI={ai_count}/{target_per_class}")
    
    if human_count >= target_per_class and ai_count >= target_per_class:
        break

df = pd.concat(human_samples + ai_samples).sample(frac=1, random_state=42).reset_index(drop=True)
print(f"\n✅ Dataset: {len(df)} samples")
print(df['label'].value_counts())

# Split
texts = df['text'].values
labels = df['label'].values

X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.25, random_state=42, stratify=labels
)

print(f"\nTrain: {len(X_train)}, Test: {len(X_test)}")

# Simple TF-IDF
print("\nExtracting TF-IDF features (word-level only)...")
vectorizer = TfidfVectorizer(
    max_features=2000,
    ngram_range=(1, 2),
    min_df=5,
    max_df=0.75,
    sublinear_tf=True
)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

print(f"Feature shape: {X_train_vec.shape}")

# Train
print("\nTraining...")
model = LogisticRegression(
    C=1.0,
    max_iter=300,
    solver='liblinear',
    random_state=42,
    class_weight='balanced'
)

model.fit(X_train_vec, y_train)

# Evaluate
y_pred = model.predict(X_test_vec)
acc = accuracy_score(y_test, y_pred)

print("\n" + "="*70)
print(f"Test Accuracy: {acc:.4f}")
print("\n" + classification_report(y_test, y_pred, target_names=['Human', 'AI']))

cm = confusion_matrix(y_test, y_pred)
print("Confusion Matrix:")
print(f"              Predicted")
print(f"            Human    AI")
print(f"Actual Human {cm[0,0]:4d}  {cm[0,1]:4d}")
print(f"       AI    {cm[1,0]:4d}  {cm[1,1]:4d}")

# Save
models_dir = os.path.join(base_dir, "../Models")
os.makedirs(models_dir, exist_ok=True)

joblib.dump(model, os.path.join(models_dir, "tfidf_model.joblib"))
joblib.dump(vectorizer, os.path.join(models_dir, "word_vectorizer.joblib"))

print("\n✅ Model saved!")
print("="*70)
