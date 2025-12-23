"""Hybrid Stress Detector

Combines audio analysis and physiological sensor data for comprehensive stress detection.
Implements weighted fusion of multiple detection modalities.
"""

import numpy as np
import logging
from typing import Dict, Optional, Tuple
from .audio_stress_detector import AudioStressDetector
from .physiological_analyzer import PhysiologicalAnalyzer
from .feature_extractor import AudioFeatureExtractor

logger = logging.getLogger(__name__)


class HybridStressDetector:
    """Combines audio and physiological analysis for stress detection"""
    
    def __init__(
        self,
        audio_detector: Optional[AudioStressDetector] = None,
        physio_analyzer: Optional[PhysiologicalAnalyzer] = None,
        feature_extractor: Optional[AudioFeatureExtractor] = None,
        audio_weight: float = 0.6,
        physio_weight: float = 0.4
    ):
        """
        Args:
            audio_detector: Audio stress detector instance
            physio_analyzer: Physiological analyzer instance
            feature_extractor: Audio feature extractor
            audio_weight: Weight for audio analysis (0-1)
            physio_weight: Weight for physiological analysis (0-1)
        """
        self.audio_detector = audio_detector or AudioStressDetector()
        self.physio_analyzer = physio_analyzer or PhysiologicalAnalyzer()
        self.feature_extractor = feature_extractor or AudioFeatureExtractor()
        
        # Normalize weights
        total_weight = audio_weight + physio_weight
        self.audio_weight = audio_weight / total_weight
        self.physio_weight = physio_weight / total_weight
        
        logger.info(
            f"HybridStressDetector initialized with weights: "
            f"audio={self.audio_weight:.2f}, physio={self.physio_weight:.2f}"
        )
    
    def analyze_multimodal(
        self,
        audio_data: Optional[np.ndarray] = None,
        audio_features: Optional[np.ndarray] = None,
        heart_rate: Optional[float] = None,
        temperature: Optional[float] = None
    ) -> Dict:
        """Perform multimodal stress analysis
        
        Args:
            audio_data: Raw audio time series (optional)
            audio_features: Pre-extracted audio features (optional)
            heart_rate: Heart rate in bpm (optional)
            temperature: Body temperature in Celsius (optional)
            
        Returns:
            Comprehensive analysis results with stress detection
        """
        results = {
            'audio_analysis': None,
            'physiological_analysis': None,
            'combined_score': 0.0,
            'stress_detected': False,
            'confidence': 0.0,
            'modalities_used': []
        }
        
        # Audio analysis
        if audio_data is not None or audio_features is not None:
            try:
                if audio_features is None:
                    audio_features = self.feature_extractor.extract_all_features(audio_data)
                
                audio_prediction, audio_confidence = self.audio_detector.predict(audio_features)
                
                results['audio_analysis'] = {
                    'prediction': audio_prediction,
                    'confidence': audio_confidence,
                    'stress_detected': audio_prediction == 1
                }
                results['modalities_used'].append('audio')
                
                logger.debug(f"Audio analysis: prediction={audio_prediction}, confidence={audio_confidence:.3f}")
            except Exception as e:
                logger.error(f"Audio analysis failed: {e}")
        
        # Physiological analysis
        if heart_rate is not None and temperature is not None:
            try:
                physio_result = self.physio_analyzer.analyze_combined(heart_rate, temperature)
                results['physiological_analysis'] = physio_result
                results['modalities_used'].append('physiological')
                
                logger.debug(f"Physiological analysis: score={physio_result['combined_score']:.3f}")
            except Exception as e:
                logger.error(f"Physiological analysis failed: {e}")
        
        # Combined decision
        if len(results['modalities_used']) > 0:
            results['combined_score'], results['stress_detected'], results['confidence'] = \
                self._fuse_predictions(results)
        
        logger.info(
            f"Hybrid detection: Stress={results['stress_detected']}, "
            f"Score={results['combined_score']:.3f}, "
            f"Modalities={results['modalities_used']}"
        )
        
        return results
    
    def _fuse_predictions(self, results: Dict) -> Tuple[float, bool, float]:
        """Fuse predictions from multiple modalities
        
        Args:
            results: Dictionary containing analysis results
            
        Returns:
            (combined_score, stress_detected, confidence)
        """
        scores = []
        weights = []
        
        # Audio modality
        if results['audio_analysis'] is not None:
            audio_score = results['audio_analysis']['confidence']
            scores.append(audio_score)
            weights.append(self.audio_weight)
        
        # Physiological modality
        if results['physiological_analysis'] is not None:
            physio_score = results['physiological_analysis']['combined_score']
            scores.append(physio_score)
            weights.append(self.physio_weight)
        
        # Weighted average
        if len(scores) == 0:
            return 0.0, False, 0.0
        
        # Normalize weights
        weights = np.array(weights)
        weights = weights / weights.sum()
        
        combined_score = np.average(scores, weights=weights)
        
        # Decision threshold
        stress_detected = combined_score >= 0.5
        
        # Confidence based on agreement between modalities
        if len(scores) > 1:
            # High confidence if both modalities agree
            score_std = np.std(scores)
            confidence = combined_score * (1 - min(score_std, 0.3))
        else:
            confidence = combined_score
        
        return float(combined_score), stress_detected, float(confidence)
    
    def analyze_audio_only(self, audio_data: np.ndarray) -> Dict:
        """Analyze audio data only
        
        Args:
            audio_data: Raw audio time series
            
        Returns:
            Audio analysis results
        """
        return self.analyze_multimodal(audio_data=audio_data)
    
    def analyze_physiological_only(self, heart_rate: float, temperature: float) -> Dict:
        """Analyze physiological data only
        
        Args:
            heart_rate: Heart rate in bpm
            temperature: Body temperature in Celsius
            
        Returns:
            Physiological analysis results
        """
        return self.analyze_multimodal(heart_rate=heart_rate, temperature=temperature)
    
    def get_recommendation(self, analysis_result: Dict) -> Dict:
        """Get action recommendations based on analysis
        
        Args:
            analysis_result: Result from analyze_multimodal()
            
        Returns:
            Recommended actions
        """
        recommendations = {
            'trigger_alert': False,
            'activate_camera': False,
            'activate_buzzer': False,
            'notify_guardians': False,
            'priority': 'low',
            'message': ''
        }
        
        score = analysis_result['combined_score']
        stress_detected = analysis_result['stress_detected']
        
        if stress_detected:
            if score >= 0.8:
                recommendations['trigger_alert'] = True
                recommendations['activate_camera'] = True
                recommendations['activate_buzzer'] = True
                recommendations['notify_guardians'] = True
                recommendations['priority'] = 'critical'
                recommendations['message'] = 'High stress detected - immediate action required'
            elif score >= 0.6:
                recommendations['trigger_alert'] = True
                recommendations['activate_camera'] = True
                recommendations['notify_guardians'] = True
                recommendations['priority'] = 'high'
                recommendations['message'] = 'Moderate stress detected - alerting guardians'
            else:
                recommendations['trigger_alert'] = True
                recommendations['priority'] = 'medium'
                recommendations['message'] = 'Mild stress detected - monitoring situation'
        else:
            recommendations['message'] = 'No stress detected - normal monitoring'
        
        logger.info(f"Recommendations: {recommendations['message']}")
        return recommendations