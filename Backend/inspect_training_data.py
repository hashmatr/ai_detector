import pandas as pd
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_dir, "../data.csv/data_with_features.csv")

print("Checking training data quality...")
print("="*70)

# Load the data we actually trained on
df = pd.read_csv(data_path, nrows=20)

print("\nFirst 20 samples from training data:")
print("="*70)

for idx, row in df.iterrows():
    label = "AI" if row['label'] == 1 else "HUMAN"
    text = str(row['text'])[:150]
    print(f"\n[{idx+1}] Label: {label}")
    print(f"Text: {text}...")
    print("-"*70)

print("\n" + "="*70)
print("QUESTION: Do these labels look correct to you?")
print("If the 'HUMAN' samples look AI-generated or vice versa,")
print("then the dataset itself has incorrect labels.")
print("="*70)
