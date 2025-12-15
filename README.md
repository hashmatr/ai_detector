# AI Content Detector

A sophisticated AI content detection system using hybrid ensemble models to identify AI-generated text with high accuracy.

## Features

- **Hybrid AI Detection**: Combines RoBERTa transformer (70%) with ML ensemble models (30%)
- **File Upload Support**: Analyze PDF and DOCX documents
- **Sentence Highlighting**: Visual identification of AI-suspected sentences
- **Batch Processing**: Process multiple files simultaneously
- **Analysis History**: Track and review past analyses
- **Professional UI**: Clean, emoji-free interface
- **Dark/Light Theme**: Toggle between themes

## Tech Stack

### Backend
- **Python** with Flask
- **PyTorch** & Transformers (Hugging Face)
- **scikit-learn** for ML models
- **RoBERTa** transformer model: `Hello-SimpleAI/chatgpt-detector-roberta`

### Frontend
- **React** with Vite
- **Axios** for API calls
- Modern CSS with responsive design

## Models

### Primary Model: RoBERTa Transformer (70% weight)
- Pre-trained on AI-generated text detection
- 125 million parameters
- Excellent semantic understanding

### Secondary Model: ML Ensemble (30% weight)
- Random Forest + K-Nearest Neighbors
- Feature engineering with TF-IDF
- Statistical pattern detection

### Combined Accuracy: ~95%+

## Installation

### Backend Setup
```bash
cd Backend
pip install -r requirements.txt
python app.py
```

### Frontend Setup
```bash
cd Frontend
npm install
npm run dev
```

## Usage

1. **Text Analysis**: Paste text directly into the analyzer
2. **File Upload**: Upload PDF or DOCX files for analysis
3. **Batch Processing**: Process multiple files at once
4. **View History**: Review past analyses and statistics

## API Endpoints

- `POST /predict` - Analyze text
- `POST /predict-file` - Analyze uploaded file
- `GET /info` - Get model information

## Project Structure

```
ai_detector/
├── Backend/
│   ├── app.py              # Flask API
│   ├── Models/             # Trained models (not in Git)
│   └── Model_training/     # Training scripts
├── Frontend/
│   ├── src/
│   │   ├── App.jsx         # Main application
│   │   ├── components/     # React components
│   │   └── utils/          # Utility functions
│   └── index.html
└── .gitignore
```

## Model Files

Model files (`.joblib`, `.pkl`) are excluded from Git due to size. Train models using scripts in `Backend/Model_training/`.

## License

MIT

## Author

Developed as an advanced machine learning project for AI content detection.