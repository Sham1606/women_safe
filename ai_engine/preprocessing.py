import librosa
import numpy as np
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def load_audio(file_path):
    """
    Load an audio file, resample to fixed rate, and return audio time series.
    """
    try:
        y, sr = librosa.load(file_path, sr=config.SAMPLE_RATE)
        return y
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def trim_silence(y):
    """Remove leading and trailing silence."""
    yt, _ = librosa.effects.trim(y, top_db=20)
    return yt

def normalize_audio(y):
    """Normalize audio amplitude to range [-1, 1]."""
    max_val = np.max(np.abs(y))
    if max_val > 0:
        return y / max_val
    return y

def pad_or_truncate(y):
    """Ensure audio is exactly the configured duration."""
    target_len = int(config.SAMPLE_RATE * config.DURATION)
    if len(y) > target_len:
        return y[:target_len]
    else:
        padding = target_len - len(y)
        return np.pad(y, (0, padding), 'constant')

def preprocess_pipeline(file_path):
    """
    Full preprocessing pipeline:
    Load -> Trim -> Normalize -> Pad/Truncate
    """
    y = load_audio(file_path)
    if y is None:
        return None
    
    y = trim_silence(y)
    y = normalize_audio(y)
    y = pad_or_truncate(y)
    
    return y
