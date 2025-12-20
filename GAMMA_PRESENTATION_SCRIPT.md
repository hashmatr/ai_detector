# Gamma AI Presentation Script: AI Content Detector Project

**Instructions:**
1. Go to [Gamma.app](https://gamma.app).
2. Click **"Create new"** -> **"Paste in text"** (or "Generate from notes").
3. Copy and paste the content below into the input box.
4. Select a **"Professional"** or **"Tech"** theme (e.g., "Dark Mode", "Cyberpunk", or "Minimalist").

---

# Presentation Title: Advanced AI Content Detector: Dual-Mode Architecture

## Slide 1: Experience the Challenge
**Subtitle:** The Rise of AI-Generated Content
**Points:**
- rapid proliferation of LLMs (ChatGPT, Claude, Gemini).
- The blurring line between human and machine writing.
- The critical need for academic integrity and content authenticity.
- **Problem:** Existing detectors are often biased or inaccurate on modern AI text.

## Slide 2: Project Overview & Solution
**Subtitle:** A Dual-Mode Approach to Detection
**Points:**
- **Core Concept:** A sophisticated web application offering two distinct detection strategies.
- **Pure ML Mode:** Fast, explainable baseline using traditional Machine Learning.
- **Hybrid Mode:** High-accuracy deep learning combined with ensemble methods.
- **Goal:** Robust detection capable of identifying subtle AI patterns.

## Slide 3: Pure Machine Learning Mode
**Subtitle:** Speed & Interpretability
**Points:**
- **Architecture:** Ensemble of 3 classic models.
- **Models Used:** 
  - Support Vector Machine (SVM)
  - AdaBoost Classifier
  - Random Forest
- **Features:** TF-IDF Vectorization & Linguistic Feature Extraction.
- **Pros:** Extremely fast inference, low resource usage.

## Slide 4: Hybrid ML + DL Mode (The Powerhouse)
**Subtitle:** Combining the Best of Both Worlds
**Points:**
- **Architecture:** Weighted vote between Deep Learning and ML Ensemble.
- **Configuration:** 
  - **70%** RoBERTa Transformer (Fine-tuned on 300k+ samples).
  - **30%** ML Ensemble (SVM + AdaBoost + RF).
- **Why this works:** RoBERTa captures semantic context, while ML catches statistical anomalies.
- **Result:** Superior accuracy on "hard-to-detect" modern AI text.

## Slide 5: Technical Stack
**Subtitle:** Built with Modern Technologies
**Points:**
- **Frontend:** React.js + Vite (Responsive, Dark Mode).
- **Backend:** Flask (Python) with RESTful API.
- **ML Libraries:** Scikit-learn, Transformers (Hugging Face), PyTorch.
- **Deployment:** Docker & AWS ready.
- **Data:** Trained on a custom dataset of 310,000+ human and AI samples.

## Slide 6: Key Application Features
**Subtitle:** More Than Just a Score
**Points:**
- **Aggressive Highlighting:** Visually marks AI-suspected sentences.
- **Detection Patterns:** Identifies academic formalisms, buzzwords, and passive voice overkill.
- **Multi-Input:** Support for direct text paste and File Uploads (PDF/DOCX).
- **Detailed Breakdown:** Shows probability splits and model confidence.
- **PDF Export:** Download detailed analysis reports.

## Slide 7: Future Roadmap
**Subtitle:** Continuously Evolving
**Points:**
- Expanding dataset to 1M+ samples.
- Adding support for multi-lingual detection.
- Real-time API integration for LMS (Learning Management Systems).
- Enhancing the RoBERTa fine-tuning with newer models (e.g., DeBERTa).

---
