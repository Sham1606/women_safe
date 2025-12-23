"""Ensemble Audio Stress Detector

Implements Soft Voting Ensemble with multiple base classifiers:
- Logistic Regression
- Random Forest
- Gradient Boosting
- Support Vector Machine
"""

import numpy as np
import joblib
from sklearn.ensemble import VotingClassifier, RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class AudioStressDetector:
    """Ensemble-based audio stress detection model"""
    
    def __init__(self, model_path: Optional[str] = None, scaler_path: Optional[str] = None):
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.model = None
        self.scaler = None
        
        if model_path and scaler_path:
            self.load_model(model_path, scaler_path)
    
    def build_ensemble(self) -> VotingClassifier:
        """Build soft voting ensemble classifier"""
        
        # Base classifiers
        lr = LogisticRegression(random_state=42, max_iter=1000)
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        gb = GradientBoostingClassifier(n_estimators=100, random_state=42)
        svm = SVC(probability=True, random_state=42)
        
        # Soft voting ensemble
        ensemble = VotingClassifier(
            estimators=[
                ('lr', lr),
                ('rf', rf),
                ('gb', gb),
                ('svm', svm)
            ],
            voting='soft',
            weights=[1, 2, 2, 1]  # RF and GB get higher weights
        )
        
        logger.info("Built ensemble with 4 base classifiers (LR, RF, GB, SVM)")
        return ensemble
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> Tuple[float, dict]:
        """Train the ensemble model
        
        Args:
            X_train: Training features (n_samples, n_features)
            y_train: Training labels (0=non-stressed, 1=stressed)
            
        Returns:
            Training accuracy and metrics
        """
        logger.info(f"Training on {X_train.shape[0]} samples with {X_train.shape[1]} features")
        
        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X_train)
        
        # Build and train ensemble
        self.model = self.build_ensemble()
        self.model.fit(X_scaled, y_train)
        
        # Calculate training accuracy
        train_acc = self.model.score(X_scaled, y_train)
        
        metrics = {
            'train_accuracy': train_acc,
            'n_samples': X_train.shape[0],
            'n_features': X_train.shape[1]
        }
        
        logger.info(f"Training completed. Accuracy: {train_acc:.4f}")
        return train_acc, metrics
    
    def predict(self, features: np.ndarray) -> Tuple[int, float]:
        """Predict stress level for audio features
        
        Args:
            features: Audio features array
            
        Returns:
            (prediction, confidence_score)
            prediction: 0=non-stressed, 1=stressed
            confidence_score: probability of stress (0.0 to 1.0)
        """
        if self.model is None or self.scaler is None:
            raise ValueError("Model not loaded. Call load_model() or train() first.")
        
        # Ensure features are 2D
        if features.ndim == 1:
            features = features.reshape(1, -1)
        
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        # Predict
        prediction = self.model.predict(features_scaled)[0]
        probabilities = self.model.predict_proba(features_scaled)[0]
        confidence = probabilities[1]  # Probability of stress
        
        logger.debug(f"Prediction: {prediction}, Confidence: {confidence:.4f}")
        return int(prediction), float(confidence)
    
    def save_model(self, model_path: str, scaler_path: str):
        """Save trained model and scaler"""
        if self.model is None or self.scaler is None:
            raise ValueError("No model to save. Train the model first.")
        
        joblib.dump(self.model, model_path)
        joblib.dump(self.scaler, scaler_path)
        logger.info(f"Model saved to {model_path}, Scaler saved to {scaler_path}")
    
    def load_model(self, model_path: str, scaler_path: str):
        """Load pre-trained model and scaler"""
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        logger.info(f"Model loaded from {model_path}")
    
    def get_feature_importance(self) -> dict:
        """Get feature importance from Random Forest classifier"""
        if self.model is None:
            raise ValueError("Model not loaded")
        
        # Extract RF from ensemble
        rf_model = self.model.named_estimators_['rf']
        importances = rf_model.feature_importances_
        
        return {
            'feature_importances': importances.tolist(),
            'top_10_indices': np.argsort(importances)[-10:][::-1].tolist()
        }