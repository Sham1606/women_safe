import requests
import zipfile
import os
import sys
from tqdm import tqdm

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

RAVDESS_URL = "https://zenodo.org/record/1188976/files/Audio_Speech_Actors_01-24.zip?download=1"

def download_file(url, dest_path):
    print(f"Downloading from {url}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024 * 64 # 64KB chunks to save memory

        with open(dest_path, 'wb') as f, tqdm(total=total_size, unit='iB', unit_scale=True) as bar:
            for data in response.iter_content(block_size):
                bar.update(len(data))
                f.write(data)
        print("Download complete.")
        return True
    except Exception as e:
        print(f"Download Error: {e}")
        return False

def extract_file(zip_path, extract_to):
    print(f"Extracting {zip_path} to {extract_to}...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Extract one by one to avoid memory spike if many files
            for file in tqdm(zip_ref.namelist(), desc="Extracting"):
                zip_ref.extract(file, extract_to)
        print("Extraction complete.")
    except Exception as e:
        print(f"Extraction Error: {e}")

def main():
    # Ensure raw directory
    os.makedirs(config.RAW_DATA_DIR, exist_ok=True)
    
    zip_name = "ravdess_speech.zip"
    zip_path = os.path.join(config.DATA_DIR, zip_name)
    
    # 1. Download
    # Check if file exists and is decent size (e.g. > 100MB)
    if os.path.exists(zip_path) and os.path.getsize(zip_path) > 100 * 1024 * 1024:
        print("Zip file already exists, skipping download.")
    else:
        if not download_file(RAVDESS_URL, zip_path):
            return

    # 2. Extract
    extract_file(zip_path, config.RAW_DATA_DIR)
    
    print("RAVDESS dataset is ready in data/raw.")

if __name__ == "__main__":
    main()
