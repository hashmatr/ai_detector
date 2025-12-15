import requests

print("="*70)
print("TESTING YOUR GEMINI SAMPLE")
print("="*70)

gemini_text = """Expansion (Enlargement): The push to integrate Western Balkan countries, Ukraine, and Moldova is not just a matter of economic inclusion but a profound geopolitical move to consolidate the democratic, liberal space of Europe against authoritarian influence. This process will inevitably add complexity and divergence to the Union.

In conclusion, Europe's journey is a profound paradox: it is a land that invented the nation-state and the devastating ideology of total war, yet it simultaneously conceived of and successfully implemented a system designed to transcend both."""

try:
    response = requests.post('http://127.0.0.1:5000/predict', json={'text': gemini_text})
    result = response.json()
    
    print("\nYour Gemini Text:")
    print(gemini_text[:150] + "...")
    
    print("\n" + "="*70)
    print("PREDICTION RESULT:")
    print("="*70)
    print(f"Label: {result['label']}")
    print(f"AI Probability: {result['ai_probability']*100:.1f}%")
    print(f"Human Probability: {result['human_probability']*100:.1f}%")
    
    if result['label'] == 'AI' and result['ai_probability'] > 0.7:
        print("\n✅ SUCCESS! Correctly identified as AI with high confidence!")
        print("The new model is working perfectly!")
    elif result['label'] == 'AI':
        print("\n⚠️  Identified as AI but with low confidence")
        print("May need more training data")
    else:
        print("\n❌ Incorrectly identified as Human")
        print("The model needs more training")
    
    print("="*70)
    
except Exception as e:
    print(f"Error: {e}")
