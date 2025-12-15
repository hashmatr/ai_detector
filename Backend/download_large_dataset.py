"""
Download the largest AI detection datasets available
Target: 1 million+ samples
"""
from datasets import load_dataset
import pandas as pd
import os

print("="*80)
print("DOWNLOADING LARGE-SCALE AI DETECTION DATASETS")
print("Target: 1 Million+ samples")
print("="*80)

base_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(base_dir, "../data.csv")
os.makedirs(output_dir, exist_ok=True)

# List of large datasets to try
datasets_to_download = [
    {
        "name": "M4 - Massive Multi-domain AI Detection",
        "id": "mbzuai/M4",
        "split": "train",
        "description": "1M+ samples across multiple domains"
    },
    {
        "name": "GPT-wiki-intro (Full)",
        "id": "aadityaubhat/GPT-wiki-intro",
        "split": "train",
        "description": "150k Wikipedia vs GPT samples"
    },
    {
        "name": "ArguGPT",
        "id": "UKPLab/argugpt",
        "split": "train",
        "description": "Large argumentative text dataset"
    }
]

all_samples = []
total_downloaded = 0

for dataset_info in datasets_to_download:
    print(f"\n{'='*80}")
    print(f"Downloading: {dataset_info['name']}")
    print(f"Description: {dataset_info['description']}")
    print(f"{'='*80}")
    
    try:
        print("Loading dataset...")
        dataset = load_dataset(dataset_info['id'], split=dataset_info['split'], trust_remote_code=True)
        
        df = dataset.to_pandas()
        print(f"✅ Downloaded {len(df):,} samples")
        print(f"   Columns: {df.columns.tolist()}")
        
        # Try to identify text and label columns
        text_col = None
        label_col = None
        
        # Common column names
        text_candidates = ['text', 'content', 'article', 'generated_intro', 'wiki_intro', 'sentence', 'document']
        label_candidates = ['label', 'class', 'generated', 'is_ai', 'model']
        
        for col in df.columns:
            col_lower = col.lower()
            if any(candidate in col_lower for candidate in text_candidates):
                if text_col is None:
                    text_col = col
            if any(candidate in col_lower for candidate in label_candidates):
                if label_col is None:
                    label_col = col
        
        # Special handling for GPT-wiki dataset
        if 'generated_intro' in df.columns and 'wiki_intro' in df.columns:
            print("   Processing GPT-wiki format...")
            samples = []
            for idx, row in df.iterrows():
                if idx % 10000 == 0 and idx > 0:
                    print(f"      Processed {idx:,}/{len(df):,}...")
                
                # AI sample
                if pd.notna(row['generated_intro']) and len(str(row['generated_intro'])) > 50:
                    samples.append({
                        'text': str(row['generated_intro']),
                        'label': 1,
                        'source': dataset_info['name']
                    })
                
                # Human sample
                if pd.notna(row['wiki_intro']) and len(str(row['wiki_intro'])) > 50:
                    samples.append({
                        'text': str(row['wiki_intro']),
                        'label': 0,
                        'source': dataset_info['name']
                    })
            
            all_samples.extend(samples)
            total_downloaded += len(samples)
            print(f"   ✅ Extracted {len(samples):,} samples")
        
        elif text_col and label_col:
            print(f"   Using columns: text='{text_col}', label='{label_col}'")
            
            for idx, row in df.iterrows():
                if idx % 10000 == 0 and idx > 0:
                    print(f"      Processed {idx:,}/{len(df):,}...")
                
                text = str(row[text_col])
                if len(text) > 50:  # Min length filter
                    # Convert label to binary
                    label_val = row[label_col]
                    if isinstance(label_val, str):
                        label = 0 if label_val.lower() in ['human', '0', 'false'] else 1
                    else:
                        label = int(label_val)
                    
                    all_samples.append({
                        'text': text,
                        'label': label,
                        'source': dataset_info['name']
                    })
            
            total_downloaded += len(df)
            print(f"   ✅ Processed {len(df):,} samples")
        else:
            print(f"   ⚠️  Could not identify text/label columns")
            print(f"   Available columns: {df.columns.tolist()}")
        
        print(f"\n   Running total: {total_downloaded:,} samples")
        
        # Stop if we have enough
        if total_downloaded >= 1000000:
            print(f"\n✅ Reached 1 million samples! Stopping download.")
            break
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        continue

# Create final dataset
if all_samples:
    print(f"\n{'='*80}")
    print("CREATING FINAL DATASET")
    print(f"{'='*80}")
    
    df_all = pd.DataFrame(all_samples)
    
    # Remove duplicates
    print(f"\nRemoving duplicates...")
    original_len = len(df_all)
    df_all = df_all.drop_duplicates(subset=['text'])
    print(f"   Removed {original_len - len(df_all):,} duplicates")
    
    # Check balance
    human_count = sum(df_all['label'] == 0)
    ai_count = sum(df_all['label'] == 1)
    
    print(f"\nDataset composition:")
    print(f"   Human: {human_count:,}")
    print(f"   AI: {ai_count:,}")
    print(f"   Total: {len(df_all):,}")
    
    # Balance if needed
    if abs(human_count - ai_count) > len(df_all) * 0.2:  # If imbalance > 20%
        print(f"\nBalancing dataset...")
        min_count = min(human_count, ai_count)
        
        df_human = df_all[df_all['label'] == 0].sample(n=min_count, random_state=42)
        df_ai = df_all[df_all['label'] == 1].sample(n=min_count, random_state=42)
        
        df_all = pd.concat([df_human, df_ai])
        print(f"   Balanced to {len(df_all):,} samples ({min_count:,} per class)")
    
    # Shuffle
    df_all = df_all.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Save
    output_path = os.path.join(output_dir, "large_ai_dataset.csv")
    print(f"\nSaving to: {output_path}")
    print("This may take several minutes...")
    
    df_all.to_csv(output_path, index=False)
    
    print(f"\n{'='*80}")
    print("SUCCESS!")
    print(f"{'='*80}")
    print(f"Total samples: {len(df_all):,}")
    print(f"Human: {sum(df_all['label']==0):,}")
    print(f"AI: {sum(df_all['label']==1):,}")
    print(f"\nSaved to: {output_path}")
    print(f"\n{'='*80}")
    print("NEXT STEP:")
    print("python Model_training/train_on_large_dataset.py")
    print(f"{'='*80}")
else:
    print("\n❌ No data was downloaded successfully")
