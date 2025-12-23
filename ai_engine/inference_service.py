"""Real-time Inference Service

Provides inference API for real-time stress detection.
Can be called by backend or used as standalone service.
"""

import numpy as np
import logging
from pathlib import Path
from typing import Dict, Optional, Union
import base64
import io
import soundfile as sf

from .hybrid_detector import HybridStressDetector
from .audio_stress_detector import AudioStressDetector
from .physiological_analyzer import PhysiologicalAnalyzer
from .feature_extractor import AudioFeatureExtractor
from .preprocessing import preprocess_audio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InferenceService:
    """Real-time stress detection inference service"""
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        scaler_path: Optional[str] = None
    ):
        """
        Args:
            model_path: Path to trained model
            scaler_path: Path to feature scaler
        """
        # Default model paths
        if model_path is None:
            model_path = "ai_engine/models/audio_stress_model.pkl"
        if scaler_path is None:
            scaler_path = "ai_engine/models/scaler.pkl"
        
        # Initialize components
        self.audio_detector = AudioStressDetector(model_path, scaler_path)
        self.physio_analyzer = PhysiologicalAnalyzer()
        self.feature_extractor = AudioFeatureExtractor()
        self.hybrid_detector = HybridStressDetector(
            audio_detector=self.audio_detector,
            physio_analyzer=self.physio_analyzer,
            feature_extractor=self.feature_extractor
        )
        
        logger.info("Inference service initialized and ready")
    
    def analyze_audio_file(self, audio_path: str) -> Dict:
        """Analyze audio file for stress detection
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Analysis results
        """
        try:
            # Load and preprocess audio
            audio, sr = self.feature_extractor.load_audio(audio_path)
            audio_preprocessed = preprocess_audio(audio, sr)
            
            # Extract features and predict
            features = self.feature_extractor.extract_all_features(audio_preprocessed)
            prediction, confidence = self.audio_detector.predict(features)
            
            result = {
                'success': True,
                'stress_detected': bool(prediction == 1),
                'confidence': float(confidence),
                'audio_duration': float(len(audio) / sr),
                'modality': 'audio_only'
            }
            
            logger.info(f"Audio analysis: stress={result['stress_detected']}, confidence={confidence:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_audio_bytes(self, audio_bytes: bytes, sample_rate: int = 22050) -> Dict:
        """Analyze audio from bytes (for IoT device streaming)
        
        Args:
            audio_bytes: Raw audio bytes
            sample_rate: Audio sample rate
            
        Returns:
            Analysis results
        """
        try:
            # Convert bytes to numpy array
            audio_io = io.BytesIO(audio_bytes)
            audio, sr = sf.read(audio_io)
            
            # Preprocess and analyze
            audio_preprocessed = preprocess_audio(audio, sr)
            features = self.feature_extractor.extract_all_features(audio_preprocessed)
            prediction, confidence = self.audio_detector.predict(features)
            
            result = {
                'success': True,
                'stress_detected': bool(prediction == 1),
                'confidence': float(confidence),
                'modality': 'audio_only'
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Audio bytes analysis failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_audio_base64(self, audio_base64: str) -> Dict:
        """Analyze audio from base64 string (for API requests)
        
        Args:
            audio_base64: Base64 encoded audio
            
        Returns:
            Analysis results
        """
        try:
            # Decode base64
            audio_bytes = base64.b64decode(audio_base64)
            return self.analyze_audio_bytes(audio_bytes)
            
        except Exception as e:
            logger.error(f"Base64 audio analysis failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_physiological(self, heart_rate: float, temperature: float) -> Dict:
        """Analyze physiological data only
        
        Args:
            heart_rate: Heart rate in bpm
            temperature: Body temperature in Celsius
            
        Returns:
            Analysis results
        """
        try:
            result = self.physio_analyzer.analyze_combined(heart_rate, temperature)
            
            response = {
                'success': True,
                'stress_detected': result['stress_detected'],
                'confidence': result['confidence'],
                'combined_score': result['combined_score'],
                'alert_recommended': result['alert_recommended'],
                'heart_rate_analysis': result['heart_rate'],
                'temperature_analysis': result['temperature'],
                'modality': 'physiological_only'
            }
            
            return response
            
        except Exception as e:
            logger.error(f"Physiological analysis failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_multimodal(
        self,
        audio_data: Optional[Union[str, bytes]] = None,
        heart_rate: Optional[float] = None,
        temperature: Optional[float] = None
    ) -> Dict:
        """Complete multimodal analysis
        
        Args:
            audio_data: Audio file path or bytes
            heart_rate: Heart rate in bpm
            temperature: Body temperature in Celsius
            
        Returns:
            Comprehensive analysis results
        """
        try:
            # Process audio if provided
            audio_array = None
            if audio_data is not None:
                if isinstance(audio_data, str):
                    audio_array, sr = self.feature_extractor.load_audio(audio_data)
                elif isinstance(audio_data, bytes):
                    audio_io = io.BytesIO(audio_data)
                    audio_array, sr = sf.read(audio_io)
                
                if audio_array is not None:
                    audio_array = preprocess_audio(audio_array, sr)
            
            # Multimodal analysis
            result = self.hybrid_detector.analyze_multimodal(
                audio_data=audio_array,
                heart_rate=heart_rate,
                temperature=temperature
            )
            
            # Get recommendations
            recommendations = self.hybrid_detector.get_recommendation(result)
            
            response = {
                'success': True,
                'stress_detected': result['stress_detected'],
                'confidence': result['confidence'],
                'combined_score': result['combined_score'],
                'modalities_used': result['modalities_used'],
                'recommendations': recommendations,
                'detailed_analysis': {
                    'audio': result['audio_analysis'],
                    'physiological': result['physiological_analysis']
                }
            }
            
            logger.info(
                f"Multimodal analysis: stress={result['stress_detected']}, "
                f"score={result['combined_score']:.3f}, "
                f"modalities={result['modalities_used']}"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Multimodal analysis failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Singleton instance for API usage
_inference_service = None

def get_inference_service() -> InferenceService:
    """Get singleton inference service instance"""
    global _inference_service
    if _inference_service is None:
        _inference_service = InferenceService()
    return _inference_service