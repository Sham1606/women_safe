"""Ensemble Audio Stress Detector

Implements soft voting ensemble with:
- Logistic Regression
- Random Forest
- Gradient Boosting
- Support Vector Machine
"""

import numpy as np
import pickle
from sklearn.ensemble import VotingClassifier, RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from typing import Tuple, Optional
import os

from .feature_extractor import AudioFeatureExtractor
from .preprocessing import AudioPreprocessor


class AudioStressDetector:
    """Ensemble-based audio stress detection"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.feature_extractor = AudioFeatureExtractor()
        self.preprocessor = AudioPreprocessor()
        self.scaler = StandardScaler()
        self.model = None
        self.model_path = model_path or 'ai_engine/models/audio_stress_model.pkl'
        
        # Load model if exists
        if os.path.exists(self.model_path):
            self.load_model()
    
    def create_ensemble(self) -> VotingClassifier:
        """Create soft voting ensemble classifier"""
        # Define base classifiers
        lr = LogisticRegression(random_state=42, max_iter=1000)
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        gb = GradientBoostingClassifier(n_estimators=100, random_state=42)
        svm = SVC(kernel='rbf', probability=True, random_state=42)
        
        # Create voting ensemble
        ensemble = VotingClassifier(
            estimators=[
                ('lr', lr),
                ('rf', rf),
                ('gb', gb),
                ('svm', svm)
            ],
            voting='soft'  # Soft voting uses predicted probabilities
        )
        
        return ensemble
    
    def train(self, X: np.ndarray, y: np.ndarray, test_size: float = 0.2) -> dict:
        """Train ensemble model
        
        Args:
            X: Feature matrix (n_samples, n_features)
            y: Labels (n_samples,) - 0: non-stressed, 1: stressed
            test_size: Test split ratio
            
        Returns:
            Training metrics dictionary
        """
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Create and train ensemble
        self.model = self.create_ensemble()
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        # Get predictions
        y_pred = self.model.predict(X_test_scaled)
        
        from sklearn.metrics import classification_report, confusion_matrix
        
        metrics = {
            'train_accuracy': train_score,
            'test_accuracy': test_score,
            'classification_report': classification_report(y_test, y_pred),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
        }
        
        return metrics
    
    def predict(self, audio_input) -> Tuple[int, float]:
        """Predict stress level from audio
        
        Args:
            audio_input: Audio file path or numpy array
            
        Returns:
            (prediction, confidence) - prediction: 0 or 1, confidence: 0.0-1.0
        """
        if self.model is None:
            raise ValueError("Model not loaded. Train or load a model first.")
        
        # Preprocess if it's a file path
        if isinstance(audio_input, str):
            audio, sr = self.preprocessor.load_and_preprocess(audio_input)
        else:
            audio = audio_input
        
        # Extract features
        features = self.feature_extractor.extract_features(audio)
        
        if features is None:
            return 0, 0.0
        
        # Scale features
        features_scaled = self.scaler.transform(features.reshape(1, -1))
        
        # Predict
        prediction = self.model.predict(features_scaled)[0]
        probabilities = self.model.predict_proba(features_scaled)[0]
        confidence = probabilities[prediction]
        
        return int(prediction), float(confidence)
    
    def predict_with_details(self, audio_input) -> dict:
        """Predict with detailed information from each classifier"""
        if self.model is None:
            raise ValueError("Model not loaded.")
        
        # Extract features
        if isinstance(audio_input, str):
            audio, sr = self.preprocessor.load_and_preprocess(audio_input)
        else:
            audio = audio_input
        
        features = self.feature_extractor.extract_features(audio)
        if features is None:
            return {'error': 'Feature extraction failed'}
        
        features_scaled = self.scaler.transform(features.reshape(1, -1))
        
        # Get predictions from each classifier
        predictions_detail = {}
        for name, clf in self.model.named_estimators_.items():
            pred = clf.predict(features_scaled)[0]
            prob = clf.predict_proba(features_scaled)[0]
            predictions_detail[name] = {
                'prediction': int(pred),
                'probability_stressed': float(prob[1])
            }
        
        # Overall prediction
        final_pred = self.model.predict(features_scaled)[0]
        final_prob = self.model.predict_proba(features_scaled)[0]
        
        return {
            'final_prediction': int(final_pred),
            'final_confidence': float(final_prob[final_pred]),
            'stress_probability': float(final_prob[1]),
            'classifier_details': predictions_detail
        }
    
    def save_model(self, path: Optional[str] = None):
        """Save trained model and scaler"""
        save_path = path or self.model_path
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler
        }
        
        with open(save_path, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"Model saved to {save_path}")
    
    def load_model(self, path: Optional[str] = None):
        """Load trained model and scaler"""
        load_path = path or self.model_path
        
        if not os.path.exists(load_path):
            raise FileNotFoundError(f"Model file not found: {load_path}")
        
        with open(load_path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        
        print(f"Model loaded from {load_path}")