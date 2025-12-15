"""
Download modern AI detection dataset from multiple sources
Uses datasets that are already in standard format
"""
from datasets import load_dataset
import pandas as pd
import os
import random

print("="*80)
print("DOWNLOADING MODERN AI DETECTION DATASETS")
print("="*80)

all_samples = []

# Dataset 1: AI vs Human text detection
print("\n[1/3] Downloading AI-Human text dataset...")
try:
    dataset = load_dataset("aadityaubhat/GPT-wiki-intro")
    df = dataset['train'].to_pandas()
    
    for idx, row in df.iterrows():
        if 'generated_intro' in df.columns and 'wiki_intro' in df.columns:
            # AI sample
            if pd.notna(row['generated_intro']) and len(str(row['generated_intro'])) > 50:
                all_samples.append({
                    'text': str(row['generated_intro']),
                    'label': 1,
                    'source': 'GPT-wiki'
                })
            # Human sample
            if pd.notna(row['wiki_intro']) and len(str(row['wiki_intro'])) > 50:
                all_samples.append({
                    'text': str(row['wiki_intro']),
                    'label': 0,
                    'source': 'Wikipedia'
                })
    
    print(f"   ✅ Added {len([s for s in all_samples if s['source'] in ['GPT-wiki', 'Wikipedia']]):,} samples")
except Exception as e:
    print(f"   ⚠️  Skipped: {e}")

# Dataset 2: Essay dataset
print("\n[2/3] Downloading essay dataset...")
try:
    dataset = load_dataset("qwedsacf/ivypanda-essays")
    df = dataset['train'].to_pandas()
    
    for idx, row in df.iterrows():
        if 'INSTRUCTION' in df.columns:
            text = str(row['INSTRUCTION'])
            if len(text) > 100:
                all_samples.append({
                    'text': text,
                    'label': 0,  # Human essays
                    'source': 'IvyPanda-Essays'
                })
    
    print(f"   ✅ Added {len([s for s in all_samples if s['source'] == 'IvyPanda-Essays']):,} human essays")
except Exception as e:
    print(f"   ⚠️  Skipped: {e}")

# Dataset 3: Try to get ChatGPT detection dataset
print("\n[3/3] Downloading ChatGPT detection dataset...")
try:
    dataset = load_dataset("Hello-SimpleAI/HC3-Chinese", split="baike")
    df = dataset.to_pandas()
    
    for idx, row in df.iterrows():
        if idx > 5000:  # Limit to avoid too much data
            break
        if 'question' in df.columns and 'human_answers' in df.columns:
            # Human answers
            if isinstance(row['human_answers'], list):
                for ans in row['human_answers'][:2]:  # Take first 2
                    if ans and len(str(ans)) > 50:
                        all_samples.append({
                            'text': str(ans),
                            'label': 0,
                            'source': 'HC3-Human'
                        })
            # ChatGPT answers
            if 'chatgpt_answers' in df.columns and isinstance(row['chatgpt_answers'], list):
                for ans in row['chatgpt_answers'][:2]:
                    if ans and len(str(ans)) > 50:
                        all_samples.append({
                            'text': str(ans),
                            'label': 1,
                            'source': 'HC3-ChatGPT'
                        })
    
    print(f"   ✅ Added HC3 samples")
except Exception as e:
    print(f"   ⚠️  Skipped: {e}")

# Create final dataset
if len(all_samples) > 0:
    print(f"\n{'='*80}")
    print("PROCESSING COMBINED DATASET")
    print(f"{'='*80}")
    
    df_all = pd.DataFrame(all_samples)
    
    # Remove duplicates
    df_all = df_all.drop_duplicates(subset=['text'])
    
    # Balance classes
    human_count = sum(df_all['label'] == 0)
    ai_count = sum(df_all['label'] == 1)
    
    print(f"\nBefore balancing:")
    print(f"  Human: {human_count:,}")
    print(f"  AI: {ai_count:,}")
    
    # Balance to the smaller class
    min_count = min(human_count, ai_count)
    
    df_human = df_all[df_all['label'] == 0].sample(n=min(min_count, human_count), random_state=42)
    df_ai = df_all[df_all['label'] == 1].sample(n=min(min_count, ai_count), random_state=42)
    
    df_final = pd.concat([df_human, df_ai]).sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Save
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "../data.csv")
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "modern_ai_dataset.csv")
    df_final.to_csv(output_path, index=False)
    
    print(f"\n{'='*80}")
    print("SUCCESS!")
    print(f"{'='*80}")
    print(f"Total samples: {len(df_final):,}")
    print(f"Human: {sum(df_final['label']==0):,}")
    print(f"AI: {sum(df_final['label']==1):,}")
    print(f"\nSaved to: {output_path}")
    print(f"\n{'='*80}")
    print("READY TO TRAIN!")
    print(f"{'='*80}")
else:
    print("\n❌ No data was downloaded. Check your internet connection.")
