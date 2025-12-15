
import requests
import json

url = 'http://127.0.0.1:5000/predict'

texts = {
    "Evolution Essay Intro": """Evolution is one of the most profound and transformative concepts in the history of science. It explains the diversity of life on Earth, the shared ancestry of all organisms, and the biological processes that shape species over millions of years. Although most people associate evolution with Charles Darwin, the idea has roots that stretch far before him and scientific advancements that extend far beyond him. Today, evolution stands as the unifying framework of modern biology, integrating genetics, paleontology, ecology, geology, biochemistry, and many other fields into a comprehensive explanation of life’s complexity. Understanding evolution is essential not just for science students but for anyone who wishes to comprehend how living organisms—including humans—came to be."""
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
