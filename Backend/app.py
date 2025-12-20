from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import pandas as pd
import os
import re
from docx import Document
from PyPDF2 import PdfReader
from werkzeug.utils import secure_filename
import io

app = Flask(__name__)
CORS(app)

# ===========================
# GLOBAL VARIABLES
# ===========================

# Pure ML Ensemble Models
svm_model = None
adaboost_model = None
random_forest_model = None

tfidf_vectorizer = None

# Deep Learning Model (RoBERTa)
roberta_model = None
roberta_tokenizer = None
torch_available = False

# Model weights for ensemble voting
MODEL_WEIGHTS = {
    'SVM': 0.35,
    'AdaBoost': 0.20,
    'RandomForest': 0.45
}

# Hybrid weights
ROBERTA_WEIGHT = 0.70
ML_WEIGHT = 0.30

# Models directory
MODELS_DIR = os.path.join(os.path.dirname(__file__), "Models")

# ===========================
# LOAD MODELS
# ===========================

print("=" * 60)
print("🚀 LOADING AI DETECTION MODELS")
print("=" * 60)

# --- LOAD ML MODELS ---
print("\n📦 LOADING PURE ML MODELS")
print("-" * 40)

# Load TF-IDF Vectorizer
print(f"📝 Loading TF-IDF Vectorizer...")
tfidf_path = os.path.join(MODELS_DIR, "tfidf_vectorizer.joblib")
try:
    if os.path.exists(tfidf_path):
        tfidf_vectorizer = joblib.load(tfidf_path)
        print(f"   ✅ TF-IDF Vectorizer loaded")
except Exception as e:
    print(f"   ❌ Failed: {e}")

# Load SVM Model
print(f"🔷 Loading SVM Model...")
svm_path = os.path.join(MODELS_DIR, "svm_model.joblib")
try:
    if os.path.exists(svm_path):
        svm_model = joblib.load(svm_path)
        print(f"   ✅ SVM Model loaded")
except Exception as e:
    print(f"   ❌ Failed: {e}")

# Load AdaBoost Model
print(f"🔶 Loading AdaBoost Model...")
adaboost_path = os.path.join(MODELS_DIR, "adaboost_model.joblib")
try:
    if os.path.exists(adaboost_path):
        adaboost_model = joblib.load(adaboost_path)
        print(f"   ✅ AdaBoost Model loaded")
except Exception as e:
    print(f"   ❌ Failed: {e}")

# Load Random Forest Model
print(f"🌲 Loading Random Forest Model...")
rf_path = os.path.join(MODELS_DIR, "random_forest_model.joblib")
try:
    if os.path.exists(rf_path):
        random_forest_model = joblib.load(rf_path)
        print(f"   ✅ Random Forest Model loaded")
except Exception as e:
    print(f"   ❌ Failed: {e}")

# Count ML models
ml_models_loaded = sum([
    svm_model is not None,
    adaboost_model is not None,
    random_forest_model is not None
])

# --- LOAD DL MODEL (RoBERTa) ---
print("\n🤖 LOADING DEEP LEARNING MODEL")
print("-" * 40)
print("📥 Loading RoBERTa Transformer...")

try:
    import torch
    import torch.nn.functional as F
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    
    torch_available = True
    roberta_model_name = "Hello-SimpleAI/chatgpt-detector-roberta"
    
    roberta_tokenizer = AutoTokenizer.from_pretrained(roberta_model_name)
    roberta_model = AutoModelForSequenceClassification.from_pretrained(roberta_model_name)
    print(f"   ✅ RoBERTa loaded ({roberta_model_name})")
except Exception as e:
    print(f"   ❌ RoBERTa not available: {e}")
    torch_available = False

print("\n" + "=" * 60)
print(f"✅ ML MODELS: {ml_models_loaded}/3")
print(f"✅ DL MODEL: {'RoBERTa Loaded' if roberta_model else 'Not Available'}")
print(f"📊 TF-IDF: {'✅' if tfidf_vectorizer else '❌'}")
print("-" * 60)
print(f"⚖️  HYBRID RATIO: RoBERTa {ROBERTA_WEIGHT*100:.0f}% | ML {ML_WEIGHT*100:.0f}%")
print("=" * 60 + "\n")

# ===========================
# PREDICTION FUNCTIONS
# ===========================

def predict_ml_only(text):
    """Pure ML prediction using SVM, AdaBoost, Random Forest"""
    if not tfidf_vectorizer:
        raise ValueError("TF-IDF Vectorizer not loaded")
    
    X = tfidf_vectorizer.transform([text])
    predictions = {}
    probabilities = {}
    
    if svm_model:
        try:
            pred = svm_model.predict(X)[0]
            predictions['SVM'] = int(pred)
            decision = svm_model.decision_function(X)[0]
            prob = 1 / (1 + np.exp(-decision))
            probabilities['SVM'] = float(prob)
        except Exception as e:
            print(f"⚠️ SVM error: {e}")
    
    if adaboost_model:
        try:
            pred = adaboost_model.predict(X)[0]
            predictions['AdaBoost'] = int(pred)
            prob = adaboost_model.predict_proba(X)[0][1]
            probabilities['AdaBoost'] = float(prob)
        except Exception as e:
            print(f"⚠️ AdaBoost error: {e}")
    
    if random_forest_model:
        try:
            pred = random_forest_model.predict(X)[0]
            predictions['RandomForest'] = int(pred)
            prob = random_forest_model.predict_proba(X)[0][1]
            probabilities['RandomForest'] = float(prob)
        except Exception as e:
            print(f"⚠️ Random Forest error: {e}")
    
    if not probabilities:
        raise ValueError("No ML models available")
    
    # Weighted average
    total_weight = 0
    weighted_prob = 0
    for model_name, prob in probabilities.items():
        weight = MODEL_WEIGHTS.get(model_name, 0.33)
        weighted_prob += weight * prob
        total_weight += weight
    
    final_prob = weighted_prob / total_weight if total_weight > 0 else 0.5
    
    return {
        'final_probability': final_prob,
        'predictions': predictions,
        'probabilities': probabilities,
        'models_used': len(predictions)
    }


def predict_roberta(text):
    """RoBERTa Deep Learning prediction"""
    import torch
    import torch.nn.functional as F
    
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 50]
    
    if not sentences:
        sentences = [text]
    
    if len(sentences) > 1:
        chunks = sentences + [text]
    else:
        chunks = sentences
    
    chunk_probs = []
    for chunk in chunks:
        inputs = roberta_tokenizer(chunk, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = roberta_model(**inputs)
            probs = F.softmax(outputs.logits, dim=-1)
            ai_p = float(probs[0][1])
            chunk_probs.append(ai_p)
    
    avg_prob = sum(chunk_probs) / len(chunk_probs)
    calibrated = min(avg_prob * 1.35, 1.0)
    
    return calibrated


def predict_hybrid(text):
    """Hybrid ML + DL prediction"""
    ml_result = predict_ml_only(text)
    ml_prob = ml_result['final_probability']
    
    roberta_prob = predict_roberta(text)
    
    final_prob = (ROBERTA_WEIGHT * roberta_prob) + (ML_WEIGHT * ml_prob)
    
    return {
        'final_probability': final_prob,
        'ml_probability': ml_prob,
        'roberta_probability': roberta_prob,
        'ml_breakdown': ml_result['probabilities']
    }

# ===========================
# ROUTES
# ===========================

@app.route('/info', methods=['GET'])
def get_info():
    return jsonify({
        'ml_models_loaded': ml_models_loaded,
        'dl_model_loaded': roberta_model is not None,
        'vectorizer_loaded': tfidf_vectorizer is not None,
        'modes_available': {
            'ml_only': ml_models_loaded > 0 and tfidf_vectorizer is not None,
            'hybrid': ml_models_loaded > 0 and roberta_model is not None
        },
        'configuration': {
            'roberta_weight': ROBERTA_WEIGHT,
            'ml_weight': ML_WEIGHT,
            'ml_models_breakdown': MODEL_WEIGHTS
        }
    })


@app.route('/predict', methods=['POST'])
def predict():
    """Default prediction - uses ML only"""
    return predict_ml_endpoint()


@app.route('/predict-ml', methods=['POST'])
def predict_ml_endpoint():
    """Pure ML prediction endpoint"""
    if ml_models_loaded == 0 or not tfidf_vectorizer:
        return jsonify({'error': 'ML models not loaded'}), 500
    
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        result = predict_ml_only(text)
        final_prob = result['final_probability']
        is_ai = final_prob > 0.50
        
        confidence = 'High' if final_prob > 0.85 or final_prob < 0.15 else \
                    'Medium' if final_prob > 0.70 or final_prob < 0.30 else 'Low'
        
        print(f"\n[ML] Final: {final_prob:.4f} → {'AI' if is_ai else 'Human'}")
        
        return jsonify({
            'is_ai': bool(is_ai),
            'ai_probability': float(final_prob),
            'human_probability': float(1.0 - final_prob),
            'label': 'AI' if is_ai else 'Human',
            'confidence': confidence,
            'model_name': 'Pure ML Ensemble (SVM + AdaBoost + RF)',
            'mode': 'ml_only',
            'breakdown': result['probabilities']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/predict-hybrid', methods=['POST'])
def predict_hybrid_endpoint():
    """Hybrid ML + DL prediction endpoint"""
    if not roberta_model:
        return jsonify({'error': 'RoBERTa model not loaded'}), 500
    if ml_models_loaded == 0:
        return jsonify({'error': 'ML models not loaded'}), 500
    
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        result = predict_hybrid(text)
        final_prob = result['final_probability']
        is_ai = final_prob > 0.45
        
        confidence = 'High' if final_prob > 0.85 or final_prob < 0.15 else \
                    'Medium' if final_prob > 0.70 or final_prob < 0.30 else 'Low'
        
        print(f"\n[Hybrid] RoBERTa: {result['roberta_probability']:.4f} | ML: {result['ml_probability']:.4f} | Final: {final_prob:.4f}")
        
        return jsonify({
            'is_ai': bool(is_ai),
            'ai_probability': float(final_prob),
            'human_probability': float(1.0 - final_prob),
            'label': 'AI' if is_ai else 'Human',
            'confidence': confidence,
            'model_name': 'Hybrid Ensemble (RoBERTa + ML)',
            'mode': 'hybrid',
            'breakdown': {
                'roberta_prob': float(result['roberta_probability']),
                'ml_prob': float(result['ml_probability']),
                'ml_details': result['ml_breakdown']
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/predict-file', methods=['POST'])
def predict_file():
    """File prediction with mode selection"""
    mode = request.form.get('mode', 'ml')  # Default to ML
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    filename = secure_filename(file.filename)
    file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    if file_ext not in ['pdf', 'docx', 'doc']:
        return jsonify({'error': 'Only PDF and Word files supported'}), 400
    
    try:
        text = ''
        if file_ext == 'pdf':
            pdf_file = io.BytesIO(file.read())
            pdf_reader = PdfReader(pdf_file)
            for page in pdf_reader.pages:
                text += page.extract_text() + '\n'
        elif file_ext in ['docx', 'doc']:
            doc_file = io.BytesIO(file.read())
            doc = Document(doc_file)
            for paragraph in doc.paragraphs:
                text += paragraph.text + '\n'
        
        text = text.strip()
        if not text:
            return jsonify({'error': 'No text found in file'}), 400
        
        # Choose prediction mode
        if mode == 'hybrid' and roberta_model:
            result = predict_hybrid(text)
            model_name = 'Hybrid Ensemble (RoBERTa + ML)'
        else:
            result = predict_ml_only(text)
            model_name = 'Pure ML Ensemble (SVM + AdaBoost + RF)'
        
        final_prob = result['final_probability']
        is_ai = final_prob > 0.50 if mode == 'ml' else final_prob > 0.45
        
        confidence = 'High' if final_prob > 0.85 or final_prob < 0.15 else \
                    'Medium' if final_prob > 0.70 or final_prob < 0.30 else 'Low'
        
        return jsonify({
            'is_ai': bool(is_ai),
            'ai_probability': float(final_prob),
            'human_probability': float(1.0 - final_prob),
            'label': 'AI' if is_ai else 'Human',
            'confidence': confidence,
            'model_name': model_name,
            'mode': mode,
            'filename': filename,
            'file_type': file_ext.upper(),
            'text_length': len(text),
            'word_count': len(text.split()),
            'extracted_text': text
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'ml_models': ml_models_loaded,
        'dl_model': roberta_model is not None
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False, threaded=True)
