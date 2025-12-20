from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
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

# RoBERTa Model
roberta_model = None
roberta_tokenizer = None
roberta_model_name = "Hello-SimpleAI/chatgpt-detector-roberta"
using_finetuned_model = False  # Flag to track which model is loaded

# Fine-tuned model paths (will be used if available)
FINETUNED_MODEL_PATH = os.path.join(os.path.dirname(__file__), "Models", "roberta_finetuned")
FINETUNED_TOKENIZER_PATH = os.path.join(os.path.dirname(__file__), "Models", "roberta_finetuned_tokenizer")

# ML Ensemble Models
ml_ensemble = None
ml_scaler = None
ml_tfidf = None

# Weights for ensemble combination
ROBERTA_WEIGHT = 0.70  # RoBERTa gets 70% weight
ML_WEIGHT = 0.30       # ML models get 30% weight

# ===========================
# FEATURE EXTRACTION
# ===========================

def extract_text_features(text):
    """Extract linguistic features from text"""
    if not isinstance(text, str):
        text = str(text)
    
    words = text.split()
    word_count = len(words)
    
    features = {
        'text_length': len(text),
        'word_count': word_count,
        'avg_word_length': np.mean([len(w) for w in words]) if words else 0,
        'unique_word_ratio': len(set(words)) / word_count if word_count > 0 else 0,
        'upper_case_ratio': sum(1 for c in text if c.isupper()) / len(text) if text else 0,
        'digit_freq': sum(1 for c in text if c.isdigit()) / len(text) if text else 0,
        'punc_freq': sum(1 for c in text if c in '.,!?;:') / len(text) if text else 0,
        'exclamation_count': text.count('!'),
        'question_count': text.count('?'),
        'comma_count': text.count(','),
        'period_count': text.count('.'),
        'avg_sentence_length': word_count / max(text.count('.') + text.count('!') + text.count('?'), 1),
    }
    return features

# ===========================
# LOAD MODELS
# ===========================

print("=" * 60)
print("LOADING AI DETECTION MODELS")
print("=" * 60)

# Load RoBERTa - Try fine-tuned first, then fall back to pre-trained
print(f"\n📚 Loading RoBERTa Model...")

# Check if fine-tuned model exists
if os.path.exists(FINETUNED_MODEL_PATH) and os.path.exists(FINETUNED_TOKENIZER_PATH):
    print(f"   🎯 Found fine-tuned model at: {FINETUNED_MODEL_PATH}")
    try:
        roberta_tokenizer = AutoTokenizer.from_pretrained(FINETUNED_TOKENIZER_PATH)
        roberta_model = AutoModelForSequenceClassification.from_pretrained(FINETUNED_MODEL_PATH)
        using_finetuned_model = True
        print(f"   ✅ Fine-tuned RoBERTa loaded successfully!")
        print(f"   📊 This model was trained on YOUR dataset")
        
        # Try to load training info
        training_info_path = os.path.join(FINETUNED_MODEL_PATH, "training_info.json")
        if not os.path.exists(training_info_path):
            training_info_path = os.path.join(os.path.dirname(__file__), "Models", "training_info.json")
        
        if os.path.exists(training_info_path):
            import json
            with open(training_info_path, 'r') as f:
                info = json.load(f)
            if 'final_metrics' in info:
                metrics = info['final_metrics']
                print(f"   📈 Training Accuracy: {metrics.get('accuracy', 'N/A'):.2%}")
                print(f"   📈 Training F1-Score: {metrics.get('f1_score', 'N/A'):.2%}")
    except Exception as e:
        print(f"   ⚠️  Failed to load fine-tuned model: {e}")
        print(f"   📥 Falling back to pre-trained model...")
        using_finetuned_model = False

# Fall back to pre-trained model if fine-tuned not available or failed
if not using_finetuned_model:
    print(f"   📥 Loading pre-trained: {roberta_model_name}")
    try:
        roberta_tokenizer = AutoTokenizer.from_pretrained(roberta_model_name)
        roberta_model = AutoModelForSequenceClassification.from_pretrained(roberta_model_name)
        print(f"   ✅ Pre-trained RoBERTa loaded successfully")
    except Exception as e:
        print(f"   ❌ Failed to load RoBERTa: {e}")

# Load ML Ensemble
models_dir = os.path.join(os.path.dirname(__file__), "Models")
ensemble_path = os.path.join(models_dir, "ml_ensemble_model.joblib")
scaler_path = os.path.join(models_dir, "ml_ensemble_scaler.joblib")
tfidf_path = os.path.join(models_dir, "ml_ensemble_tfidf.joblib")

print(f"\n📚 Loading ML Ensemble (Random Forest + KNN)...")
try:
    if os.path.exists(ensemble_path) and os.path.exists(scaler_path) and os.path.exists(tfidf_path):
        ml_ensemble = joblib.load(ensemble_path)
        ml_scaler = joblib.load(scaler_path)
        ml_tfidf = joblib.load(tfidf_path)
        print(f"   ✅ ML Ensemble loaded successfully")
    else:
        print(f"   ⚠️  ML Ensemble not found. Run train_ensemble_all_data.py first.")
        print(f"   Will use RoBERTa only.")
except Exception as e:
    print(f"   ⚠️  Failed to load ML Ensemble: {e}")
    print(f"   Will use RoBERTa only.")

print("\n" + "=" * 60)
print(f"MODELS LOADED - RoBERTa Weight: {ROBERTA_WEIGHT:.0%}, ML Weight: {ML_WEIGHT:.0%}")
print("=" * 60 + "\n")

# ===========================
# ROUTES
# ===========================

@app.route('/info', methods=['GET'])
def get_info():
    models_active = []
    if roberta_model:
        if using_finetuned_model:
            models_active.append('RoBERTa (Fine-tuned)')
        else:
            models_active.append('RoBERTa (Pre-trained)')
    if ml_ensemble:
        models_active.append('ML Ensemble (RF+KNN)')
    
    return jsonify({
        'model_name': f'Hybrid Ensemble: {" + ".join(models_active)}',
        'status': 'active' if roberta_model else 'inactive',
        'type': 'hybrid_transformer_ml',
        'roberta_weight': ROBERTA_WEIGHT,
        'ml_weight': ML_WEIGHT if ml_ensemble else 0,
        'using_finetuned_model': using_finetuned_model,
        'finetuned_model_path': FINETUNED_MODEL_PATH if using_finetuned_model else None
    })

@app.route('/predict', methods=['POST'])
def predict():
    if not roberta_model or not roberta_tokenizer:
        return jsonify({'error': 'RoBERTa model not loaded'}), 500

    data = request.get_json()
    text = data.get('text', '')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        # ===========================
        # 1️⃣ RoBERTa Prediction
        # ===========================
        
        # Split text into chunks
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
        
        avg_ai_prob = sum(chunk_probs) / len(chunk_probs)
        
        # Apply calibration
        calibration_factor = 1.35
        roberta_ai_prob = min(avg_ai_prob * calibration_factor, 1.0)
        
        print(f"🤖 RoBERTa: Raw={avg_ai_prob:.4f}, Calibrated={roberta_ai_prob:.4f}")
        
        # ===========================
        # 2️⃣ ML Ensemble Prediction
        # ===========================
        
        ml_ai_prob = 0.5  # Default neutral if ML not available
        
        if ml_ensemble and ml_scaler and ml_tfidf:
            try:
                # Extract features
                feature_dict = extract_text_features(text)
                feature_df = pd.DataFrame([feature_dict])
                
                # TF-IDF features
                tfidf_features = ml_tfidf.transform([text]).toarray()
                tfidf_df = pd.DataFrame(tfidf_features, columns=[f'tfidf_{i}' for i in range(tfidf_features.shape[1])])
                
                # Combine features
                X = pd.concat([feature_df, tfidf_df], axis=1)
                
                # Scale
                X_scaled = ml_scaler.transform(X)
                
                # Predict
                ml_ai_prob = ml_ensemble.predict_proba(X_scaled)[0][1]
                
                print(f"🔬 ML Ensemble: {ml_ai_prob:.4f}")
                
            except Exception as e:
                print(f"⚠️  ML prediction failed: {e}")
                ml_ai_prob = 0.5  # Neutral fallback
        
        # ===========================
        # 3️⃣ Combine Predictions
        # ===========================
        
        # Weighted average
        if ml_ensemble:
            final_ai_prob = (ROBERTA_WEIGHT * roberta_ai_prob) + (ML_WEIGHT * ml_ai_prob)
            model_name = 'Hybrid Ensemble (RoBERTa + RF + KNN)'
        else:
            final_ai_prob = roberta_ai_prob
            model_name = 'RoBERTa ChatGPT Detector'
        
        # Decision threshold
        is_ai = final_ai_prob > 0.45
        
        print(f"🎯 Final: {final_ai_prob:.4f} → {'AI' if is_ai else 'Human'}")
        print("-" * 60)
        
        result = {
            'is_ai': bool(is_ai),
            'ai_probability': float(final_ai_prob),
            'human_probability': float(1.0 - final_ai_prob),
            'label': 'AI' if is_ai else 'Human',
            'model_name': model_name,
            'breakdown': {
                'roberta_prob': float(roberta_ai_prob),
                'ml_prob': float(ml_ai_prob) if ml_ensemble else None,
                'roberta_weight': float(ROBERTA_WEIGHT),
                'ml_weight': float(ML_WEIGHT) if ml_ensemble else 0.0
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        import traceback
        print("ERROR:", str(e))
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@app.route('/predict-file', methods=['POST'])
def predict_file():
    """Predict AI content from uploaded Word or PDF file"""
    if not roberta_model or not roberta_tokenizer:
        return jsonify({'error': 'RoBERTa model not loaded'}), 500
    
    # Check if file is present
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Get file extension
    filename = secure_filename(file.filename)
    file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    if file_ext not in ['pdf', 'docx', 'doc']:
        return jsonify({'error': 'Only PDF and Word (.docx, .doc) files are supported'}), 400
    
    try:
        # Extract text based on file type
        text = ''
        
        if file_ext == 'pdf':
            # Read PDF
            pdf_file = io.BytesIO(file.read())
            pdf_reader = PdfReader(pdf_file)
            
            # Extract text from all pages
            for page in pdf_reader.pages:
                text += page.extract_text() + '\n'
        
        elif file_ext in ['docx', 'doc']:
            # Read Word document
            doc_file = io.BytesIO(file.read())
            doc = Document(doc_file)
            
            # Extract text from all paragraphs
            for paragraph in doc.paragraphs:
                text += paragraph.text + '\n'
        
        # Clean up text
        text = text.strip()
        
        if not text:
            return jsonify({'error': 'No text found in the file'}), 400
        
        # Use the same prediction logic as /predict endpoint
        # ===========================
        # 1️⃣ RoBERTa Prediction
        # ===========================
        
        # Split text into chunks
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
        
        avg_ai_prob = sum(chunk_probs) / len(chunk_probs)
        
        # Apply calibration
        calibration_factor = 1.35
        roberta_ai_prob = min(avg_ai_prob * calibration_factor, 1.0)
        
        print(f"🤖 RoBERTa (File): Raw={avg_ai_prob:.4f}, Calibrated={roberta_ai_prob:.4f}")
        
        # ===========================
        # 2️⃣ ML Ensemble Prediction
        # ===========================
        
        ml_ai_prob = 0.5  # Default neutral if ML not available
        
        if ml_ensemble and ml_scaler and ml_tfidf:
            try:
                # Extract features
                feature_dict = extract_text_features(text)
                feature_df = pd.DataFrame([feature_dict])
                
                # TF-IDF features
                tfidf_features = ml_tfidf.transform([text]).toarray()
                tfidf_df = pd.DataFrame(tfidf_features, columns=[f'tfidf_{i}' for i in range(tfidf_features.shape[1])])
                
                # Combine features
                X = pd.concat([feature_df, tfidf_df], axis=1)
                
                # Scale
                X_scaled = ml_scaler.transform(X)
                
                # Predict
                ml_ai_prob = ml_ensemble.predict_proba(X_scaled)[0][1]
                
                print(f"🔬 ML Ensemble (File): {ml_ai_prob:.4f}")
                
            except Exception as e:
                print(f"⚠️  ML prediction failed: {e}")
                ml_ai_prob = 0.5  # Neutral fallback
        
        # ===========================
        # 3️⃣ Combine Predictions
        # ===========================
        
        # Weighted average
        if ml_ensemble:
            final_ai_prob = (ROBERTA_WEIGHT * roberta_ai_prob) + (ML_WEIGHT * ml_ai_prob)
            model_name = 'Hybrid Ensemble (RoBERTa + RF + KNN)'
        else:
            final_ai_prob = roberta_ai_prob
            model_name = 'RoBERTa ChatGPT Detector'
        
        # Decision threshold
        is_ai = final_ai_prob > 0.45
        
        print(f"🎯 Final (File): {final_ai_prob:.4f} → {'AI' if is_ai else 'Human'}")
        print(f"📄 File: {filename} ({file_ext.upper()})")
        print("-" * 60)
        
        result = {
            'is_ai': bool(is_ai),
            'ai_probability': float(final_ai_prob),
            'human_probability': float(1.0 - final_ai_prob),
            'label': 'AI' if is_ai else 'Human',
            'model_name': model_name,
            'filename': filename,
            'file_type': file_ext.upper(),
            'text_length': len(text),
            'word_count': len(text.split()),
            'extracted_text': text,  # Return the extracted text for highlighting
            'breakdown': {
                'roberta_prob': float(roberta_ai_prob),
                'ml_prob': float(ml_ai_prob) if ml_ensemble else None,
                'roberta_weight': float(ROBERTA_WEIGHT),
                'ml_weight': float(ML_WEIGHT) if ml_ensemble else 0.0
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        import traceback
        print("ERROR (File Upload):", str(e))
        print(traceback.format_exc())
        return jsonify({'error': f'Failed to process file: {str(e)}'}), 500

if __name__ == '__main__':
    # Disable reloader to prevent connection resets during file uploads
    app.run(debug=True, port=5000, use_reloader=False, threaded=True)
