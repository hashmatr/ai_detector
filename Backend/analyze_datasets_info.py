import os
import pandas as pd
import sys

output_file = "dataset_info.txt"

def log(msg):
    print(msg)
    with open(output_file, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def get_file_size_mb(file_path):
    return os.path.getsize(file_path) / (1024 * 1024)

def analyze_csv(file_path):
    name = os.path.basename(file_path)
    log(f"Analyzing {name}...")
    try:
        # Read header
        df_header = pd.read_csv(file_path, nrows=0)
        columns = df_header.columns.tolist()
        num_cols = len(columns)
        
        # Estimate rows if too large, or count strictly
        # For speed on large files, counting lines is safer but slower
        # Let's count bytes and estimate or just count lines
        count = 0
        with open(file_path, 'rb') as f:
            for _ in f:
                count += 1
        num_rows = count - 1 if count > 0 else 0
            
        size_mb = get_file_size_mb(file_path)
        
        log(f"  Size: {size_mb:.2f} MB")
        log(f"  Rows: {num_rows:,}")
        log(f"  Columns: {num_cols}")
        log(f"  Column Names: {columns}")
        log("-" * 40)
        
    except Exception as e:
        log(f"  Error analyzing {name}: {str(e)}")
        log("-" * 40)

# Clear file
with open(output_file, "w") as f:
    f.write("DATASET REPORT\n================\n")

data_dir = r"e:\Machine Learning Project\ai_detector\data.csv"
files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]

# Sort by size to do small ones first? No, let's just do them.
files.sort()

log(f"Found {len(files)} datasets in {data_dir}\n")
log("-" * 40)

for f in files:
    analyze_csv(os.path.join(data_dir, f))
