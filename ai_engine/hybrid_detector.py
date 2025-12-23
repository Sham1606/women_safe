"""Hybrid Stress Detection System

Combines audio stress detection and physiological sensor analysis
for comprehensive stress/distress detection.
"""

import numpy as np
from typing import Dict, Tuple
import logging
from datetime import datetime

from .audio_stress_detector import AudioStressDetector
from .physiological_analyzer import PhysiologicalAnalyzer

logger = logging.getLogger(__name__)


class HybridDetector:
    """Hybrid detection combining audio and physiological signals"""
    
    def __init__(self, model_path: str = None, audio_weight: float = 0.6, physio_weight: float = 0.4):
        """
        Args:
            model_path: Path to trained audio model
            audio_weight: Weight for audio stress detection
            physio_weight: Weight for physiological analysis
        """
        self.audio_detector = AudioStressDetector(model_path)
        self.physio_analyzer = PhysiologicalAnalyzer()
        
        # Weights for combining signals
        self.audio_weight = audio_weight
        self.physio_weight = physio_weight
        
        logger.info(f"Initialized HybridDetector (audio:{audio_weight}, physio:{physio_weight})")
    
    def detect_from_audio_file(self, audio_path: str, heart_rate: int, temperature: float) -> Dict:
        """Detect stress from audio file + physiological data
        
        Args:
            audio_path: Path to audio file
            heart_rate: Heart rate in BPM
            temperature: Body temperature in Celsius
            
        Returns:
            Combined detection results
        """
        try:
            # Audio stress detection
            audio_prediction, audio_confidence = self.audio_detector.predict(audio_path)
            
            # Physiological analysis
            physio_analysis = self.physio_analyzer.analyze_combined(heart_rate, temperature)
            physio_stress = physio_analysis['combined_stress_level']
            
            # Combined stress score (weighted average)
            combined_score = (self.audio_weight * audio_confidence * audio_prediction + 
                            self.physio_weight * physio_stress)
            
            # Final decision (threshold at 0.5)
            distress_detected = combined_score >= 0.5
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'audio_analysis': {
                    'prediction': 'stressed' if audio_prediction == 1 else 'non-stressed',
                    'confidence': audio_confidence,
                    'stress_score': audio_prediction * audio_confidence
                },
                'physiological_analysis': physio_analysis,
                'combined_stress_score': round(combined_score, 3),
                'distress_detected': distress_detected,
                'detection_mode': self._determine_mode(audio_prediction, physio_analysis['distress_detected']),
                'recommendation': self._get_recommendation(combined_score, distress_detected)
            }
            
            logger.info(f"Hybrid detection: Score={combined_score:.3f}, Distress={distress_detected}")
            
            return result
            
        except Exception as e:
            logger.error(f"Hybrid detection failed: {e}")
            raise
    
    def detect_from_audio_array(self, audio: np.ndarray, heart_rate: int, temperature: float) -> Dict:
        """Detect stress from audio array + physiological data
        
        Args:
            audio: Audio numpy array
            heart_rate: Heart rate in BPM
            temperature: Body temperature in Celsius
            
        Returns:
            Combined detection results
        """
        try:
            # Audio stress detection
            audio_prediction, audio_confidence = self.audio_detector.predict_from_array(audio)
            
            # Physiological analysis
            physio_analysis = self.physio_analyzer.analyze_combined(heart_rate, temperature)
            physio_stress = physio_analysis['combined_stress_level']
            
            # Combined stress score
            combined_score = (self.audio_weight * audio_confidence * audio_prediction + 
                            self.physio_weight * physio_stress)
            
            distress_detected = combined_score >= 0.5
            
            result = {
                'timestamp': datetime.now().isoformat(),
                'audio_analysis': {
                    'prediction': 'stressed' if audio_prediction == 1 else 'non-stressed',
                    'confidence': audio_confidence,
                    'stress_score': audio_prediction * audio_confidence
                },
                'physiological_analysis': physio_analysis,
                'combined_stress_score': round(combined_score, 3),
                'distress_detected': distress_detected,
                'detection_mode': self._determine_mode(audio_prediction, physio_analysis['distress_detected']),
                'recommendation': self._get_recommendation(combined_score, distress_detected)
            }
            
            logger.info(f"Hybrid detection: Score={combined_score:.3f}, Distress={distress_detected}")
            
            return result
            
        except Exception as e:
            logger.error(f"Hybrid detection from array failed: {e}")
            raise
    
    def _determine_mode(self, audio_prediction: int, physio_distress: bool) -> str:
        """Determine which mode triggered detection"""
        if audio_prediction == 1 and physio_distress:
            return "both"
        elif audio_prediction == 1:
            return "audio"
        elif physio_distress:
            return "physiological"
        else:
            return "none"
    
    def _get_recommendation(self, score: float, distress: bool) -> str:
        """Get action recommendation"""
        if distress:
            return "CRITICAL: Distress detected. Activate emergency alert system."
        elif score > 0.4:
            return "WARNING: Elevated stress levels. Continue monitoring."
        else:
            return "Normal state. No action required."
