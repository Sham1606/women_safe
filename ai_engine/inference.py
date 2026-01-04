import numpy as np
import os
import sys
import io
import librosa
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from ai_engine.audio_stress_detector import AudioStressDetector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model instance
DETECTOR = None

def load_model():
    """Load the AudioStressDetector model if not already loaded."""
    global DETECTOR
    if DETECTOR is None:
        try:
            # Path to the ensemble model trained by train_ensemble.py
            model_path = os.path.join(config.BASE_DIR, 'ai_engine', 'models', 'ensemble_model.pkl')
            
            if not os.path.exists(model_path):
                logger.error(f"Model file not found at {model_path}")
                return False
                
            DETECTOR = AudioStressDetector(model_path=model_path)
            logger.info("AudioStressDetector loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading AudioStressDetector: {e}")
            return False
    return True

def predict_stress(audio_bytes=None, file_path=None):
    """
    Predict stress from audio bytes or file path.
    Returns: {"label": "stressed"|"normal", "confidence": float}
    """
    if not load_model():
        return {"error": "Model not loaded"}

    try:
        if audio_bytes:
            # Load audio from bytes
            # librosa.load accepts file-like objects
            y, sr = librosa.load(io.BytesIO(audio_bytes), sr=config.SAMPLE_RATE)
        elif file_path:
            # Load audio from file path
            y, sr = librosa.load(file_path, sr=config.SAMPLE_RATE)
        else:
            return {"error": "No input provided"}
            
        # Use detector to predict from array (since we already loaded it to memory)
        # Note: AudioStressDetector.predict_from_array handles preprocessing
        prediction, confidence = DETECTOR.predict_from_array(y)
        
        return {
            "label": "stressed" if prediction == 1 else "normal",
            "confidence": confidence,
            "is_stressed": bool(prediction == 1)
        }
        
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        return {"error": f"Prediction failed: {str(e)}"}

if __name__ == "__main__":
    # Test with a dummy file if available
    print("Running inference test...")
    if load_model():
        # Look for a test file
        test_dir = os.path.join(config.RAW_DATA_DIR)
        test_files = []
        for root, dirs, files in os.walk(test_dir):
            for file in files:
                if file.endswith('.wav'):
                    test_files.append(os.path.join(root, file))
                    if len(test_files) > 0: break
            if len(test_files) > 0: break
            
        if test_files:
            print(f"Testing with {test_files[0]}")
            result = predict_stress(file_path=test_files[0])
            print("Result:", result)
        else:
            print("No wav files found for testing.")
