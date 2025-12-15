import requests

gemini_text = """Expansion (Enlargement): The push to integrate Western Balkan countries, Ukraine, and Moldova is not just a matter of economic inclusion but a profound geopolitical move to consolidate the democratic, liberal space of Europe against authoritarian influence."""

r = requests.post('http://127.0.0.1:5000/predict', json={'text': gemini_text})
result = r.json()

print("="*70)
print("FINAL TEST - GEMINI SAMPLE")
print("="*70)
print(f"\nLabel: {result['label']}")
print(f"AI Probability: {result['ai_probability']*100:.1f}%")
print(f"Human Probability: {result['human_probability']*100:.1f}%")
print("\n" + "="*70)

if result['label'] == 'AI' and result['ai_probability'] > 0.7:
    print("✅ SUCCESS! High confidence AI detection!")
elif result['label'] == 'AI':
    print("✓ Correctly identified as AI")
else:
    print("❌ Incorrectly identified")
print("="*70)
