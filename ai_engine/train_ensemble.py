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

from audio_stress_detector import AudioStressDetector
from feature_extractor import FeatureExtractor
from preprocessing import AudioPreprocessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_dataset(data_dir: str) -> tuple:
    """Load audio dataset and labels
    
    Expected structure:
    data_dir/
        stressed/
            audio1.wav
            audio2.wav
        non_stressed/
            audio3.wav
            audio4.wav
    
    Returns:
        (features, labels)
    """
    data_path = Path(data_dir)
    
    stressed_dir = data_path / "stressed"
    non_stressed_dir = data_path / "non_stressed"
    
    feature_extractor = FeatureExtractor()
    
    features = []
    labels = []
    
    # Load stressed samples
    logger.info(f"Loading stressed samples from {stressed_dir}")
    for audio_file in stressed_dir.glob("*.wav"):
        try:
            feat = feature_extractor.extract_from_file(str(audio_file))
            features.append(feat)
            labels.append(1)  # Stressed
        except Exception as e:
            logger.warning(f"Failed to process {audio_file}: {e}")
    
    # Load non-stressed samples
    logger.info(f"Loading non-stressed samples from {non_stressed_dir}")
    for audio_file in non_stressed_dir.glob("*.wav"):
        try:
            feat = feature_extractor.extract_from_file(str(audio_file))
            features.append(feat)
            labels.append(0)  # Non-stressed
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
