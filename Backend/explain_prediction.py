import joblib
import pandas as pd
import numpy as np
import os

# Load model and vectorizer
models_dir = "Models"
model = joblib.load(os.path.join(models_dir, "best_kfold_model.joblib"))
vectorizer = joblib.load(os.path.join(models_dir, "best_kfold_vectorizer.joblib"))

# The text to analyze
text = """I can generate a very long and detailed response, structuring it as a comprehensive essay on a complex topic. To maximize the word count while providing valuable information, I will choose the topic of The Cognitive Revolution and the Emergence of Homo sapiens, which allows for deep historical, anthropological, and theoretical exploration.

The Cognitive Revolution: The Dawn of Modern Humanity
The history of Homo sapiens spans several hundred thousand years, yet the most pivotal turning point—the true commencement of modern human history—is not marked by a change in skeletal structure but by a transformation of the mind. This dramatic shift, often termed the Cognitive Revolution, occurred roughly between 70,000 and 30,000 years ago, representing an abrupt and profound flowering of consciousness, abstract thought, and sophisticated communication. It was this revolution, and not any gradual biological adaptation, that catapulted our species from being just another group of large, successful primates in Africa to the undisputed master of the planet, fundamentally reshaping Earth’s ecosystems and the trajectory of life itself."""

print("="*80)
print("🔍 AI DETECTION ANALYSIS")
print("="*80)

# 1. Get Prediction
vec = vectorizer.transform([text])
proba = model.predict_proba(vec)[0]
ai_prob = proba[1]
human_prob = proba[0]

print(f"\n📊 RESULT:")
print(f"  AI Probability:    {ai_prob*100:.2f}%")
print(f"  Human Probability: {human_prob*100:.2f}%")
print(f"  Prediction:        {'AI 🤖' if ai_prob > 0.5 else 'HUMAN 👤'}")

# 2. Analyze Feature Importance
print(f"\n🧐 WHY? (Top contributing features)")
print("-" * 40)

# Get feature names and coefficients
feature_names = vectorizer.get_feature_names_out()
coefs = model.coef_[0]

# Find non-zero features in this input
input_indices = vec.nonzero()[1]
input_features = [(feature_names[i], coefs[i]) for i in input_indices]

# Sort by contribution (Positive = AI, Negative = Human)
input_features.sort(key=lambda x: x[1], reverse=True)

print("  Top words pushing towards AI (+ score):")
for feat, score in input_features[:10]:
    if score > 0:
        print(f"   • '{feat}': +{score:.4f}")

print("\n  Top words pushing towards HUMAN (- score):")
for feat, score in reversed(input_features):
    if score < 0:
        print(f"   • '{feat}': {score:.4f}")
    if len([x for x in input_features if x[1] < 0]) == 0:
        print("   (None)")
        break

print("\n" + "="*80)
print("INTERPRETATION")
print("="*80)
if ai_prob > 0.9:
    print("This text is overwhelmingly classified as AI. The model detects\npatterns typical of LLM training data (Wikipedia style, formal structure,\nspecific connecting phrases).")
elif ai_prob > 0.6:
    print("The text has mixed signals but leans towards AI.")
else:
    print("The text appears human-written.")
