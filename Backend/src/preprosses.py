# preprocess.py - OPTIMIZED VERSION (Fast!)
import re
import pandas as pd

def clean_text(text):
    """Clean and normalize text data - FAST version"""
    if not isinstance(text, str): 
        return ""
    text = text.lower()
    text = re.sub(r"http\S+", "", text)  # Remove URLs
    text = re.sub(r"<.*?>", " ", text)  # Remove HTML tags
    text = re.sub(r"[^a-z0-9\s\.\,\!\?\']", " ", text)  # Keep only alphanumeric and basic punctuation
    text = re.sub(r"\s+", " ", text).strip()  # Remove extra whitespace
    return text

def filter_min_words_fast(text, min_words=30):
    """Check if text has minimum number of words - FAST version using split()"""
    # Using split() instead of NLTK - 100x faster!
    return len(text.split()) >= min_words

def create_labels(df):
    """Create binary labels: 0 for human, 1 for AI-generated"""
    df['label'] = df['source'].apply(lambda s: 0 if s.lower() == 'human' else 1)
    return df

if __name__ == "__main__":
    print("="*60)
    print("PREPROCESSING DATA - OPTIMIZED VERSION")
    print("="*60)
    
    # Load data
    print("\n[1/4] Loading data...")
    df = pd.read_csv("../../data.csv/data.csv")
    print(f"   Loaded: {df.shape[0]:,} samples")
    
    # Create labels
    print("\n[2/4] Creating labels...")
    df = create_labels(df)
    print(f"   Labels created!")
    print(f"   Human (0): {sum(df['label']==0):,}")
    print(f"   AI (1): {sum(df['label']==1):,}")
    
    # Clean text
    print("\n[3/4] Cleaning text...")
    df['cleaned_text'] = df['text'].apply(clean_text)
    print(f"   Text cleaned!")
    
    # Filter by minimum words (FAST version)
    print("\n[4/4] Filtering by minimum words (≥30)...")
    df['has_min_words'] = df['cleaned_text'].apply(filter_min_words_fast)
    df_filtered = df[df['has_min_words']].copy()
    
    print(f"\n   Original samples: {len(df):,}")
    print(f"   Filtered samples: {len(df_filtered):,}")
    print(f"   Removed: {len(df) - len(df_filtered):,}")
    
    print(f"\n   Label distribution (filtered):")
    print(f"   Human (0): {sum(df_filtered['label']==0):,}")
    print(f"   AI (1): {sum(df_filtered['label']==1):,}")
    
    # Save processed data
    print("\n[5/5] Saving processed data...")
    df_filtered.to_csv("../../data.csv/processed_data.csv", index=False)
    print(f"   ✅ Saved to: ../../data.csv/processed_data.csv")
    
    print("\n" + "="*60)
    print("PREPROCESSING COMPLETE!")
    print("="*60)
    print(f"\nFinal dataset shape: {df_filtered.shape}")
    print(f"Columns: {list(df_filtered.columns)}")
