"""Ensemble Audio Stress Detection

Implements the algorithm from project requirements:
- Multiple base classifiers: Logistic Regression, Random Forest, Gradient Boosting, SVM
- Soft Voting Ensemble to aggregate probabilities
- Feature extraction: MFCC, Chroma, Mel, Spectral Contrast
"""

import numpy as np
import pickle
from sklearn.ensemble import VotingClassifier, RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import logging
from typing import Tuple, Dict
from pathlib import Path

import sys
import os

# Add parent directory to path to allow absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_engine.feature_extractor import FeatureExtractor
from ai_engine.preprocessing import AudioPreprocessor

logger = logging.getLogger(__name__)


class AudioStressDetector:
    """Ensemble-based audio stress detector"""
    
    def __init__(self, model_path: str = None):
        """
        Args:
            model_path: Path to saved model file
        """
        self.feature_extractor = FeatureExtractor()
        self.preprocessor = AudioPreprocessor()
        self.scaler = StandardScaler()
        self.ensemble = None
        
        if model_path and Path(model_path).exists():
            self.load_model(model_path)
            logger.info(f"Loaded model from {model_path}")
        else:
            self._initialize_ensemble()
            logger.info("Initialized new ensemble model")
    
    def _initialize_ensemble(self):
        """Initialize ensemble with base classifiers"""
        # Base classifiers
        lr = LogisticRegression(random_state=42, max_iter=1000)
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        gb = GradientBoostingClassifier(n_estimators=100, random_state=42)
        svm = SVC(probability=True, random_state=42)
        
        # Soft Voting Ensemble
        self.ensemble = VotingClassifier(
            estimators=[
                ('lr', lr),
                ('rf', rf),
                ('gb', gb),
                ('svm', svm)
            ],
            voting='soft',  # Use predicted probabilities
            n_jobs=-1
        )
        logger.info("Initialized ensemble with LR, RF, GB, SVM")
    
    def prepare_features(self, audio_path: str) -> np.ndarray:
        """Preprocess audio and extract features
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Feature vector
        """
        # Preprocess
        audio, sr = self.preprocessor.preprocess_from_file(audio_path)
        
        # Extract features
        features = self.feature_extractor.extract_all_features(audio)
        
        return features
    
    def train(self, X: np.ndarray, y: np.ndarray, test_size: float = 0.2) -> Dict:
        """Train the ensemble model
        
        Args:
            X: Feature matrix (n_samples, n_features)
            y: Labels (0: non-stressed, 1: stressed)
            test_size: Test set proportion
            
        Returns:
            Training metrics
        """
        logger.info(f"Training on {len(X)} samples")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train ensemble
        logger.info("Training ensemble...")
        self.ensemble.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.ensemble.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        conf_matrix = confusion_matrix(y_test, y_pred)
        class_report = classification_report(y_test, y_pred)
        
        logger.info(f"Training completed. Accuracy: {accuracy:.4f}")
        logger.info(f"Confusion Matrix:\n{conf_matrix}")
        logger.info(f"Classification Report:\n{class_report}")
        
        return {
            'accuracy': accuracy,
            'confusion_matrix': conf_matrix.tolist(),
            'classification_report': class_report
        }
    
    def predict(self, audio_path: str) -> Tuple[int, float]:
        """Predict stress level from audio file
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Tuple of (prediction, confidence)
            prediction: 0 (non-stressed) or 1 (stressed)
            confidence: Probability score
        """
        if self.ensemble is None:
            raise ValueError("Model not trained or loaded")
        
        try:
            # Extract features
            features = self.prepare_features(audio_path)
            features = features.reshape(1, -1)
            
            # Scale
            features_scaled = self.scaler.transform(features)
            
            # Predict
            prediction = self.ensemble.predict(features_scaled)[0]
            probabilities = self.ensemble.predict_proba(features_scaled)[0]
            confidence = probabilities[prediction]
            
            logger.info(f"Prediction: {'Stressed' if prediction == 1 else 'Non-stressed'} (confidence: {confidence:.4f})")
            
            return int(prediction), float(confidence)
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise
    
    def predict_from_array(self, audio: np.ndarray) -> Tuple[int, float]:
        """Predict stress from audio array
        
        Args:
            audio: Audio numpy array
            
        Returns:
            Tuple of (prediction, confidence)
        """
        if self.ensemble is None:
            raise ValueError("Model not trained or loaded")
        
        try:
            # Preprocess
            audio = self.preprocessor.preprocess(audio, self.preprocessor.target_sr)
            
            # Extract features
            features = self.feature_extractor.extract_all_features(audio)
            features = features.reshape(1, -1)
            
            # Scale and predict
            features_scaled = self.scaler.transform(features)
            prediction = self.ensemble.predict(features_scaled)[0]
            probabilities = self.ensemble.predict_proba(features_scaled)[0]
            confidence = probabilities[prediction]
            
            return int(prediction), float(confidence)
            
        except Exception as e:
            logger.error(f"Prediction from array failed: {e}")
            raise
    
    def save_model(self, save_path: str):
        """Save trained model
        
        Args:
            save_path: Path to save model
        """
        model_data = {
            'ensemble': self.ensemble,
            'scaler': self.scaler
        }
        
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(save_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Model saved to {save_path}")
    
    def load_model(self, load_path: str):
        """Load trained model
        
        Args:
            load_path: Path to model file
        """
        with open(load_path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.ensemble = model_data['ensemble']
        self.scaler = model_data['scaler']
        
        logger.info(f"Model loaded from {load_path}")
