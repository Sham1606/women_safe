import joblib
import numpy as np
import os
import sys
import io
import librosa
import soundfile as sf

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from ai_engine.preprocessing import trim_silence, normalize_audio, pad_or_truncate
from ai_engine.features import extract_features

# Global model cache
MODEL = None
SCALER = None

def load_models():
    """Load model and scaler if not already loaded."""
    global MODEL, SCALER
    if MODEL is None:
        try:
            MODEL = joblib.load(config.MODEL_PATH)
            SCALER = joblib.load(config.SCALER_PATH)
            print("Models loaded successfully.")
        except Exception as e:
            print(f"Error loading models: {e}")
            return False
    return True

def predict_stress(audio_bytes=None, file_path=None):
    """
    Predict stress from audio bytes or file path.
    Returns: {"label": "stressed"|"normal", "confidence": float}
    """
    if not load_models():
        return {"error": "Model not loaded"}

    # Load audio
    try:
        if audio_bytes:
            # Load from bytes (expected format: wav/mp3/etc)
            y, sr = librosa.load(io.BytesIO(audio_bytes), sr=config.SAMPLE_RATE)
        elif file_path:
            y, sr = librosa.load(file_path, sr=config.SAMPLE_RATE)
        else:
            return {"error": "No input provided"}
    except Exception as e:
        return {"error": f"Audio load failed: {str(e)}"}

    # Preprocess
    y = trim_silence(y)
    y = normalize_audio(y)
    y = pad_or_truncate(y)

    # Feature extraction
    feats = extract_features(y)
    feats = feats.reshape(1, -1) # Reshape for scalar

    # Scale
    feats_scaled = SCALER.transform(feats)

    # Predict
    probs = MODEL.predict_proba(feats_scaled)[0]
    classes = MODEL.classes_
    
    # Get class with highest probability
    max_idx = np.argmax(probs)
    label = classes[max_idx]
    confidence = float(probs[max_idx])

    return {
        "label": label,
        "confidence": confidence
    }

if __name__ == "__main__":
    # Simple test
    print("Running inference test...")
    # Generate a dummy file if needed or use one exists
    test_file = os.path.join(config.RAW_DATA_DIR, "03-01-05-01-01-01-01.wav") # Angry dummy
    if os.path.exists(test_file):
        result = predict_stress(file_path=test_file)
        print("Result:", result)
    else:
        print("No test file found.")
