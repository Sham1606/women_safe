"""Hybrid Stress Detector

Combines audio stress detection and physiological sensor analysis
for final stress classification decision.
"""

from typing import Dict, Tuple, Optional
import numpy as np

from .audio_stress_detector import AudioStressDetector
from .physiological_analyzer import PhysiologicalAnalyzer


class HybridStressDetector:
    """Hybrid detector combining audio and physiological signals"""
    
    def __init__(self, 
                 audio_model_path: Optional[str] = None,
                 audio_weight: float = 0.6,
                 physio_weight: float = 0.4):
        """
        Args:
            audio_model_path: Path to trained audio stress model
            audio_weight: Weight for audio stress detection (0-1)
            physio_weight: Weight for physiological analysis (0-1)
        """
        self.audio_detector = AudioStressDetector(model_path=audio_model_path)
        self.physio_analyzer = PhysiologicalAnalyzer()
        
        # Ensure weights sum to 1
        total = audio_weight + physio_weight
        self.audio_weight = audio_weight / total
        self.physio_weight = physio_weight / total
    
    def detect_stress(self, 
                     audio_input,
                     heart_rate: int,
                     temperature: float) -> Dict:
        """Detect stress using both audio and physiological data
        
        Args:
            audio_input: Audio file path or numpy array
            heart_rate: Heart rate in BPM
            temperature: Body temperature in Celsius
            
        Returns:
            Comprehensive stress detection result
        """
        # Audio stress detection
        try:
            audio_pred, audio_conf = self.audio_detector.predict(audio_input)
            audio_stress_detected = bool(audio_pred == 1)
        except Exception as e:
            print(f"Audio detection error: {e}")
            audio_stress_detected = False
            audio_conf = 0.0
        
        # Physiological analysis
        physio_result = self.physio_analyzer.analyze_combined(heart_rate, temperature)
        physio_stress_detected = physio_result['stress_detected']
        physio_conf = physio_result['confidence']
        
        # Weighted fusion
        weighted_confidence = (
            self.audio_weight * audio_conf + 
            self.physio_weight * physio_conf
        )
        
        # Decision logic:
        # 1. If both detect stress -> HIGH confidence
        # 2. If one detects stress with high confidence -> MEDIUM confidence
        # 3. If neither detects stress -> NO stress
        
        if audio_stress_detected and physio_stress_detected:
            final_decision = True
            decision_confidence = max(0.9, weighted_confidence)
            decision_reason = "Both audio and physiological indicators show stress"
        elif audio_stress_detected and audio_conf >= 0.75:
            final_decision = True
            decision_confidence = audio_conf * 0.85
            decision_reason = "High confidence audio stress detected"
        elif physio_stress_detected and physio_conf >= 0.80:
            final_decision = True
            decision_confidence = physio_conf * 0.85
            decision_reason = "High confidence physiological stress detected"
        elif audio_stress_detected or physio_stress_detected:
            final_decision = True
            decision_confidence = weighted_confidence
            decision_reason = "One modality detected stress"
        else:
            final_decision = False
            decision_confidence = 1 - weighted_confidence
            decision_reason = "No stress indicators detected"
        
        return {
            'stress_detected': final_decision,
            'confidence': float(decision_confidence),
            'decision_reason': decision_reason,
            'audio_analysis': {
                'stress_detected': audio_stress_detected,
                'confidence': float(audio_conf)
            },
            'physiological_analysis': physio_result,
            'fusion_weights': {
                'audio': self.audio_weight,
                'physiological': self.physio_weight
            }
        }
    
    def detect_with_manual_trigger(self,
                                   audio_input,
                                   heart_rate: int,
                                   temperature: float,
                                   manual_trigger: bool) -> Dict:
        """Detect stress with manual trigger option
        
        Args:
            audio_input: Audio input
            heart_rate: Heart rate in BPM
            temperature: Temperature in Celsius
            manual_trigger: True if user pressed emergency button
            
        Returns:
            Detection result with manual trigger consideration
        """
        if manual_trigger:
            # Manual trigger overrides AI detection
            return {
                'stress_detected': True,
                'confidence': 1.0,
                'decision_reason': 'Manual emergency trigger activated',
                'trigger_type': 'manual',
                'audio_analysis': {'skipped': True},
                'physiological_analysis': self.physio_analyzer.analyze_combined(heart_rate, temperature)
            }
        else:
            # Normal AI-based detection
            result = self.detect_stress(audio_input, heart_rate, temperature)
            result['trigger_type'] = 'ai_automatic'
            return result