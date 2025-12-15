"""
Test script to verify the /predict-file endpoint is working correctly
"""
import requests
import os

# Test configuration
BACKEND_URL = "http://localhost:5000"
TEST_FILE_PATH = "test_document.txt"  # You can change this to your test file

def create_test_file():
    """Create a simple test text file if it doesn't exist"""
    if not os.path.exists(TEST_FILE_PATH):
        with open(TEST_FILE_PATH, 'w', encoding='utf-8') as f:
            f.write("""
Furthermore, the implementation of artificial intelligence in modern 
applications has revolutionized the way we approach complex problems. 
It is important to note that machine learning algorithms can leverage 
vast amounts of data to optimize decision-making processes. Moreover, 
the integration of neural networks has facilitated unprecedented 
advancements in natural language processing. Consequently, these 
cutting-edge technologies have transformed various industries, 
demonstrating remarkable capabilities in pattern recognition and 
predictive analytics. Additionally, the deployment of deep learning 
models has enabled sophisticated automation across numerous sectors.
            """)
        print(f"✅ Created test file: {TEST_FILE_PATH}")
    return TEST_FILE_PATH

def test_info_endpoint():
    """Test the /info endpoint"""
    print("\n" + "="*60)
    print("Testing /info endpoint...")
    print("="*60)
    
    try:
        response = requests.get(f"{BACKEND_URL}/info")
        if response.status_code == 200:
            data = response.json()
            print("✅ /info endpoint working!")
            print(f"   Model: {data.get('model_name')}")
            print(f"   Status: {data.get('status')}")
            print(f"   Type: {data.get('type')}")
            return True
        else:
            print(f"❌ /info endpoint failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error connecting to backend: {e}")
        print("   Make sure the backend is running on http://localhost:5000")
        return False

def test_predict_endpoint():
    """Test the /predict endpoint with text"""
    print("\n" + "="*60)
    print("Testing /predict endpoint...")
    print("="*60)
    
    test_text = """
    Furthermore, the implementation of artificial intelligence in modern 
    applications has revolutionized the way we approach complex problems.
    It is important to note that machine learning algorithms can leverage 
    vast amounts of data to optimize decision-making processes.
    """
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/predict",
            json={"text": test_text}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ /predict endpoint working!")
            print(f"   Label: {data.get('label')}")
            print(f"   AI Probability: {data.get('ai_probability', 0)*100:.1f}%")
            print(f"   Human Probability: {data.get('human_probability', 0)*100:.1f}%")
            return True
        else:
            print(f"❌ /predict endpoint failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_file_upload_endpoint(file_path):
    """Test the /predict-file endpoint"""
    print("\n" + "="*60)
    print("Testing /predict-file endpoint...")
    print("="*60)
    
    if not os.path.exists(file_path):
        print(f"❌ Test file not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f, 'text/plain')}
            response = requests.post(
                f"{BACKEND_URL}/predict-file",
                files=files
            )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ /predict-file endpoint working!")
            print(f"   Filename: {data.get('filename')}")
            print(f"   File Type: {data.get('file_type')}")
            print(f"   Word Count: {data.get('word_count')}")
            print(f"   Label: {data.get('label')}")
            print(f"   AI Probability: {data.get('ai_probability', 0)*100:.1f}%")
            print(f"   Human Probability: {data.get('human_probability', 0)*100:.1f}%")
            return True
        else:
            print(f"❌ /predict-file endpoint failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("AI DETECTOR BACKEND TEST SUITE")
    print("="*60)
    
    # Test 1: Info endpoint
    info_ok = test_info_endpoint()
    
    if not info_ok:
        print("\n❌ Backend is not responding. Please start the backend server:")
        print("   cd Backend")
        print("   python app.py")
        return
    
    # Test 2: Predict endpoint
    predict_ok = test_predict_endpoint()
    
    # Test 3: File upload endpoint
    # Create test file
    test_file = create_test_file()
    file_ok = test_file_upload_endpoint(test_file)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"✅ /info endpoint: {'PASS' if info_ok else 'FAIL'}")
    print(f"✅ /predict endpoint: {'PASS' if predict_ok else 'FAIL'}")
    print(f"✅ /predict-file endpoint: {'PASS' if file_ok else 'FAIL'}")
    
    if info_ok and predict_ok and file_ok:
        print("\n🎉 All tests passed! The backend is working correctly.")
        print("\n📝 Next steps:")
        print("   1. Open http://localhost:5173 in your browser")
        print("   2. Click 'File Upload' tab")
        print("   3. Upload a PDF or DOCX file")
        print("   4. Click 'Analyze File'")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
