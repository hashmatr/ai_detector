
import joblib
import os

try:
    model_path = r"e:\Machine Learning Project\ai_detector\Backend\Models\best_kfold_model.joblib"
    model = joblib.load(model_path)
    print(f"Model Type: {type(model)}")
    print(f"Model: {model}")
except Exception as e:
    print(f"Error: {e}")
