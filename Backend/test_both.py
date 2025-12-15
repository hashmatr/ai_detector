
import requests
import json

url = 'http://127.0.0.1:5000/predict'

texts = {
    "Meditation (AI)": """Meditation offers a wide range of benefits that improve both mental and physical well-being. It helps reduce stress by calming the mind and lowering cortisol levels. Regular practice improves focus, attention, and emotional stability, allowing individuals to respond rather than react to challenges. Meditation also enhances self-awareness, helping people better understand their thoughts and feelings.""",
    
    "Evolution (AI)": """Evolution is one of the most profound and transformative concepts in the history of science. It explains the diversity of life on Earth, the shared ancestry of all organisms, and the biological processes that shape species over millions of years."""
}

for name, text in texts.items():
    print(f"\nTesting {name}...")
    try:
        response = requests.post(url, json={'text': text})
        if response.status_code == 200:
            result = response.json()
            print(f"Result: {result}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")
