import joblib
import os

# Load model
base_dir = os.path.dirname(os.path.abspath(__file__))
model = joblib.load(os.path.join(base_dir, "Models/tfidf_model.joblib"))
vectorizer = joblib.load(os.path.join(base_dir, "Models/word_vectorizer.joblib"))

print("="*70)
print("MODEL TESTING")
print("="*70)

# Test cases
test_cases = [
    ("Hey! How are you doing today? I'm feeling great!", "HUMAN"),
    ("The implementation of artificial intelligence systems requires careful consideration of ethical implications and potential societal impacts.", "AI"),
    ("lol that's so funny 😂 can't believe u did that", "HUMAN"),
    ("In conclusion, the analysis demonstrates that the proposed methodology yields significant improvements over existing approaches.", "AI"),
    ("I went to the store yesterday and bought some groceries. It was a nice day.", "HUMAN"),
    ("Furthermore, it is important to note that the aforementioned considerations necessitate a comprehensive evaluation of the underlying mechanisms.", "AI"),
]

print("\nTesting predictions:\n")

for text, expected in test_cases:
    text_vec = vectorizer.transform([text])
    prediction = model.predict(text_vec)[0]
    proba = model.predict_proba(text_vec)[0]
    
    predicted_label = "AI" if prediction == 1 else "HUMAN"
    status = "✅" if predicted_label == expected else "❌"
    
    print(f"{status} Expected: {expected:6s} | Predicted: {predicted_label:6s} | Confidence: {max(proba):.2%}")
    print(f"   Text: {text[:80]}...")
    print(f"   Probabilities: Human={proba[0]:.2%}, AI={proba[1]:.2%}")
    print()

print("="*70)
print("\nNow paste YOUR test cases below:")
print("Enter text (or 'quit' to exit):")

while True:
    try:
        text = input("\nText: ")
        if text.lower() == 'quit':
            break
        
        text_vec = vectorizer.transform([text])
        prediction = model.predict(text_vec)[0]
        proba = model.predict_proba(text_vec)[0]
        
        predicted_label = "AI" if prediction == 1 else "HUMAN"
        
        print(f"\n  Prediction: {predicted_label}")
        print(f"  Confidence: Human={proba[0]:.2%}, AI={proba[1]:.2%}")
        
    except EOFError:
        break
    except Exception as e:
        print(f"Error: {e}")
