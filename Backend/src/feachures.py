# features.py - OPTIMIZED & CLEANED
# Removes slow dependencies like SpaCy/POS tagging for 100x speedup.

import pandas as pd
import numpy as np
import re
import math
from collections import Counter
import os
import time

# ---------------------------------------------------------
# CONFIGURATION & CONSTANTS
# ---------------------------------------------------------
STOPWORDS = set([
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", 
    "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 
    'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 
    'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 
    'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 
    'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 
    'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 
    'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 
    'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 
    'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 
    'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 
    'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 
    'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 
    'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm', 
    'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', 
    "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', 
    "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't", 
    'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 
    'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"
])

def simple_tokenize(text):
    """Fast word tokenization using regex"""
    return re.findall(r'\b\w+\b', text.lower())

def count_sentences(text):
    """Fast sentence counting"""
    return max(1, len(re.split(r'[.!?]+', text)) - 1)

# ---------------------------------------------------------
# FEATURE EXTRACTION LOGIC
# ---------------------------------------------------------
def extract_features_fast(text):
    """
    Extracts key features quickly.
    Removed slow POS tagging (nouns/verbs) for performance.
    """
    if not isinstance(text, str) or not text:
        return {
            'avg_word_len': 0, 'avg_sent_len': 0, 'ttr': 0,
            'stop_ratio': 0, 'punc_freq': 0, 'digit_freq': 0,
            'upper_case_ratio': 0
        }

    # Basic stats
    words = simple_tokenize(text)
    num_words = len(words)
    num_sents = count_sentences(text)
    
    if num_words == 0:
        return {
            'avg_word_len': 0, 'avg_sent_len': 0, 'ttr': 0,
            'stop_ratio': 0, 'punc_freq': 0, 'digit_freq': 0,
            'upper_case_ratio': 0
        }

    # 1. Average Word Length
    word_lens = [len(w) for w in words]
    avg_word_len = sum(word_lens) / num_words

    # 2. Average Sentence Length (words per sentence)
    avg_sent_len = num_words / num_sents

    # 3. Type-Token Ratio (Vocabulary Richness)
    # Unique words / Total words
    ttr = len(set(words)) / num_words

    # 4. Stopword Ratio
    # How many words are common stopwords?
    num_stops = sum(1 for w in words if w in STOPWORDS)
    stop_ratio = num_stops / num_words

    # 5. Punctuation Frequency
    num_punc = len(re.findall(r'[^\w\s]', text))
    punc_freq = num_punc / len(text)

    # 6. Digit Frequency
    num_digits = sum(c.isdigit() for c in text)
    digit_freq = num_digits / len(text)
    
    # 7. Uppercase Ratio (checks for shouting or formal nouns)
    upper_case_ratio = sum(1 for c in text if c.isupper()) / len(text)

    return {
        'avg_word_len': avg_word_len,
        'avg_sent_len': avg_sent_len,
        'ttr': ttr,
        'stop_ratio': stop_ratio,
        'punc_freq': punc_freq,
        'digit_freq': digit_freq,
        'upper_case_ratio': upper_case_ratio
    }

# ---------------------------------------------------------
# MAIN EXECUTION
# ---------------------------------------------------------
if __name__ == "__main__":
    # Setup paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, "..", "..", "data.csv", "processed_data.csv")
    output_path = os.path.join(script_dir, "..", "..", "data.csv", "data_with_features.csv")

    print("="*60)
    print("FAST FEATURE EXTRACTION (CHUNKED)")
    print("="*60)

    # 1. Check Input
    print(f"\n[1/3] Checking input: {input_path}")
    if not os.path.exists(input_path):
        print("❌ Error: processed_data.csv not found!")
        exit()

    # 2. Extract Features in Chunks
    print("\n[2/3] Extracting features in chunks...")
    start_time = time.time()
    
    chunk_size = 10000
    target_samples = 25000
    
    print(f"\nScanning for {target_samples} samples per class...")
    
    human_samples = []
    ai_samples = []
    
    human_count = 0
    ai_count = 0
    
    chunk_iter = pd.read_csv(input_path, chunksize=chunk_size)
    
    try:
        for i, chunk in enumerate(chunk_iter):
            # Optimally identifying needed samples
            needed_human = target_samples - human_count
            needed_ai = target_samples - ai_count
            
            if needed_human <= 0 and needed_ai <= 0:
                print("   ✅ Reached target for both classes!")
                break
                
            # Filter chunk
            # Assuming 'label' is 0 for Human, 1 for AI. 
            # Or 'source' column 'human' vs 'gpt'/'ai'/'model'
            
            # Let's inspect source just in case label is missing or wrong
            if 'label' not in chunk.columns:
                 chunk['label'] = chunk['source'].apply(lambda s: 0 if str(s).lower() == 'human' else 1)
            
            chunk_human = chunk[chunk['label'] == 0]
            chunk_ai = chunk[chunk['label'] == 1]
            
            # Take what we need
            if needed_human > 0 and not chunk_human.empty:
                to_take = chunk_human.head(needed_human).copy()
                # Extract features only for these
                features_data = [extract_features_fast(str(text)) for text in to_take['text']]
                features_df = pd.DataFrame(features_data)
                
                combined = pd.concat([to_take.reset_index(drop=True), features_df], axis=1)
                human_samples.append(combined)
                human_count += len(combined)
                
            if needed_ai > 0 and not chunk_ai.empty:
                to_take = chunk_ai.head(needed_ai).copy()
                features_data = [extract_features_fast(str(text)) for text in to_take['text']]
                features_df = pd.DataFrame(features_data)
                
                combined = pd.concat([to_take.reset_index(drop=True), features_df], axis=1)
                ai_samples.append(combined)
                ai_count += len(combined)
                
            print(f"   Batch {i+1}: Human={human_count}/{target_samples}, AI={ai_count}/{target_samples}")

        # specific check if we failed to get enough data
        if human_count == 0 or ai_count == 0:
             print("❌ Failed to find data for one class! Check label column.")
             
        df_human = pd.concat(human_samples) if human_samples else pd.DataFrame()
        df_ai = pd.concat(ai_samples) if ai_samples else pd.DataFrame()
        
        # Combine
        print(f"\n   Combining {len(df_human)} Human + {len(df_ai)} AI samples...")
        df_final = pd.concat([df_human, df_ai])
        
        # Shuffle
        df_final = df_final.sample(frac=1, random_state=42).reset_index(drop=True)
        
        df_final.to_csv(output_path, index=False)
        print(f"   ✅ Saved balanced dataset ({len(df_final):,} rows)")
        
    except Exception as e:
        print(f"\n❌ Loop Error: {e}")
        import traceback
        traceback.print_exc()

    # 3. Done
    print(f"\n[3/3] Done.")
    print("="*60)