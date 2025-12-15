import pandas as pd
import joblib
import os
import numpy as np

# Load Model
base_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(base_dir, "../Models/random_forest_model.joblib")
model = joblib.load(model_path)

# Load Data (subset for speed)
data_path = os.path.join(base_dir, "../../data.csv/data_with_features.csv")
df = pd.read_csv(data_path, nrows=5000)

# Feature Columns
feature_cols = [
    'text_length',
    'word_count',
    'has_min_words', 
    'avg_word_len', 
    'avg_sent_len', 
    'ttr', 
    'stop_ratio', 
    'punc_freq', 
    'digit_freq', 
    'upper_case_ratio'
]

print(f"Model loaded: {type(model)}")
print(f"Data loaded: {df.shape}")

with open("bias_analysis_result.txt", "w", encoding="utf-8") as f:
    f.write("-" * 40 + "\n")
    f.write("FEATURE IMPORTANCE\n")
    f.write("-" * 40 + "\n")
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]

    for i in range(len(feature_cols)):
        idx = indices[i]
        f.write(f"{i+1}. {feature_cols[idx]}: {importances[idx]:.4f}\n")

    # 2. Data Statistics (Human vs AI)
    f.write("\n" + "-" * 40 + "\n")
    f.write("DATA STATISTICS (Mean Values)\n")
    f.write("-" * 40 + "\n")

    human_df = df[df['label'] == 0]
    ai_df = df[df['label'] == 1]

    f.write(f"{'Feature':<20} | {'Human (0)':<12} | {'AI (1)':<12} | {'Diff'}\n")
    f.write("-" * 60 + "\n")

    for col in feature_cols:
        if col == 'has_min_words': continue # Boolean
        h_mean = human_df[col].mean()
        a_mean = ai_df[col].mean()
        f.write(f"{col:<20} | {h_mean:<12.4f} | {a_mean:<12.4f} | {a_mean - h_mean:.4f}\n")

    f.write("-" * 60 + "\n")
print("Analysis complete. Saved to bias_analysis_result.txt")
