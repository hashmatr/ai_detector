"""
Quick test to demonstrate the Hybrid Ensemble AI Detector
"""
import requests
import json

API_URL = "http://127.0.0.1:5000"

def test_prediction(text, description):
    print("\n" + "=" * 70)
    print(f"TEST: {description}")
    print("=" * 70)
    print(f"Text: {text[:100]}...")
    print()
    
    try:
        response = requests.post(f"{API_URL}/predict", json={"text": text})
        result = response.json()
        
        print(f"🎯 Result: {result['label']}")
        print(f"📊 AI Probability: {result['ai_probability']:.2%}")
        print(f"📊 Human Probability: {result['human_probability']:.2%}")
        print(f"🤖 Model: {result['model_name']}")
        
        if 'breakdown' in result and result['breakdown']:
            breakdown = result['breakdown']
            print(f"\n📈 Breakdown:")
            print(f"   RoBERTa: {breakdown['roberta_prob']:.2%} (weight: {breakdown['roberta_weight']:.0%})")
            if breakdown['ml_prob'] is not None:
                print(f"   ML Ensemble: {breakdown['ml_prob']:.2%} (weight: {breakdown['ml_weight']:.0%})")
        
    except Exception as e:
        print(f"❌ Error: {e}")

# Test 1: AI-generated text (ChatGPT style)
ai_text = """
Artificial intelligence has revolutionized numerous industries in recent years. 
From healthcare to finance, AI systems are increasingly being deployed to automate 
tasks, analyze data, and make predictions. Machine learning algorithms can process 
vast amounts of information far more quickly than humans, enabling organizations 
to gain insights that were previously impossible to obtain. As AI continues to 
advance, it is essential to consider both its potential benefits and the ethical 
implications of its widespread adoption.
"""

# Test 2: Human-written text (more casual, personal)
human_text = """
I went to the store yesterday and you won't believe what happened! The cashier 
was super friendly and we ended up chatting for like 10 minutes about our favorite 
TV shows. She recommended this new series on Netflix that I'd never heard of. 
I'm definitely gonna check it out this weekend. Also, they had a sale on ice cream 
so I grabbed like 3 tubs lol. My freezer is packed now but no regrets!
"""

# Test 3: Mixed/ambiguous text
mixed_text = """
The implementation of sustainable practices in modern business operations has 
become increasingly important. Companies are recognizing that environmental 
responsibility is not just good for the planet, but also beneficial for their 
bottom line. Many organizations have started implementing green initiatives, 
reducing waste, and optimizing resource usage.
"""

print("\n" + "🚀" * 35)
print("HYBRID ENSEMBLE AI DETECTOR - TEST SUITE")
print("🚀" * 35)

# Get model info
try:
    info = requests.get(f"{API_URL}/info").json()
    print(f"\n📋 Model Info:")
    print(f"   Name: {info['model_name']}")
    print(f"   Status: {info['status']}")
    print(f"   Type: {info['type']}")
    print(f"   RoBERTa Weight: {info['roberta_weight']:.0%}")
    print(f"   ML Weight: {info['ml_weight']:.0%}")
except Exception as e:
    print(f"⚠️  Could not fetch model info: {e}")

# Run tests
test_prediction(ai_text, "AI-Generated Text (ChatGPT style)")
test_prediction(human_text, "Human-Written Text (Casual)")
test_prediction(mixed_text, "Mixed/Ambiguous Text")

print("\n" + "=" * 70)
print("✅ TEST COMPLETE")
print("=" * 70)
print("\nThe hybrid ensemble combines:")
print("  • RoBERTa Transformer (85% weight) - Deep learning power")
print("  • ML Ensemble: RF + KNN (15% weight) - Your custom data patterns")
print("\nThis provides more accurate and robust AI detection!")
