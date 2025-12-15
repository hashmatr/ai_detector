"""
Use a pre-trained AI detector from HuggingFace
This model is trained on GPT-4, Claude, and other modern AI
"""
from transformers import pipeline
import torch

print("="*70)
print("LOADING PRE-TRAINED AI DETECTOR")
print("="*70)

print("\nLoading model (this may take a few minutes)...")

try:
    # Use a pre-trained AI detector
    # Options:
    # 1. "roberta-base-openai-detector" - OpenAI's detector
    # 2. "Hello-SimpleAI/chatgpt-detector-roberta" - ChatGPT detector
    
    detector = pipeline(
        "text-classification",
        model="Hello-SimpleAI/chatgpt-detector-roberta",
        device=0 if torch.cuda.is_available() else -1
    )
    
    print("✅ Model loaded successfully!")
    
    # Test on your Gemini sample
    gemini_text = """Expansion (Enlargement): The push to integrate Western Balkan countries, 
    Ukraine, and Moldova is not just a matter of economic inclusion but a profound geopolitical 
    move to consolidate the democratic, liberal space of Europe against authoritarian influence."""
    
    result = detector(gemini_text)
    print("\n" + "="*70)
    print("TEST ON GEMINI TEXT:")
    print("="*70)
    print(f"Result: {result}")
    
    # Test on human text
    human_text = """hey so i was thinking about what you said yesterday and honestly i dont 
    really agree lol. like yeah the movie was ok but it wasnt THAT good you know?"""
    
    result_human = detector(human_text)
    print("\n" + "="*70)
    print("TEST ON HUMAN TEXT:")
    print("="*70)
    print(f"Result: {result_human}")
    
    print("\n" + "="*70)
    print("SUCCESS! This model should work much better on modern AI.")
    print("To integrate this into your Flask app, update app.py")
    print("="*70)
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nMake sure you have installed:")
    print("pip install transformers torch")

