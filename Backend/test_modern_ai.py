"""
Test the current model on modern AI text vs human text
"""
import joblib
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
model = joblib.load(os.path.join(base_dir, "Models/tfidf_model.joblib"))
vectorizer = joblib.load(os.path.join(base_dir, "Models/word_vectorizer.joblib"))

print("="*80)
print("TESTING MODEL ON MODERN AI vs HUMAN TEXT")
print("="*80)

# Modern AI text (Gemini, GPT-4, Claude)
modern_ai_samples = [
    """The European Union remains a historical experiment, one that constantly struggles 
    to balance the deep, cultural pull of national identity with the pragmatic, economic, 
    and security necessity of continental unity. Its success is measured not in the 
    perfection of its institutions, but in its ability to adapt and survive the crises 
    that have defined and challenged its existence since the coal and steel of its first 
    foundation.""",
    
    """In conclusion, the analysis demonstrates that the proposed methodology yields 
    significant improvements over existing approaches. Furthermore, it is important to 
    note that the aforementioned considerations necessitate a comprehensive evaluation 
    of the underlying mechanisms.""",
    
    """The integration of artificial intelligence systems into modern workflows requires 
    careful consideration of both technical and ethical dimensions. Organizations must 
    balance innovation with responsibility, ensuring that automated systems augment 
    rather than replace human decision-making in critical contexts."""
]

# Actual human text (casual, informal, with errors)
human_samples = [
    """hey so i was thinking about what you said yesterday and honestly i dont really 
    agree lol. like yeah the movie was ok but it wasnt THAT good you know? anyway lets 
    grab coffee tomorrow if ur free""",
    
    """I went to the store yesterday and it was packed! Couldn't believe how many people 
    were there. Got what I needed though - milk, eggs, bread, the usual stuff. Oh and 
    I ran into Sarah, haven't seen her in forever. We should all hang out soon.""",
    
    """So basically what happened was my car broke down on the highway. Total nightmare. 
    Had to wait like 2 hours for the tow truck. But the mechanic said it's just the 
    battery so not too expensive to fix thank god."""
]

print("\n" + "="*80)
print("MODERN AI TEXT (Should predict ~90%+ AI):")
print("="*80)

for i, text in enumerate(modern_ai_samples, 1):
    text_vec = vectorizer.transform([text])
    proba = model.predict_proba(text_vec)[0]
    prediction = "AI" if proba[1] > 0.5 else "HUMAN"
    
    status = "✅" if proba[1] > 0.7 else "⚠️" if proba[1] > 0.5 else "❌"
    
    print(f"\n{status} Sample {i}: Predicted {prediction}")
    print(f"   Confidence: Human={proba[0]:.1%}, AI={proba[1]:.1%}")
    print(f"   Text: {text[:100]}...")

print("\n" + "="*80)
print("HUMAN TEXT (Should predict ~90%+ Human):")
print("="*80)

for i, text in enumerate(human_samples, 1):
    text_vec = vectorizer.transform([text])
    proba = model.predict_proba(text_vec)[0]
    prediction = "AI" if proba[1] > 0.5 else "HUMAN"
    
    status = "✅" if proba[0] > 0.7 else "⚠️" if proba[0] > 0.5 else "❌"
    
    print(f"\n{status} Sample {i}: Predicted {prediction}")
    print(f"   Confidence: Human={proba[0]:.1%}, AI={proba[1]:.1%}")
    print(f"   Text: {text[:100]}...")

print("\n" + "="*80)
print("YOUR GEMINI SAMPLE:")
print("="*80)

gemini_text = """Expansion (Enlargement): The push to integrate Western Balkan countries, Ukraine, and Moldova is not just a matter of economic inclusion but a profound geopolitical move to consolidate the democratic, liberal space of Europe against authoritarian influence. This process will inevitably add complexity and divergence to the Union.

In conclusion, Europe's journey is a profound paradox: it is a land that invented the nation-state and the devastating ideology of total war, yet it simultaneously conceived of and successfully implemented a system designed to transcend both."""

text_vec = vectorizer.transform([gemini_text])
proba = model.predict_proba(text_vec)[0]
prediction = "AI" if proba[1] > 0.5 else "HUMAN"

print(f"\nPredicted: {prediction}")
print(f"Confidence: Human={proba[0]:.1%}, AI={proba[1]:.1%}")

if proba[1] < 0.8:
    print("\n⚠️  ISSUE: Model has low confidence on modern AI text!")
    print("This suggests the training data contains older AI models (GPT-2/3)")
    print("and doesn't recognize modern AI patterns (GPT-4/Gemini/Claude).")

print("\n" + "="*80)
print("DIAGNOSIS:")
print("="*80)
print("""
The model was trained on data from 2020-2022 era AI models.
Modern AI (2023-2024) like GPT-4, Gemini, and Claude:
- Use more natural language
- Have better coherence
- Mimic human writing patterns better
- Include intentional imperfections

SOLUTION: You need training data that includes modern AI samples.
""")
print("="*80)
