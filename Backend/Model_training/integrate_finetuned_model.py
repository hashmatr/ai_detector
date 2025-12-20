"""
Script to integrate the fine-tuned RoBERTa model into your AI Detector backend.

This script:
1. Checks if the fine-tuned model exists
2. Validates the model files
3. Updates the backend to use the fine-tuned model

Run this after downloading the model from Google Colab.
"""

import os
import sys
import json
import shutil

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(BASE_DIR)  # Go up from Model_training to Backend
MODELS_DIR = os.path.join(BACKEND_DIR, "Models")

# Expected model paths
FINETUNED_MODEL_PATH = os.path.join(MODELS_DIR, "roberta_finetuned")
FINETUNED_TOKENIZER_PATH = os.path.join(MODELS_DIR, "roberta_finetuned_tokenizer")

# Required files for the model to work
REQUIRED_MODEL_FILES = ['config.json']
REQUIRED_TOKENIZER_FILES = ['tokenizer.json', 'vocab.json']


def check_model_exists():
    """Check if fine-tuned model files exist"""
    print("=" * 60)
    print("🔍 CHECKING FINE-TUNED MODEL FILES")
    print("=" * 60)
    
    model_exists = os.path.exists(FINETUNED_MODEL_PATH)
    tokenizer_exists = os.path.exists(FINETUNED_TOKENIZER_PATH)
    
    print(f"\n📁 Model path: {FINETUNED_MODEL_PATH}")
    print(f"   Exists: {'✅ Yes' if model_exists else '❌ No'}")
    
    print(f"\n📁 Tokenizer path: {FINETUNED_TOKENIZER_PATH}")
    print(f"   Exists: {'✅ Yes' if tokenizer_exists else '❌ No'}")
    
    return model_exists and tokenizer_exists


def validate_model_files():
    """Validate that all required model files are present"""
    print("\n" + "=" * 60)
    print("🔬 VALIDATING MODEL FILES")
    print("=" * 60)
    
    all_valid = True
    
    # Check model files
    print(f"\n📦 Model directory contents:")
    if os.path.exists(FINETUNED_MODEL_PATH):
        model_files = os.listdir(FINETUNED_MODEL_PATH)
        for f in model_files:
            file_path = os.path.join(FINETUNED_MODEL_PATH, f)
            size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            print(f"   - {f} ({size:.2f} MB)")
        
        # Check required files
        for req_file in REQUIRED_MODEL_FILES:
            if req_file not in model_files:
                print(f"   ⚠️  Missing required file: {req_file}")
                all_valid = False
        
        # Check for at least one model weights file
        weight_files = [f for f in model_files if 'model' in f.lower() or 'pytorch' in f.lower() or 'safetensors' in f.lower()]
        if not weight_files:
            print(f"   ⚠️  No model weights file found!")
            all_valid = False
    else:
        print(f"   ❌ Directory not found!")
        all_valid = False
    
    # Check tokenizer files
    print(f"\n📦 Tokenizer directory contents:")
    if os.path.exists(FINETUNED_TOKENIZER_PATH):
        tokenizer_files = os.listdir(FINETUNED_TOKENIZER_PATH)
        for f in tokenizer_files:
            file_path = os.path.join(FINETUNED_TOKENIZER_PATH, f)
            size = os.path.getsize(file_path) / 1024  # KB
            print(f"   - {f} ({size:.2f} KB)")
        
        # Check required tokenizer files
        for req_file in REQUIRED_TOKENIZER_FILES:
            if req_file not in tokenizer_files:
                # Some files might have different names
                print(f"   ℹ️  Note: {req_file} not found (may use alternative format)")
    else:
        print(f"   ❌ Directory not found!")
        all_valid = False
    
    return all_valid


def load_training_info():
    """Load and display training info if available"""
    training_info_path = os.path.join(MODELS_DIR, "roberta_finetuned", "training_info.json")
    
    if not os.path.exists(training_info_path):
        training_info_path = os.path.join(MODELS_DIR, "training_info.json")
    
    if os.path.exists(training_info_path):
        print("\n" + "=" * 60)
        print("📊 TRAINING INFORMATION")
        print("=" * 60)
        
        with open(training_info_path, 'r') as f:
            info = json.load(f)
        
        if 'final_metrics' in info:
            metrics = info['final_metrics']
            print(f"\n🎯 Final Metrics:")
            print(f"   Accuracy:  {metrics.get('accuracy', 'N/A'):.4f}")
            print(f"   F1-Score:  {metrics.get('f1_score', 'N/A'):.4f}")
            print(f"   Best F1:   {metrics.get('best_f1', 'N/A'):.4f}")
        
        if 'training_samples' in info:
            print(f"\n📈 Training Data:")
            print(f"   Training samples: {info.get('training_samples', 'N/A'):,}")
            print(f"   Test samples:     {info.get('test_samples', 'N/A'):,}")
            print(f"   Total samples:    {info.get('total_samples', 'N/A'):,}")
        
        if 'config' in info:
            config = info['config']
            print(f"\n⚙️  Training Config:")
            print(f"   Epochs:        {config.get('epochs', 'N/A')}")
            print(f"   Batch size:    {config.get('batch_size', 'N/A')}")
            print(f"   Learning rate: {config.get('learning_rate', 'N/A')}")
        
        return info
    
    return None


def test_model_loading():
    """Test if the model can be loaded successfully"""
    print("\n" + "=" * 60)
    print("🧪 TESTING MODEL LOADING")
    print("=" * 60)
    
    try:
        print("\n📦 Importing transformers...")
        from transformers import RobertaTokenizer, RobertaForSequenceClassification
        import torch
        
        print("📥 Loading tokenizer...")
        tokenizer = RobertaTokenizer.from_pretrained(FINETUNED_TOKENIZER_PATH)
        print("   ✅ Tokenizer loaded!")
        
        print("📥 Loading model...")
        model = RobertaForSequenceClassification.from_pretrained(FINETUNED_MODEL_PATH)
        print("   ✅ Model loaded!")
        
        print("\n🔬 Testing inference...")
        test_text = "This is a test sentence to verify the model works correctly."
        
        inputs = tokenizer(test_text, return_tensors="pt", truncation=True, max_length=512)
        
        with torch.no_grad():
            outputs = model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)
            human_prob = float(probs[0][0])
            ai_prob = float(probs[0][1])
        
        print(f"   Test text: \"{test_text[:50]}...\"")
        print(f"   Human probability: {human_prob:.4f}")
        print(f"   AI probability:    {ai_prob:.4f}")
        print("   ✅ Inference successful!")
        
        return True
        
    except Exception as e:
        print(f"\n   ❌ Error loading model: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_instructions():
    """Print instructions for using the model"""
    print("\n" + "=" * 60)
    print("📋 NEXT STEPS")
    print("=" * 60)
    
    print("""
To use the fine-tuned model in your backend:

1. The backend (app.py) is already configured to automatically
   detect and use the fine-tuned model if it exists.

2. Simply restart your Flask server:
   
   cd Backend
   python app.py

3. The server will show which model is being used:
   - "Fine-tuned RoBERTa" if using your trained model
   - "Hello-SimpleAI/chatgpt-detector-roberta" if using pre-trained

4. Test the API:
   
   curl -X POST http://localhost:5000/predict \\
     -H "Content-Type: application/json" \\
     -d '{"text": "Your test text here"}'
""")


def main():
    print("\n" + "🚀" * 30)
    print("\n  FINE-TUNED MODEL INTEGRATION CHECKER")
    print("\n" + "🚀" * 30)
    
    # Step 1: Check if model exists
    exists = check_model_exists()
    
    if not exists:
        print("\n" + "⚠️" * 30)
        print("\n❌ FINE-TUNED MODEL NOT FOUND!")
        print("\nPlease complete these steps first:")
        print("1. Train the model on Google Colab using RoBERTa_Colab_Training.ipynb")
        print("2. Download the trained model files")
        print("3. Copy files to:")
        print(f"   - {FINETUNED_MODEL_PATH}")
        print(f"   - {FINETUNED_TOKENIZER_PATH}")
        print("\n" + "⚠️" * 30)
        return False
    
    # Step 2: Validate files
    valid = validate_model_files()
    
    if not valid:
        print("\n⚠️  Some model files may be missing. The model might not load correctly.")
    
    # Step 3: Load training info
    load_training_info()
    
    # Step 4: Test loading
    success = test_model_loading()
    
    if success:
        print("\n" + "✅" * 30)
        print("\n✅ MODEL INTEGRATION SUCCESSFUL!")
        print("   Your fine-tuned model is ready to use!")
        print("\n" + "✅" * 30)
        
        print_instructions()
        return True
    else:
        print("\n" + "❌" * 30)
        print("\n❌ MODEL INTEGRATION FAILED!")
        print("   Please check the error messages above.")
        print("\n" + "❌" * 30)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
