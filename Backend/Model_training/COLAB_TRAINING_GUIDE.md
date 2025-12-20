# 🚀 RoBERTa Training on Google Colab - Complete Guide

This guide walks you through training your AI detector model on Google Colab with GPU acceleration using all samples from your dataset.

---

## 📋 Prerequisites

- Google account (for Colab and Google Drive)
- Your `processed_data.csv` file (~2.8 GB)
- Stable internet connection for uploading/downloading

---

## 🎯 Step 1: Open Google Colab

1. Go to **[colab.research.google.com](https://colab.research.google.com)**
2. Sign in with your Google account

---

## 📤 Step 2: Upload the Notebook

1. Click **File → Upload notebook**
2. Navigate to:
   ```
   e:\Machine Learning Project\ai_detector\Backend\Model_training\RoBERTa_Colab_Training.ipynb
   ```
3. Click **Open** to upload

---

## ⚡ Step 3: Enable GPU (CRITICAL!)

1. Click **Runtime → Change runtime type**
2. Under **Hardware accelerator**, select **T4 GPU**
3. Click **Save**

> ⚠️ **Important**: Without GPU, training will take 10-20x longer!

### Verify GPU is Enabled:
Run the first cell - it will show:
```
✅ GPU Available: Tesla T4
📊 GPU Memory: 15.XX GB
```

---

## 📊 Step 4: Upload Your Data

When you run **Cell 2**, a file picker will appear:

1. Click **Choose Files**
2. Navigate to:
   ```
   e:\Machine Learning Project\ai_detector\data.csv\processed_data.csv
   ```
3. Click **Open**
4. Wait for upload to complete (5-15 minutes for 2.8 GB)

> 💡 **Tip**: Use a stable connection. If upload fails, you can also upload to Google Drive first, then mount Drive in Colab.

---

## ⚙️ Step 5: Configure Training (Optional)

In **Cell 4**, you can modify the training configuration:

```python
CONFIG = {
    'model_name': 'Hello-SimpleAI/chatgpt-detector-roberta',
    'max_length': 512,        # Token length (512 is max for RoBERTa)
    'batch_size': 16,         # Increase to 24/32 if you have enough GPU memory
    'epochs': 3,              # Increase for better accuracy (4-5 recommended)
    'learning_rate': 2e-5,    # Standard for fine-tuning transformers
    'warmup_ratio': 0.1,      # 10% warmup steps
    'weight_decay': 0.01,     # Regularization
    'test_size': 0.1,         # 10% for testing
    'gradient_accumulation_steps': 2,
}
```

### Recommended Settings by Dataset Size:

| Dataset Size | Batch Size | Epochs | Est. Time |
|--------------|------------|--------|-----------|
| < 100K       | 16         | 5      | ~1 hour   |
| 100K - 500K  | 16         | 3-4    | ~2-3 hours|
| 500K - 1M    | 16         | 3      | ~4-6 hours|
| > 1M         | 16         | 2-3    | ~6+ hours |

---

## ▶️ Step 6: Run Training

### Option A: Run All at Once
- Click **Runtime → Run all**

### Option B: Run Cell by Cell
- Click the **Play** button on each cell in order
- This allows you to see progress and catch any issues

### During Training You'll See:
```
📍 Epoch 1/3
Training Epoch 1: 100%|██████████| 5000/5000 [45:32<00:00, 1.83it/s]
📈 Training - Loss: 0.2341, Accuracy: 0.9234

🔍 Evaluating...
📊 Validation Results (Epoch 1):
   Accuracy:  0.9456
   Precision: 0.9423
   Recall:    0.9489
   F1-Score:  0.9456
   ⏱️ Epoch Time: 52.3 minutes
   
   ⭐ New best model! F1: 0.9456
```

---

## 💾 Step 7: Save the Trained Model

### Option A: Save to Google Drive (Recommended)
Run **Cell 12** - the model will be saved to:
```
Google Drive/My Drive/AI_Detector_Model/
├── roberta_finetuned/
├── roberta_finetuned_tokenizer/
├── training_info.json
└── training_history.png
```

### Option B: Direct Download
Run **Cell 13** - downloads `roberta_finetuned_model.zip` to your computer

---

## 📥 Step 8: Download Model to Your Computer

### From Google Drive:
1. Open [drive.google.com](https://drive.google.com)
2. Navigate to **My Drive/AI_Detector_Model/**
3. Right-click `roberta_finetuned` folder → **Download**
4. Right-click `roberta_finetuned_tokenizer` folder → **Download**

### From Direct Download:
The zip file should auto-download when you run Cell 13.

---

## 📁 Step 9: Copy Model to Your Project

Extract/copy the downloaded model files to your project:

```
e:\Machine Learning Project\ai_detector\Backend\Models\
├── roberta_finetuned\
│   ├── config.json
│   ├── model.safetensors (or pytorch_model.bin)
│   └── ...
└── roberta_finetuned_tokenizer\
    ├── tokenizer.json
    ├── vocab.json
    ├── merges.txt
    └── ...
```

### PowerShell Commands:
```powershell
# Create the Models directory if it doesn't exist
New-Item -ItemType Directory -Force -Path "e:\Machine Learning Project\ai_detector\Backend\Models"

# If you downloaded the zip file, extract it:
Expand-Archive -Path "$HOME\Downloads\roberta_finetuned_model.zip" -DestinationPath "e:\Machine Learning Project\ai_detector\Backend\Models" -Force

# Or if you downloaded folders from Google Drive, copy them:
Copy-Item -Recurse -Path "$HOME\Downloads\roberta_finetuned" -Destination "e:\Machine Learning Project\ai_detector\Backend\Models\"
Copy-Item -Recurse -Path "$HOME\Downloads\roberta_finetuned_tokenizer" -Destination "e:\Machine Learning Project\ai_detector\Backend\Models\"
```

---

## 🔧 Step 10: Update Backend to Use Fine-Tuned Model

Your `app.py` needs to be updated to use the locally fine-tuned model instead of the pre-trained one.

### Update the Model Loading in `app.py`:

```python
# Change this:
MODEL_NAME = "Hello-SimpleAI/chatgpt-detector-roberta"
tokenizer = RobertaTokenizer.from_pretrained(MODEL_NAME)
model = RobertaForSequenceClassification.from_pretrained(MODEL_NAME)

# To this:
import os

# Path to your fine-tuned model
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "Models", "roberta_finetuned")
TOKENIZER_PATH = os.path.join(BASE_DIR, "Models", "roberta_finetuned_tokenizer")

# Load fine-tuned model
tokenizer = RobertaTokenizer.from_pretrained(TOKENIZER_PATH)
model = RobertaForSequenceClassification.from_pretrained(MODEL_PATH)
```

---

## ✅ Step 11: Verify the Model Works

### Test the Backend:
```powershell
cd "e:\Machine Learning Project\ai_detector\Backend"
python app.py
```

### Test with Sample Text:
```python
import requests

response = requests.post('http://localhost:5000/analyze', json={
    'text': 'This is a test sentence to verify the model is working correctly.'
})
print(response.json())
```

---

## 🎉 Training Complete!

Your AI detector is now using a model fine-tuned on YOUR complete dataset!

### Expected Improvements:
- ✅ Higher accuracy on your specific data
- ✅ Better detection of AI text patterns in your domain
- ✅ Reduced false positives/negatives
- ✅ More confident predictions

---

## 🔧 Troubleshooting

### Issue: "CUDA out of memory"
**Solution**: Reduce batch size in CONFIG:
```python
'batch_size': 8,  # Reduce from 16
```

### Issue: Upload times out
**Solution**: Upload to Google Drive first:
1. Upload `processed_data.csv` to Google Drive
2. In Colab, run:
```python
from google.colab import drive
drive.mount('/content/drive')
uploaded_file = '/content/drive/MyDrive/processed_data.csv'
```

### Issue: Training is slow
**Solution**: 
- Verify GPU is enabled (Runtime → Change runtime type)
- Close other Colab notebooks
- Try at off-peak hours

### Issue: Model not loading locally
**Solution**: Check file paths and ensure all files are present:
```python
import os
model_path = "e:/Machine Learning Project/ai_detector/Backend/Models/roberta_finetuned"
print(os.listdir(model_path))  # Should show config.json, model files, etc.
```

---

## 📊 Understanding Training Metrics

| Metric | Good Value | Meaning |
|--------|-----------|---------|
| Accuracy | > 0.90 | Overall correctness |
| Precision | > 0.90 | True positives / (True + False positives) |
| Recall | > 0.90 | True positives / (True + False negatives) |
| F1-Score | > 0.90 | Harmonic mean of precision and recall |
| Loss | < 0.3 | Lower is better; should decrease each epoch |

---

## 📞 Need Help?

If you encounter issues:
1. Check the Colab output for error messages
2. Verify GPU is enabled
3. Ensure your CSV file has the correct format (`text`, `label` or `source` columns)
4. Try reducing batch size or number of epochs

---

*Last Updated: December 2025*
