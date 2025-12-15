from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import joblib
from scipy.sparse import hstack

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# -------------------------
# Load TF-IDF Model
# -------------------------
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'Models', 'tfidf_model.joblib')
WORD_VEC_PATH = os.path.join(os.path.dirname(__file__), 'Models', 'word_vectorizer.joblib')
CHAR_VEC_PATH = os.path.join(os.path.dirname(__file__), 'Models', 'char_vectorizer.joblib')

print("Loading TF-IDF model...")
try:
    model = joblib.load(MODEL_PATH)
    word_vectorizer = joblib.load(WORD_VEC_PATH)
    char_vectorizer = joblib.load(CHAR_VEC_PATH)
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None
    word_vectorizer = None
    char_vectorizer = None

@app.route('/predict', methods=['POST'])
def predict():
    if not model or not word_vectorizer or not char_vectorizer:
        return jsonify({'error': 'Model not loaded'}), 500

    data = request.get_json()
    text = data.get('text', '')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        # Transform text using both vectorizers
        text_word = word_vectorizer.transform([text])
        text_char = char_vectorizer.transform([text])
        
        # Combine features
        text_combined = hstack([text_word, text_char])
        
        # Predict
        prediction = model.predict(text_combined)[0]
        probabilities = model.predict_proba(text_combined)[0]
        
        # Extract probabilities
        human_prob = probabilities[0]
        ai_prob = probabilities[1]
        
        result = {
            'is_ai': bool(prediction == 1),
            'ai_probability': float(ai_prob),
            'human_probability': float(human_prob),
            'label': 'AI' if prediction == 1 else 'Human'
        }
        
        print(f"Prediction: {result['label']} (AI: {ai_prob:.2%}, Human: {human_prob:.2%})")
        
        return jsonify(result)
        
    except Exception as e:
        import traceback
        print("ERROR:", str(e))
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
