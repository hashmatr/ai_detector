
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import torch.nn.functional as F

def test_pretrained():
    model_name = "Hello-SimpleAI/chatgpt-detector-roberta"
    print(f"Downloading/Loading {model_name}...")
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        
        texts = [
            """Meditation offers a wide range of benefits that improve both mental and physical well-being. It helps reduce stress by calming the mind and lowering cortisol levels. Regular practice improves focus, attention, and emotional stability, allowing individuals to respond rather than react to challenges. Meditation also enhances self-awareness, helping people better understand their thoughts and feelings.""",
            """Evolution is one of the most profound and transformative concepts in the history of science. It explains the diversity of life on Earth, the shared ancestry of all organisms, and the biological processes that shape species over millions of years."""
        ]
        
        print("\nTesting...")
        for text in texts:
            inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
            with torch.no_grad():
                outputs = model(**inputs)
                probs = F.softmax(outputs.logits, dim=-1)
                
            print(f"\nText snippet: {text[:50]}...")
            print(f"Logits: {outputs.logits}")
            print(f"Probabilities: {probs}")
            
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test_pretrained()
