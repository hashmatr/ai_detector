import pandas as pd
import os

# Find the data file
base_dir = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(base_dir, "../data.csv/processed_data.csv")

print(f"Reading from: {data_path}")
print("="*60)

# Read first 50k rows
df = pd.read_csv(data_path, nrows=50000)

print(f"\nTotal rows loaded: {len(df)}")
print(f"\nColumns: {list(df.columns)}")

print("\n" + "="*60)
print("LABEL DISTRIBUTION:")
print("="*60)
print(df['label'].value_counts())

print("\n" + "="*60)
print("SOURCE DISTRIBUTION:")
print("="*60)
print(df['source'].value_counts())

print("\n" + "="*60)
print("SAMPLE TEXTS:")
print("="*60)

# Find first human sample
human_samples = df[df['label'] == 0]
if len(human_samples) > 0:
    print("\n[HUMAN SAMPLE]:")
    print(human_samples['text'].iloc[0][:300])
else:
    print("\n⚠️ NO HUMAN SAMPLES FOUND IN FIRST 50K ROWS!")

# Find first AI sample
ai_samples = df[df['label'] == 1]
if len(ai_samples) > 0:
    print("\n[AI SAMPLE]:")
    print(ai_samples['text'].iloc[0][:300])
else:
    print("\n⚠️ NO AI SAMPLES FOUND IN FIRST 50K ROWS!")

print("\n" + "="*60)
print("CHECKING FOR DATA QUALITY ISSUES:")
print("="*60)

# Check if labels match source
df['label_from_source'] = df['source'].apply(lambda s: 0 if str(s).lower() == 'human' else 1)
mismatch = (df['label'] != df['label_from_source']).sum()
print(f"Label/Source mismatches: {mismatch}")

# Check text lengths
print(f"\nAverage text length (Human): {df[df['label']==0]['text'].str.len().mean():.0f} chars")
print(f"Average text length (AI): {df[df['label']==1]['text'].str.len().mean():.0f} chars")

print("\n" + "="*60)
