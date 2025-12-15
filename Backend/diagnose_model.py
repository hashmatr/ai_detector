"""
Complete diagnostic of current model performance
"""
import joblib
import os

# Load the current model
models_dir = "Models"
model = joblib.load(os.path.join(models_dir, "best_kfold_model.joblib"))
vectorizer = joblib.load(os.path.join(models_dir, "best_kfold_vectorizer.joblib"))

print("="*80)
print("CURRENT MODEL DIAGNOSTIC")
print("="*80)

print(f"\nModel Type: {type(model).__name__}")
print(f"Vectorizer Features: {len(vectorizer.get_feature_names_out())}")

# Test samples
test_cases = [
    ("Your Gemini Sample (SHOULD BE AI)", 
     "Expansion (Enlargement): The push to integrate Western Balkan countries, Ukraine, and Moldova is not just a matter of economic inclusion but a profound geopolitical move to consolidate the democratic, liberal space of Europe against authoritarian influence."),
    
    ("Clear AI Text",
     "In conclusion, the analysis demonstrates that the proposed methodology yields significant improvements over existing approaches. Furthermore, it is important to note that the aforementioned considerations necessitate a comprehensive evaluation."),
    
    ("Clear Human Text",
     "hey whats up? i was thinking we should grab coffee tomorrow if ur free. let me know!"),
    
    ("Another Human",
     "omg you wont believe what happened today!! my boss literally called a meeting just to tell us about new coffee machines lol"),
]

print("\n" + "="*80)
print("TESTING PREDICTIONS")
print("="*80)

for name, text in test_cases:
    vec = vectorizer.transform([text])
    pred = model.predict(vec)[0]
    
    if hasattr(model, 'predict_proba'):
        proba = model.predict_proba(vec)[0]
        ai_conf = proba[1]
        human_conf = proba[0]
    else:
        ai_conf = 1.0 if pred == 1 else 0.0
        human_conf = 1.0 if pred == 0 else 0.0
    
    label = "AI" if pred == 1 else "HUMAN"
    
    print(f"\n{name}:")
    print(f"  Prediction: {label}")
    print(f"  AI: {ai_conf*100:.1f}% | Human: {human_conf*100:.1f}%")
    print(f"  Text: {text[:80]}...")

print("\n" + "="*80)
print("ISSUE DIAGNOSIS")
print("="*80)

# Check if model is actually trained
if hasattr(model, 'coef_'):
    print(f"\n[OK] Model has coefficients (is trained)")
    print(f"  Coefficient shape: {model.coef_.shape}")
else:
    print(f"\n[FAIL] Model may not be properly trained")

# Check vectorizer
sample_features = vectorizer.transform(["test"])
print(f"\n[OK] Vectorizer working")
print(f"  Sample vector shape: {sample_features.shape}")

print("\n" + "="*80)
