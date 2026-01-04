"""Training Script for Ensemble Audio Stress Detector

Trains the ensemble model on labeled audio data.
"""

import numpy as np
import pandas as pd
from pathlib import Path
import argparse
import logging
from sklearn.model_selection import cross_val_score
import json

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_engine.audio_stress_detector import AudioStressDetector
from ai_engine.feature_extractor import FeatureExtractor
from ai_engine.preprocessing import AudioPreprocessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_dataset(data_dir: str) -> tuple:
    """Load audio dataset and labels from RAVDESS structure"""
    data_path = Path(data_dir)
    feature_extractor = FeatureExtractor()
    features = []
    labels = []
    
    # Import emotion mappings from config
    import config
    
    logger.info(f"Scanning for audio files in {data_path}...")
    
    # RAVDESS filename format: 03-01-XX-01-01-01-XX.wav
    # Third part is emotion: 01=neutral, 02=calm, ..., 08=surprised
    
    files = list(data_path.rglob("*.wav"))
    logger.info(f"Found {len(files)} .wav files")
    
    for audio_file in files:
        try:
            filename = audio_file.name
            parts = filename.split('-')
            
            if len(parts) < 3:
                continue
                
            emotion_code = parts[2]
            emotion = config.RAVDESS_MAP.get(emotion_code)
            
            if not emotion:
                continue
                
            label_str = config.EMOTION_TO_LABEL.get(emotion)
            
            if label_str is None:
                continue
                
            # Convert to binary label: stressed=1, normal=0
            label = 1 if label_str == 'stressed' else 0
            
            feat = feature_extractor.extract_from_file(str(audio_file))
            if feat is not None:
                features.append(feat)
                labels.append(label)
                
        except Exception as e:
            logger.warning(f"Failed to process {audio_file}: {e}")
            
    logger.info(f"Loaded {len(features)} samples ({labels.count(1)} stressed, {labels.count(0)} non-stressed)")
    
    return np.array(features), np.array(labels)


def train_model(data_dir: str, model_save_path: str, test_size: float = 0.2):
    """Train ensemble model
    
    Args:
        data_dir: Directory containing audio data
        model_save_path: Path to save trained model
        test_size: Test set proportion
    """
    logger.info("Starting training process...")
    
    # Load dataset
    X, y = load_dataset(data_dir)
    
    if len(X) == 0:
        logger.error("No samples loaded. Check data directory.")
        return
    
    # Initialize detector
    detector = AudioStressDetector()
    
    # Train
    metrics = detector.train(X, y, test_size=test_size)
    
    # Cross-validation
    logger.info("Running cross-validation...")
    cv_scores = cross_val_score(detector.ensemble, detector.scaler.transform(X), y, cv=5)
    logger.info(f"Cross-validation scores: {cv_scores}")
    logger.info(f"Mean CV score: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    # Save model
    detector.save_model(model_save_path)
    
    # Save metrics
    metrics_path = Path(model_save_path).parent / "training_metrics.json"
    with open(metrics_path, 'w') as f:
        json.dump({
            'test_accuracy': metrics['accuracy'],
            'confusion_matrix': metrics['confusion_matrix'],
            'cv_mean': float(cv_scores.mean()),
            'cv_std': float(cv_scores.std())
        }, f, indent=2)
    
    logger.info(f"Training completed. Metrics saved to {metrics_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train ensemble audio stress detector")
    parser.add_argument("--data-dir", type=str, required=True, help="Directory containing audio data")
    parser.add_argument("--model-path", type=str, default="ai_engine/models/ensemble_model.pkl", 
                       help="Path to save trained model")
    parser.add_argument("--test-size", type=float, default=0.2, help="Test set proportion")
    
    args = parser.parse_args()
    
    train_model(args.data_dir, args.model_path, args.test_size)
