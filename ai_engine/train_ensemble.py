"""Training Script for Ensemble Audio Stress Detection Model

Steps:
1. Collect labeled audio data (stressed / non-stressed)
2. Preprocess audio (noise removal, normalization)
3. Extract features (MFCC, Chroma, Mel, Spectral Contrast)
4. Train ensemble classifiers (LR, RF, GB, SVM)
5. Evaluate and save model
"""

import os
import numpy as np
import pandas as pd
from sklearn.model_selection import cross_val_score
import librosa
from tqdm import tqdm

from audio_stress_detector import AudioStressDetector
from feature_extractor import AudioFeatureExtractor
from preprocessing import AudioPreprocessor


def load_dataset(data_dir: str) -> tuple:
    """Load audio dataset
    
    Expected structure:
    data_dir/
        stressed/
            audio1.wav
            audio2.wav
        non_stressed/
            audio1.wav
            audio2.wav
    
    Returns:
        X: Feature matrix
        y: Labels (1: stressed, 0: non-stressed)
    """
    feature_extractor = AudioFeatureExtractor()
    preprocessor = AudioPreprocessor()
    
    X = []
    y = []
    
    # Load stressed samples
    stressed_dir = os.path.join(data_dir, 'stressed')
    if os.path.exists(stressed_dir):
        for filename in tqdm(os.listdir(stressed_dir), desc="Loading stressed samples"):
            if filename.endswith(('.wav', '.mp3', '.ogg')):
                filepath = os.path.join(stressed_dir, filename)
                try:
                    audio, sr = preprocessor.load_and_preprocess(filepath)
                    features = feature_extractor.extract_features(audio)
                    if features is not None:
                        X.append(features)
                        y.append(1)  # Stressed
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
    
    # Load non-stressed samples
    non_stressed_dir = os.path.join(data_dir, 'non_stressed')
    if os.path.exists(non_stressed_dir):
        for filename in tqdm(os.listdir(non_stressed_dir), desc="Loading non-stressed samples"):
            if filename.endswith(('.wav', '.mp3', '.ogg')):
                filepath = os.path.join(non_stressed_dir, filename)
                try:
                    audio, sr = preprocessor.load_and_preprocess(filepath)
                    features = feature_extractor.extract_features(audio)
                    if features is not None:
                        X.append(features)
                        y.append(0)  # Non-stressed
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
    
    return np.array(X), np.array(y)


def train_model(data_dir: str, save_path: str = 'ai_engine/models/audio_stress_model.pkl'):
    """Train and save the ensemble model"""
    print("=" * 60)
    print("ENSEMBLE AUDIO STRESS DETECTION - TRAINING")
    print("=" * 60)
    
    # Load dataset
    print("\n[1/5] Loading dataset...")
    X, y = load_dataset(data_dir)
    
    print(f"\nDataset loaded:")
    print(f"  - Total samples: {len(X)}")
    print(f"  - Stressed samples: {np.sum(y == 1)}")
    print(f"  - Non-stressed samples: {np.sum(y == 0)}")
    print(f"  - Feature dimensions: {X.shape[1]}")
    
    if len(X) < 10:
        print("\nError: Insufficient data for training. Need at least 10 samples.")
        return
    
    # Initialize detector
    print("\n[2/5] Initializing ensemble detector...")
    detector = AudioStressDetector()
    
    # Train model
    print("\n[3/5] Training ensemble model...")
    print("  Classifiers: Logistic Regression, Random Forest, Gradient Boosting, SVM")
    print("  Voting: Soft (probability-based)")
    
    metrics = detector.train(X, y, test_size=0.2)
    
    # Display results
    print("\n[4/5] Training completed!")
    print(f"\nPerformance Metrics:")
    print(f"  - Training Accuracy: {metrics['train_accuracy']:.4f}")
    print(f"  - Test Accuracy: {metrics['test_accuracy']:.4f}")
    print(f"\nConfusion Matrix:")
    print(f"  {metrics['confusion_matrix']}")
    print(f"\nClassification Report:")
    print(metrics['classification_report'])
    
    # Save model
    print("\n[5/5] Saving model...")
    detector.save_model(save_path)
    print(f"\n{'='*60}")
    print(f"Model saved successfully to: {save_path}")
    print(f"{'='*60}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Train Ensemble Audio Stress Detector")
    parser.add_argument('--data-dir', type=str, required=True, help='Path to dataset directory')
    parser.add_argument('--save-path', type=str, default='ai_engine/models/audio_stress_model.pkl',
                       help='Path to save trained model')
    
    args = parser.parse_args()
    
    train_model(args.data_dir, args.save_path)