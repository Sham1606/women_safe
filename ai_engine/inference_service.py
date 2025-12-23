"""Inference Service for Real-time Stress Detection

Provides API interface for backend to call AI models.
"""

import numpy as np
from typing import Dict, Optional
import logging
import base64
import io
import librosa
from pathlib import Path

from .hybrid_detector import HybridDetector

logger = logging.getLogger(__name__)


class InferenceService:
    """Service for real-time AI inference"""
    
    def __init__(self, model_path: str = "ai_engine/models/ensemble_model.pkl"):
        """
        Args:
            model_path: Path to trained model
        """
        self.hybrid_detector = HybridDetector(model_path=model_path)
        logger.info("InferenceService initialized")
    
    def analyze_audio_file(self, audio_path: str, heart_rate: int, temperature: float) -> Dict:
        """Analyze audio file with sensor data
        
        Args:
            audio_path: Path to audio file
            heart_rate: Heart rate in BPM
            temperature: Body temperature in Celsius
            
        Returns:
            Detection results
        """
        try:
            result = self.hybrid_detector.detect_from_audio_file(
                audio_path=audio_path,
                heart_rate=heart_rate,
                temperature=temperature
            )
            return result
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return self._error_response(str(e))
    
    def analyze_audio_base64(self, audio_base64: str, heart_rate: int, temperature: float) -> Dict:
        """Analyze base64-encoded audio with sensor data
        
        Args:
            audio_base64: Base64-encoded audio data
            heart_rate: Heart rate in BPM
            temperature: Body temperature in Celsius
            
        Returns:
            Detection results
        """
        try:
            # Decode base64 audio
            audio_bytes = base64.b64decode(audio_base64)
            
            # Load audio from bytes
            audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=22050)
            
            # Run detection
            result = self.hybrid_detector.detect_from_audio_array(
                audio=audio,
                heart_rate=heart_rate,
                temperature=temperature
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Base64 audio analysis failed: {e}")
            return self._error_response(str(e))
    
    def analyze_physiological_only(self, heart_rate: int, temperature: float) -> Dict:
        """Analyze physiological data only (no audio)
        
        Args:
            heart_rate: Heart rate in BPM
            temperature: Body temperature in Celsius
            
        Returns:
            Physiological analysis results
        """
        try:
            result = self.hybrid_detector.physio_analyzer.analyze_combined(
                heart_rate=heart_rate,
                temperature=temperature
            )
            return result
        except Exception as e:
            logger.error(f"Physiological analysis failed: {e}")
            return self._error_response(str(e))
    
    def batch_analyze(self, sensor_data_batch: list) -> list:
        """Batch analysis for multiple sensor readings
        
        Args:
            sensor_data_batch: List of sensor data dicts with keys:
                - audio_base64 (optional)
                - heart_rate
                - temperature
                
        Returns:
            List of detection results
        """
        results = []
        
        for data in sensor_data_batch:
            try:
                if 'audio_base64' in data and data['audio_base64']:
                    result = self.analyze_audio_base64(
                        audio_base64=data['audio_base64'],
                        heart_rate=data['heart_rate'],
                        temperature=data['temperature']
                    )
                else:
                    result = self.analyze_physiological_only(
                        heart_rate=data['heart_rate'],
                        temperature=data['temperature']
                    )
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Batch item failed: {e}")
                results.append(self._error_response(str(e)))
        
        return results
    
    def health_check(self) -> Dict:
        """Check if service is healthy
        
        Returns:
            Service status
        """
        try:
            # Verify model is loaded
            if self.hybrid_detector.audio_detector.ensemble is None:
                return {
                    'status': 'unhealthy',
                    'message': 'Model not loaded',
                    'ready': False
                }
            
            return {
                'status': 'healthy',
                'message': 'Service ready',
                'ready': True,
                'model_loaded': True
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'ready': False
            }
    
    def _error_response(self, error_message: str) -> Dict:
        """Generate error response"""
        return {
            'error': True,
            'message': error_message,
            'distress_detected': False
        }
