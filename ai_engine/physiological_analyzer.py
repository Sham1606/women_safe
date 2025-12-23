"""Physiological Sensor Analysis

Analyzes physiological signals for stress detection:
- Heart rate monitoring
- Body temperature analysis
- Threshold-based anomaly detection
"""

import numpy as np
from typing import Dict, Tuple
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class PhysiologicalAnalyzer:
    """Analyze physiological sensor data for stress indicators"""
    
    # Normal ranges
    NORMAL_HEART_RATE_MIN = 60
    NORMAL_HEART_RATE_MAX = 100
    ELEVATED_HEART_RATE_THRESHOLD = 110  # Stress indicator
    
    NORMAL_TEMP_MIN = 36.1  # Celsius
    NORMAL_TEMP_MAX = 37.2
    STRESS_TEMP_THRESHOLD = 37.5  # Elevated temperature
    
    def __init__(self):
        logger.info("Initialized PhysiologicalAnalyzer")
    
    def analyze_heart_rate(self, heart_rate: int) -> Dict:
        """Analyze heart rate for stress indicators
        
        Args:
            heart_rate: Heart rate in BPM
            
        Returns:
            Analysis results
        """
        if heart_rate < self.NORMAL_HEART_RATE_MIN:
            status = "low"
            stress_level = 0.0
        elif heart_rate <= self.NORMAL_HEART_RATE_MAX:
            status = "normal"
            stress_level = 0.0
        elif heart_rate <= self.ELEVATED_HEART_RATE_THRESHOLD:
            status = "elevated"
            # Linear scale between normal and elevated
            stress_level = (heart_rate - self.NORMAL_HEART_RATE_MAX) / \
                          (self.ELEVATED_HEART_RATE_THRESHOLD - self.NORMAL_HEART_RATE_MAX)
        else:
            status = "high"
            stress_level = 1.0
        
        logger.debug(f"Heart rate: {heart_rate} BPM -> {status} (stress: {stress_level:.2f})")
        
        return {
            'heart_rate': heart_rate,
            'status': status,
            'stress_level': round(stress_level, 3),
            'is_abnormal': heart_rate > self.ELEVATED_HEART_RATE_THRESHOLD
        }
    
    def analyze_temperature(self, temperature: float) -> Dict:
        """Analyze body temperature for stress indicators
        
        Args:
            temperature: Body temperature in Celsius
            
        Returns:
            Analysis results
        """
        if temperature < self.NORMAL_TEMP_MIN:
            status = "low"
            stress_level = 0.0
        elif temperature <= self.NORMAL_TEMP_MAX:
            status = "normal"
            stress_level = 0.0
        elif temperature <= self.STRESS_TEMP_THRESHOLD:
            status = "elevated"
            # Linear scale
            stress_level = (temperature - self.NORMAL_TEMP_MAX) / \
                          (self.STRESS_TEMP_THRESHOLD - self.NORMAL_TEMP_MAX)
        else:
            status = "high"
            stress_level = 1.0
        
        logger.debug(f"Temperature: {temperature}°C -> {status} (stress: {stress_level:.2f})")
        
        return {
            'temperature': temperature,
            'status': status,
            'stress_level': round(stress_level, 3),
            'is_abnormal': temperature > self.STRESS_TEMP_THRESHOLD
        }
    
    def analyze_combined(self, heart_rate: int, temperature: float) -> Dict:
        """Analyze both heart rate and temperature
        
        Args:
            heart_rate: Heart rate in BPM
            temperature: Body temperature in Celsius
            
        Returns:
            Combined analysis
        """
        hr_analysis = self.analyze_heart_rate(heart_rate)
        temp_analysis = self.analyze_temperature(temperature)
        
        # Combined stress level (average)
        combined_stress = (hr_analysis['stress_level'] + temp_analysis['stress_level']) / 2
        
        # Determine if distress detected
        distress_detected = hr_analysis['is_abnormal'] or temp_analysis['is_abnormal']
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'heart_rate_analysis': hr_analysis,
            'temperature_analysis': temp_analysis,
            'combined_stress_level': round(combined_stress, 3),
            'distress_detected': distress_detected,
            'recommendation': self._get_recommendation(combined_stress, distress_detected)
        }
        
        logger.info(f"Combined analysis: Stress={combined_stress:.2f}, Distress={distress_detected}")
        
        return result
    
    def _get_recommendation(self, stress_level: float, distress: bool) -> str:
        """Get recommendation based on stress level"""
        if distress:
            return "ALERT: Abnormal physiological signals detected. Immediate attention required."
        elif stress_level > 0.7:
            return "High stress level detected. Monitor closely."
        elif stress_level > 0.4:
            return "Moderate stress level. Continue monitoring."
        else:
            return "Normal physiological state."
