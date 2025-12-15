"""
Test the new modern AI model on various samples
"""
import requests
import json

API_URL = "http://127.0.0.1:5000/predict"

print("="*80)
print("TESTING NEW MODERN AI MODEL")
print("="*80)

test_cases = [
    {
        "name": "Your Gemini Sample (should be AI)",
        "text": """Expansion (Enlargement): The push to integrate Western Balkan countries, Ukraine, and Moldova is not just a matter of economic inclusion but a profound geopolitical move to consolidate the democratic, liberal space of Europe against authoritarian influence. This process will inevitably add complexity and divergence to the Union.

In conclusion, Europe's journey is a profound paradox: it is a land that invented the nation-state and the devastating ideology of total war, yet it simultaneously conceived of and successfully implemented a system designed to transcend both.""",
        "expected": "AI"
    },
    {
        "name": "Casual Human Text",
        "text": "hey so i was thinking about what you said yesterday and honestly i dont really agree lol. like yeah the movie was ok but it wasnt THAT good you know? anyway lets grab coffee tomorrow if ur free",
        "expected": "Human"
    },
    {
        "name": "Formal AI Text",
        "text": "The implementation of artificial intelligence systems into modern workflows necessitates careful consideration of both technical and ethical dimensions. Organizations must balance innovation with responsibility, ensuring that automated systems augment rather than replace human decision-making in critical contexts.",
        "expected": "AI"
    },
    {
        "name": "Informal Human Text",
        "text": "omg you won't believe what happened at work today!! my boss literally called a meeting just to tell us that we're getting new coffee machines 😂 like seriously that could've been an email",
        "expected": "Human"
    }
]

print("\nTesting predictions:\n")

for i, test in enumerate(test_cases, 1):
    print(f"[{i}/{len(test_cases)}] {test['name']}")
    print(f"Expected: {test['expected']}")
    
    try:
        response = requests.post(API_URL, json={"text": test['text']}, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            predicted = result['label']
            ai_prob = result['ai_probability']
            human_prob = result['human_probability']
            
            status = "✅" if predicted == test['expected'] else "❌"
            
            print(f"{status} Predicted: {predicted}")
            print(f"   Confidence: Human={human_prob:.1%}, AI={ai_prob:.1%}")
            
            if predicted == test['expected']:
                print(f"   🎉 CORRECT!")
            else:
                print(f"   ⚠️  WRONG - Expected {test['expected']}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running:")
        print("   python app.py")
        break
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()

print("="*80)
print("TEST COMPLETE")
print("="*80)
print("\nIf the Gemini sample is now detected as AI with >70% confidence,")
print("the model is working correctly!")
print("="*80)
