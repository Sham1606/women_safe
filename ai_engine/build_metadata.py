import os
import pandas as pd
import sys

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def parse_ravdess_filename(file_path):
    """
    Parses RAVDESS filename: 03-01-01-01-01-01-01.wav
    Returns dictionary with metadata.
    """
    filename = os.path.basename(file_path)
    parts = filename.split('.')[0].split('-')
    if len(parts) != 7:
        return None
    
    emotion_code = parts[2]
    actor_id = parts[6]
    gender = 'female' if int(actor_id) % 2 == 0 else 'male'
    
    emotion = config.RAVDESS_MAP.get(emotion_code, 'unknown')
    label = config.EMOTION_TO_LABEL.get(emotion, 'unknown')
    
    return {
        'file_path': file_path,
        'filename': filename,
        'dataset': 'RAVDESS',
        'emotion': emotion,
        'label': label,
        'actor_id': actor_id,
        'gender': gender
    }

def build_metadata():
    print("Scanning raw data directory...")
    data = []
    
    for root, dirs, files in os.walk(config.RAW_DATA_DIR):
        for file in files:
            if file.endswith('.wav'):
                full_path = os.path.join(root, file)
                # Try RAVDESS parser first
                meta = parse_ravdess_filename(full_path)
                if meta:
                    data.append(meta)
                else:
                    # Fallback or other datasets (TESS, etc.)
                    # For now just log basic info or skip
                    print(f"Skipping unknown format: {file}")

    if not data:
        print("No valid audio files found.")
        return

    df = pd.DataFrame(data)
    output_path = os.path.join(config.PROCESSED_DATA_DIR, 'metadata.csv')
    df.to_csv(output_path, index=False)
    print(f"Metadata saved to {output_path} with {len(df)} records.")
    print(df['label'].value_counts())

if __name__ == "__main__":
    build_metadata()
