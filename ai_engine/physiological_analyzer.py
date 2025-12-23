"""Physiological Stress Analyzer

Analyzes heart rate and temperature data for stress detection.
Uses threshold-based approach with abnormal pattern detection.
"""

import numpy as np
import logging
from typing import Dict, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PhysiologicalThresholds:
    """Thresholds for stress detection"""
    # Heart rate thresholds (bpm)
    heart_rate_normal_min: int = 60
    heart_rate_normal_max: int = 100
    heart_rate_stress_threshold: int = 110
    heart_rate_high_stress_threshold: int = 130
    
    # Temperature thresholds (Celsius)
    temperature_normal_min: float = 36.1
    temperature_normal_max: float = 37.2
    temperature_stress_threshold: float = 37.5
    temperature_low_threshold: float = 35.5


class PhysiologicalAnalyzer:
    """Analyzes physiological sensor data for stress detection"""
    
    def __init__(self, thresholds: PhysiologicalThresholds = None):
        self.thresholds = thresholds or PhysiologicalThresholds()
        logger.info("PhysiologicalAnalyzer initialized with thresholds")
    
    def analyze_heart_rate(self, heart_rate: float) -> Dict:
        """Analyze heart rate for stress indicators
        
        Args:
            heart_rate: Heart rate in beats per minute (bpm)
            
        Returns:
            Dictionary with analysis results
        """
        result = {
            'value': heart_rate,
            'is_abnormal': False,
            'stress_level': 'normal',
            'score': 0.0
        }
        
        if heart_rate < self.thresholds.heart_rate_normal_min:
            result['is_abnormal'] = True
            result['stress_level'] = 'low_heart_rate'
            result['score'] = 0.3
        elif heart_rate >= self.thresholds.heart_rate_high_stress_threshold:
            result['is_abnormal'] = True
            result['stress_level'] = 'high_stress'
            result['score'] = 1.0
        elif heart_rate >= self.thresholds.heart_rate_stress_threshold:
            result['is_abnormal'] = True
            result['stress_level'] = 'moderate_stress'
            result['score'] = 0.7
        elif heart_rate > self.thresholds.heart_rate_normal_max:
            result['is_abnormal'] = True
            result['stress_level'] = 'mild_stress'
            result['score'] = 0.5
        
        logger.debug(f"Heart rate analysis: {result}")
        return result
    
    def analyze_temperature(self, temperature: float) -> Dict:
        """Analyze body temperature for stress indicators
        
        Args:
            temperature: Body temperature in Celsius
            
        Returns:
            Dictionary with analysis results
        """
        result = {
            'value': temperature,
            'is_abnormal': False,
            'stress_level': 'normal',
            'score': 0.0
        }
        
        if temperature < self.thresholds.temperature_low_threshold:
            result['is_abnormal'] = True
            result['stress_level'] = 'hypothermia_risk'
            result['score'] = 0.6
        elif temperature >= self.thresholds.temperature_stress_threshold:
            result['is_abnormal'] = True
            result['stress_level'] = 'elevated_temperature'
            result['score'] = 0.8
        elif temperature > self.thresholds.temperature_normal_max:
            result['is_abnormal'] = True
            result['stress_level'] = 'mild_elevation'
            result['score'] = 0.4
        elif temperature < self.thresholds.temperature_normal_min:
            result['is_abnormal'] = True
            result['stress_level'] = 'slightly_low'
            result['score'] = 0.3
        
        logger.debug(f"Temperature analysis: {result}")
        return result
    
    def analyze_combined(self, heart_rate: float, temperature: float) -> Dict:
        """Combined analysis of heart rate and temperature
        
        Args:
            heart_rate: Heart rate in bpm
            temperature: Body temperature in Celsius
            
        Returns:
            Combined analysis with overall stress detection
        """
        hr_analysis = self.analyze_heart_rate(heart_rate)
        temp_analysis = self.analyze_temperature(temperature)
        
        # Calculate combined stress score (weighted average)
        combined_score = (hr_analysis['score'] * 0.6) + (temp_analysis['score'] * 0.4)
        
        # Determine overall stress detection
        stress_detected = combined_score >= 0.5
        
        result = {
            'heart_rate': hr_analysis,
            'temperature': temp_analysis,
            'combined_score': combined_score,
            'stress_detected': stress_detected,
            'confidence': combined_score,
            'alert_recommended': combined_score >= 0.7
        }
        
        logger.info(f"Combined analysis: Score={combined_score:.2f}, Stress={stress_detected}")
        return result
    
    def analyze_time_series(self, heart_rates: list, temperatures: list) -> Dict:
        """Analyze time series data for stress patterns
        
        Args:
            heart_rates: List of heart rate measurements
            temperatures: List of temperature measurements
            
        Returns:
            Time series analysis results
        """
        hr_array = np.array(heart_rates)
        temp_array = np.array(temperatures)
        
        # Calculate trends
        hr_mean = np.mean(hr_array)
        hr_std = np.std(hr_array)
        hr_trend = np.polyfit(range(len(hr_array)), hr_array, 1)[0]
        
        temp_mean = np.mean(temp_array)
        temp_std = np.std(temp_array)
        temp_trend = np.polyfit(range(len(temp_array)), temp_array, 1)[0]
        
        # Detect abnormal variability
        hr_high_variability = hr_std > 15
        temp_high_variability = temp_std > 0.5
        
        # Detect concerning trends (rapid increase)
        hr_rapid_increase = hr_trend > 2  # More than 2 bpm increase per reading
        temp_rapid_increase = temp_trend > 0.1  # More than 0.1°C increase per reading
        
        stress_indicators = [
            hr_high_variability,
            temp_high_variability,
            hr_rapid_increase,
            temp_rapid_increase,
            hr_mean > self.thresholds.heart_rate_stress_threshold
        ]
        
        stress_score = sum(stress_indicators) / len(stress_indicators)
        
        result = {
            'heart_rate_stats': {
                'mean': float(hr_mean),
                'std': float(hr_std),
                'trend': float(hr_trend),
                'high_variability': hr_high_variability
            },
            'temperature_stats': {
                'mean': float(temp_mean),
                'std': float(temp_std),
                'trend': float(temp_trend),
                'high_variability': temp_high_variability
            },
            'stress_score': float(stress_score),
            'stress_detected': stress_score >= 0.4,
            'n_samples': len(heart_rates)
        }
        
        logger.info(f"Time series analysis: Score={stress_score:.2f} over {len(heart_rates)} samples")
        return result