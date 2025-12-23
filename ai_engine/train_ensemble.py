"""Training Pipeline for Ensemble Audio Stress Detection

Implements the complete training workflow:
1. Load and preprocess audio data
2. Extract features
3. Train ensemble model
4. Evaluate performance
5. Save model
"""

import os
import numpy as np
import pandas as pd
import logging
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
from typing import Tuple, List

from .audio_stress_detector import AudioStressDetector
from .feature_extractor import AudioFeatureExtractor
from .preprocessing import preprocess_audio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnsembleTrainingPipeline:
    """Complete training pipeline for audio stress detection"""
    
    def __init__(self, data_dir: str, output_dir: str = "ai_engine/models"):
        """
        Args:
            data_dir: Directory containing audio files
            output_dir: Directory to save trained models
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.feature_extractor = AudioFeatureExtractor()
        self.audio_detector = AudioStressDetector()
        
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        
        logger.info(f"Training pipeline initialized. Data dir: {data_dir}")
    
    def load_dataset(self, stressed_dir: str, non_stressed_dir: str) -> Tuple[np.ndarray, np.ndarray]:
        """Load and preprocess audio dataset
        
        Args:
            stressed_dir: Directory with stressed audio samples
            non_stressed_dir: Directory with non-stressed audio samples
            
        Returns:
            (features, labels)
        """
        features_list = []
        labels_list = []
        
        # Load stressed samples (label = 1)
        stressed_path = self.data_dir / stressed_dir
        logger.info(f"Loading stressed samples from {stressed_path}")
        
        for audio_file in stressed_path.glob("*.wav"):
            try:
                audio, sr = self.feature_extractor.load_audio(str(audio_file))
                audio_preprocessed = preprocess_audio(audio, sr)
                features = self.feature_extractor.extract_all_features(audio_preprocessed)
                
                features_list.append(features)
                labels_list.append(1)
            except Exception as e:
                logger.error(f"Error processing {audio_file}: {e}")
        
        # Load non-stressed samples (label = 0)
        non_stressed_path = self.data_dir / non_stressed_dir
        logger.info(f"Loading non-stressed samples from {non_stressed_path}")
        
        for audio_file in non_stressed_path.glob("*.wav"):
            try:
                audio, sr = self.feature_extractor.load_audio(str(audio_file))
                audio_preprocessed = preprocess_audio(audio, sr)
                features = self.feature_extractor.extract_all_features(audio_preprocessed)
                
                features_list.append(features)
                labels_list.append(0)
            except Exception as e:
                logger.error(f"Error processing {audio_file}: {e}")
        
        X = np.array(features_list)
        y = np.array(labels_list)
        
        logger.info(f"Loaded {len(X)} samples: {np.sum(y)} stressed, {len(y) - np.sum(y)} non-stressed")
        return X, y
    
    def split_data(self, X: np.ndarray, y: np.ndarray, test_size: float = 0.2, random_state: int = 42):
        """Split data into training and testing sets
        
        Args:
            X: Feature matrix
            y: Labels
            test_size: Proportion of test set
            random_state: Random seed
        """
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        logger.info(
            f"Data split: Train={len(self.X_train)}, Test={len(self.X_test)}"
        )
    
    def train(self) -> dict:
        """Train the ensemble model
        
        Returns:
            Training metrics
        """
        if self.X_train is None:
            raise ValueError("No training data. Call load_dataset() and split_data() first.")
        
        logger.info("Starting ensemble training...")
        train_acc, metrics = self.audio_detector.train(self.X_train, self.y_train)
        
        return metrics
    
    def evaluate(self) -> dict:
        """Evaluate model on test set
        
        Returns:
            Evaluation metrics
        """
        if self.X_test is None:
            raise ValueError("No test data available")
        
        logger.info("Evaluating model on test set...")
        
        # Predictions
        y_pred = []
        y_proba = []
        
        for features in self.X_test:
            pred, conf = self.audio_detector.predict(features)
            y_pred.append(pred)
            y_proba.append(conf)
        
        y_pred = np.array(y_pred)
        
        # Metrics
        accuracy = accuracy_score(self.y_test, y_pred)
        conf_matrix = confusion_matrix(self.y_test, y_pred)
        class_report = classification_report(self.y_test, y_pred, output_dict=True)
        
        logger.info(f"Test Accuracy: {accuracy:.4f}")
        logger.info(f"\nConfusion Matrix:\n{conf_matrix}")
        logger.info(f"\nClassification Report:\n{classification_report(self.y_test, y_pred)}")
        
        return {
            'accuracy': accuracy,
            'confusion_matrix': conf_matrix.tolist(),
            'classification_report': class_report,
            'predictions': y_pred.tolist(),
            'probabilities': y_proba
        }
    
    def save_model(self, model_name: str = "audio_stress_model.pkl", scaler_name: str = "scaler.pkl"):
        """Save trained model and scaler
        
        Args:
            model_name: Filename for model
            scaler_name: Filename for scaler
        """
        model_path = self.output_dir / model_name
        scaler_path = self.output_dir / scaler_name
        
        self.audio_detector.save_model(str(model_path), str(scaler_path))
        logger.info(f"Model saved to {model_path}")
    
    def run_full_pipeline(
        self,
        stressed_dir: str,
        non_stressed_dir: str,
        test_size: float = 0.2
    ) -> dict:
        """Run complete training pipeline
        
        Args:
            stressed_dir: Directory with stressed audio samples
            non_stressed_dir: Directory with non-stressed audio samples
            test_size: Test set proportion
            
        Returns:
            Complete results including train and test metrics
        """
        # Step 1: Load data
        logger.info("=" * 50)
        logger.info("STEP 1: Loading Dataset")
        logger.info("=" * 50)
        X, y = self.load_dataset(stressed_dir, non_stressed_dir)
        
        # Step 2: Split data
        logger.info("\n" + "=" * 50)
        logger.info("STEP 2: Splitting Data")
        logger.info("=" * 50)
        self.split_data(X, y, test_size=test_size)
        
        # Step 3: Train model
        logger.info("\n" + "=" * 50)
        logger.info("STEP 3: Training Ensemble Model")
        logger.info("=" * 50)
        train_metrics = self.train()
        
        # Step 4: Evaluate model
        logger.info("\n" + "=" * 50)
        logger.info("STEP 4: Evaluating Model")
        logger.info("=" * 50)
        test_metrics = self.evaluate()
        
        # Step 5: Save model
        logger.info("\n" + "=" * 50)
        logger.info("STEP 5: Saving Model")
        logger.info("=" * 50)
        self.save_model()
        
        results = {
            'train_metrics': train_metrics,
            'test_metrics': test_metrics
        }
        
        logger.info("\n" + "=" * 50)
        logger.info("TRAINING PIPELINE COMPLETED")
        logger.info("=" * 50)
        
        return results


if __name__ == "__main__":
    # Example usage
    pipeline = EnsembleTrainingPipeline(
        data_dir="ai_engine/data",
        output_dir="ai_engine/models"
    )
    
    results = pipeline.run_full_pipeline(
        stressed_dir="raw/stressed",
        non_stressed_dir="raw/non_stressed",
        test_size=0.2
    )
    
    print("\nFinal Results:")
    print(f"Train Accuracy: {results['train_metrics']['train_accuracy']:.4f}")
    print(f"Test Accuracy: {results['test_metrics']['accuracy']:.4f}")