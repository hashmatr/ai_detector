from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os

app = Flask(__name__)
CORS(app)

# Global variables
model = None
tokenizer = None
model_name = "Hello-SimpleAI/chatgpt-detector-roberta"

print(f"Loading {model_name}...")
try:
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    print(f"✅ Loaded {model_name}")
except Exception as e:
    print(f"❌ Failed to load model: {e}")
    # Fallback to CPU if CUDA fails (though 'from_pretrained' handles auto device map usually, we stay simple)

@app.route('/info', methods=['GET'])
def get_info():
    return jsonify({
        'model_name': 'RoBERTa ChatGPT Detector (Pre-trained)',
        'status': 'active' if model else 'inactive',
        'type': 'transformer'
    })

@app.route('/predict', methods=['POST'])
def predict():
    if not model or not tokenizer:
        return jsonify({'error': 'Model not loaded'}), 500

    data = request.get_json()
    text = data.get('text', '')

    if not text:
        return jsonify({'error': 'No text provided'}), 400

    try:
        # Split text into chunks to catch AI content that might be hidden in long text
        # Simple splitting by periods or newlines, roughly preserving sentence structure
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 50] # Filter very short fragments
        
        # If no valid sentences found (e.g. short text), just use the whole text
        if not sentences:
            sentences = [text]
            
        # We also add the full text as one chunk to capture overall context
        if len(sentences) > 1:
            chunks = sentences + [text]
        else:
            chunks = sentences

        chunk_probs = []
        
        for chunk in chunks:
            # Tokenize
            inputs = tokenizer(chunk, return_tensors="pt", truncation=True, max_length=512)
            
            # Predict
            with torch.no_grad():
                outputs = model(**inputs)
                probs = F.softmax(outputs.logits, dim=-1)
                
                # Label 0: Human, Label 1: ChatGPT
                ai_p = float(probs[0][1])
                chunk_probs.append(ai_p)
        
        # Aggregation Strategy:
        # We calculate the average probability across all chunks to give a nuanced score.
        # This ensures the percentage reflects the *entire* text, not just one sentence.
        
        avg_ai_prob = sum(chunk_probs) / len(chunk_probs)
        
        # Calibration: Apply a slight boost to AI detection sensitivity
        # This helps detect AI content that might be scored lower than it should be
        calibration_factor = 1.35  # Moderate boost to AI probabilities
        calibrated_ai_prob = min(avg_ai_prob * calibration_factor, 1.0)
        
        # Decision logic: Slightly lower threshold for better AI detection
        is_ai = calibrated_ai_prob > 0.45
        
        print(f"DEBUG: Chunks: {len(chunks)}, Raw AI: {avg_ai_prob:.4f}, Calibrated AI: {calibrated_ai_prob:.4f}")
        
        result = {
            'is_ai': is_ai,
            'ai_probability': calibrated_ai_prob,
            'human_probability': 1.0 - calibrated_ai_prob,
            'label': 'AI' if is_ai else 'Human',
            'model_name': 'RoBERTa ChatGPT Detector (Balanced)'
        }
        
        print(f"Prediction: {result['label']} (AI: {calibrated_ai_prob:.2%})")
        return jsonify(result)
        
    except Exception as e:
        import traceback
        print("ERROR:", str(e))
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
