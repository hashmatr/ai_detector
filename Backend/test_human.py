
import requests
import json

url = 'http://127.0.0.1:5000/predict'

texts = {
    "Simple Human Sentence": "I am writing this text right now to test if the ai detector works correctly.",
    "Classic Literature (Pride and Prejudice)": "It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife. However little known the feelings or views of such a man may be on his first entering a neighbourhood, this truth is so well fixed in the minds of the surrounding families, that he is considered the rightful property of some one or other of their daughters.",
    "Technical Documentation (Likely Human)": "To install the package, run the following command in your terminal. Ensure that you have Python 3.8 or higher installed on your system."
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
