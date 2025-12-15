
import joblib
import os
import sys
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import numpy as np

# Text samples provided by the user (ChatGPT generated)
texts = {
    "Meditation Paragraph (AI)": """Meditation offers a wide range of benefits that improve both mental and physical well-being. It helps reduce stress by calming the mind and lowering cortisol levels. Regular practice improves focus, attention, and emotional stability, allowing individuals to respond rather than react to challenges. Meditation also enhances self-awareness, helping people better understand their thoughts and feelings. It can improve sleep quality, reduce anxiety, and promote a sense of inner peace. Physically, meditation supports lower blood pressure and strengthens the immune system. Overall, it provides a simple yet powerful way to cultivate a healthier, more balanced, and more mindful lifestyle.""",
    
    "Evolution Essay Intro (AI)": """Evolution is one of the most profound and transformative concepts in the history of science. It explains the diversity of life on Earth, the shared ancestry of all organisms, and the biological processes that shape species over millions of years. Although most people associate evolution with Charles Darwin, the idea has roots that stretch far before him and scientific advancements that extend far beyond him. Today, evolution stands as the unifying framework of modern biology, integrating genetics, paleontology, ecology, geology, biochemistry, and many other fields into a comprehensive explanation of life’s complexity. Understanding evolution is essential not just for science students but for anyone who wishes to comprehend how living organisms—including humans—came to be."""
}

def predict_text():
    models_dir = r"e:\Machine Learning Project\ai_detector\Backend\Models"
    
    # 1. Try DistilBERT
    distilbert_path = os.path.join(models_dir, 'distilbert_model')
    if os.path.exists(distilbert_path):
        try:
            print("\n🔍 Testing with DEEP LEARNING MODEL (DistilBERT)...")
            tokenizer = DistilBertTokenizer.from_pretrained(os.path.join(models_dir, 'distilbert_tokenizer'))
            model = DistilBertForSequenceClassification.from_pretrained(distilbert_path)
            model.eval()
            
            for name, text in texts.items():
                inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
                with torch.no_grad():
                    logits = model(**inputs).logits
                probs = torch.softmax(logits, dim=1).numpy()[0]
                ai_prob = float(probs[1])
                
                print(f"\n📝 Text: {name}")
                print(f"   prediction: {'AI' if ai_prob > 0.5 else 'HUMAN'}")
                print(f"   Confidence: {ai_prob:.2%}")
            return
        except Exception as e:
            print(f"Error loading DistilBERT: {e}")

    # 2. Fallback to Sklearn
    print("\n🔍 Testing with BEST K-FOLD MODEL (Sklearn)...")
    try:
        model = joblib.load(os.path.join(models_dir, 'best_kfold_model.joblib'))
        vectorizer = joblib.load(os.path.join(models_dir, 'best_kfold_vectorizer.joblib'))
        
        for name, text in texts.items():
            text_vec = vectorizer.transform([text])
            
            if hasattr(model, 'predict_proba'):
                prob = model.predict_proba(text_vec)[0][1]
            else:
                prob = float(model.predict(text_vec)[0])
                
            print(f"\n📝 Text: {name}")
            print(f"   Prediction: {'AI' if prob > 0.5 else 'HUMAN'}")
            print(f"   Confidence: {prob:.2%}")
            
    except Exception as e:
        print(f"Error loading Sklearn model: {e}")

if __name__ == "__main__":
    predict_text()
