"""Physiological Stress Analyzer

Analyzes heart rate and temperature sensor data to detect stress patterns.
"""

import numpy as np
from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class PhysiologicalThresholds:
    """Threshold values for stress detection"""
    heart_rate_normal_min: int = 60
    heart_rate_normal_max: int = 100
    heart_rate_stress_threshold: int = 110
    heart_rate_panic_threshold: int = 130
    
    temp_normal_min: float = 36.1
    temp_normal_max: float = 37.2
    temp_stress_threshold: float = 37.5
    temp_abnormal_threshold: float = 38.0


class PhysiologicalAnalyzer:
    """Analyze physiological sensor data for stress detection"""
    
    def __init__(self, thresholds: PhysiologicalThresholds = None):
        self.thresholds = thresholds or PhysiologicalThresholds()
        self.history = []
    
    def analyze_heart_rate(self, heart_rate: int) -> Dict:
        """Analyze heart rate for stress indicators
        
        Args:
            heart_rate: Heart rate in BPM
            
        Returns:
            Analysis result dictionary
        """
        if heart_rate < 0 or heart_rate > 220:
            return {
                'status': 'invalid',
                'stress_level': 0,
                'message': 'Invalid heart rate reading'
            }
        
        if heart_rate >= self.thresholds.heart_rate_panic_threshold:
            return {
                'status': 'panic',
                'stress_level': 3,
                'message': f'Panic level heart rate: {heart_rate} BPM',
                'stress_detected': True
            }
        elif heart_rate >= self.thresholds.heart_rate_stress_threshold:
            return {
                'status': 'stressed',
                'stress_level': 2,
                'message': f'Elevated heart rate: {heart_rate} BPM',
                'stress_detected': True
            }
        elif heart_rate > self.thresholds.heart_rate_normal_max:
            return {
                'status': 'elevated',
                'stress_level': 1,
                'message': f'Slightly elevated heart rate: {heart_rate} BPM',
                'stress_detected': False
            }
        else:
            return {
                'status': 'normal',
                'stress_level': 0,
                'message': f'Normal heart rate: {heart_rate} BPM',
                'stress_detected': False
            }
    
    def analyze_temperature(self, temperature: float) -> Dict:
        """Analyze body temperature
        
        Args:
            temperature: Body temperature in Celsius
            
        Returns:
            Analysis result dictionary
        """
        if temperature < 30 or temperature > 45:
            return {
                'status': 'invalid',
                'stress_level': 0,
                'message': 'Invalid temperature reading'
            }
        
        if temperature >= self.thresholds.temp_abnormal_threshold:
            return {
                'status': 'abnormal',
                'stress_level': 3,
                'message': f'Abnormally high temperature: {temperature}°C',
                'stress_detected': True
            }
        elif temperature >= self.thresholds.temp_stress_threshold:
            return {
                'status': 'elevated',
                'stress_level': 2,
                'message': f'Elevated temperature: {temperature}°C',
                'stress_detected': True
            }
        elif temperature > self.thresholds.temp_normal_max:
            return {
                'status': 'slightly_elevated',
                'stress_level': 1,
                'message': f'Slightly elevated temperature: {temperature}°C',
                'stress_detected': False
            }
        else:
            return {
                'status': 'normal',
                'stress_level': 0,
                'message': f'Normal temperature: {temperature}°C',
                'stress_detected': False
            }
    
    def analyze_combined(self, heart_rate: int, temperature: float) -> Dict:
        """Combined analysis of heart rate and temperature
        
        Args:
            heart_rate: Heart rate in BPM
            temperature: Temperature in Celsius
            
        Returns:
            Combined analysis result
        """
        hr_analysis = self.analyze_heart_rate(heart_rate)
        temp_analysis = self.analyze_temperature(temperature)
        
        # Combine stress levels
        total_stress_level = hr_analysis.get('stress_level', 0) + temp_analysis.get('stress_level', 0)
        
        # Determine overall stress status
        stress_detected = hr_analysis.get('stress_detected', False) or temp_analysis.get('stress_detected', False)
        
        # Calculate confidence based on both sensors
        if total_stress_level >= 4:
            confidence = 0.95
            severity = 'high'
        elif total_stress_level >= 3:
            confidence = 0.85
            severity = 'medium'
        elif total_stress_level >= 2:
            confidence = 0.70
            severity = 'low'
        else:
            confidence = 0.50
            severity = 'none'
        
        return {
            'stress_detected': stress_detected,
            'confidence': confidence,
            'severity': severity,
            'total_stress_level': total_stress_level,
            'heart_rate_analysis': hr_analysis,
            'temperature_analysis': temp_analysis,
            'sensor_data': {
                'heart_rate': heart_rate,
                'temperature': temperature
            }
        }
    
    def analyze_trend(self, history_window: int = 5) -> Dict:
        """Analyze stress trend over time
        
        Args:
            history_window: Number of recent readings to analyze
            
        Returns:
            Trend analysis result
        """
        if len(self.history) < 2:
            return {'trend': 'insufficient_data'}
        
        recent = self.history[-history_window:]
        stress_levels = [reading.get('total_stress_level', 0) for reading in recent]
        
        # Calculate trend
        if len(stress_levels) < 2:
            return {'trend': 'insufficient_data'}
        
        trend_direction = np.polyfit(range(len(stress_levels)), stress_levels, 1)[0]
        
        if trend_direction > 0.5:
            trend = 'increasing'
        elif trend_direction < -0.5:
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        return {
            'trend': trend,
            'average_stress_level': np.mean(stress_levels),
            'recent_readings': len(recent)
        }
    
    def update_history(self, analysis_result: Dict):
        """Add analysis result to history"""
        self.history.append(analysis_result)
        
        # Keep only last 50 readings
        if len(self.history) > 50:
            self.history = self.history[-50:]