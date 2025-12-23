"""Real-time Inference Service for Stress Detection

Provides API for backend to call AI engine for stress analysis.
"""

import os
import base64
import io
import numpy as np
import soundfile as sf
from typing import Dict, Optional

from .hybrid_detector import HybridStressDetector
from .audio_stress_detector import AudioStressDetector
from .physiological_analyzer import PhysiologicalAnalyzer


class InferenceService:
    """Real-time stress detection inference service"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.hybrid_detector = HybridStressDetector(audio_model_path=model_path)
        self.audio_detector = AudioStressDetector(model_path=model_path)
        self.physio_analyzer = PhysiologicalAnalyzer()
    
    def analyze_audio_only(self, audio_input) -> Dict:
        """Analyze audio stress only
        
        Args:
            audio_input: Audio file path, numpy array, or base64 string
            
        Returns:
            Analysis result dictionary
        """
        try:
            # Handle base64 audio
            if isinstance(audio_input, str) and audio_input.startswith('data:audio'):
                audio_input = self._decode_base64_audio(audio_input)
            
            prediction, confidence = self.audio_detector.predict(audio_input)
            
            return {
                'success': True,
                'stress_detected': bool(prediction == 1),
                'confidence': float(confidence),
                'analysis_type': 'audio_only'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'stress_detected': False,
                'confidence': 0.0
            }
    
    def analyze_physiological_only(self, heart_rate: int, temperature: float) -> Dict:
        """Analyze physiological data only
        
        Args:
            heart_rate: Heart rate in BPM
            temperature: Body temperature in Celsius
            
        Returns:
            Analysis result dictionary
        """
        try:
            result = self.physio_analyzer.analyze_combined(heart_rate, temperature)
            result['success'] = True
            result['analysis_type'] = 'physiological_only'
            return result
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'stress_detected': False,
                'confidence': 0.0
            }
    
    def analyze_hybrid(self, 
                      audio_input,
                      heart_rate: int,
                      temperature: float,
                      manual_trigger: bool = False) -> Dict:
        """Hybrid analysis combining audio and physiological data
        
        Args:
            audio_input: Audio data
            heart_rate: Heart rate in BPM
            temperature: Temperature in Celsius
            manual_trigger: Manual emergency trigger status
            
        Returns:
            Comprehensive analysis result
        """
        try:
            # Handle base64 audio
            if isinstance(audio_input, str) and 'base64' in audio_input:
                audio_input = self._decode_base64_audio(audio_input)
            
            result = self.hybrid_detector.detect_with_manual_trigger(
                audio_input=audio_input,
                heart_rate=heart_rate,
                temperature=temperature,
                manual_trigger=manual_trigger
            )
            
            result['success'] = True
            result['analysis_type'] = 'hybrid'
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'stress_detected': manual_trigger,  # Fallback to manual trigger
                'confidence': 1.0 if manual_trigger else 0.0,
                'decision_reason': 'Error in analysis, using manual trigger status'
            }
    
    def _decode_base64_audio(self, base64_string: str) -> np.ndarray:
        """Decode base64 audio string to numpy array
        
        Args:
            base64_string: Base64 encoded audio
            
        Returns:
            Audio numpy array
        """
        # Remove data URI prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Decode base64
        audio_bytes = base64.b64decode(base64_string)
        
        # Convert to numpy array
        audio_io = io.BytesIO(audio_bytes)
        audio_data, sample_rate = sf.read(audio_io)
        
        return audio_data
    
    def batch_analyze(self, requests: list) -> list:
        """Batch processing for multiple requests
        
        Args:
            requests: List of analysis request dictionaries
            
        Returns:
            List of analysis results
        """
        results = []
        
        for request in requests:
            analysis_type = request.get('type', 'hybrid')
            
            if analysis_type == 'audio_only':
                result = self.analyze_audio_only(request['audio'])
            elif analysis_type == 'physiological_only':
                result = self.analyze_physiological_only(
                    request['heart_rate'],
                    request['temperature']
                )
            else:
                result = self.analyze_hybrid(
                    request['audio'],
                    request['heart_rate'],
                    request['temperature'],
                    request.get('manual_trigger', False)
                )
            
            results.append(result)
        
        return results


# Global inference service instance
_inference_service = None

def get_inference_service(model_path: Optional[str] = None) -> InferenceService:
    """Get or create inference service singleton"""
    global _inference_service
    
    if _inference_service is None:
        _inference_service = InferenceService(model_path=model_path)
    
    return _inference_service