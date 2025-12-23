"""Sensor data model for physiological readings"""

from backend import db
from backend.core.database import BaseModel
from datetime import datetime, timedelta


class SensorData(BaseModel):
    """Physiological sensor data logs"""
    
    __tablename__ = 'sensor_data'
    
    # Device
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
    
    # Sensor readings
    heart_rate = db.Column(db.Integer, nullable=True)  # bpm
    temperature = db.Column(db.Float, nullable=True)  # Celsius
    
    # Audio analysis (if available)
    audio_stress_score = db.Column(db.Float, nullable=True)  # 0.0 to 1.0
    audio_confidence = db.Column(db.Float, nullable=True)  # 0.0 to 1.0
    
    # Combined analysis
    stress_detected = db.Column(db.Boolean, default=False)
    combined_score = db.Column(db.Float, nullable=True)  # 0.0 to 1.0
    
    # Location
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    
    # Battery and device status
    battery_level = db.Column(db.Integer, nullable=True)  # 0-100%
    
    # Timestamp
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __init__(self, device_id, heart_rate=None, temperature=None):
        self.device_id = device_id
        self.heart_rate = heart_rate
        self.temperature = temperature
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'device_id': self.device_id,
            'heart_rate': self.heart_rate,
            'temperature': self.temperature,
            'audio_stress_score': self.audio_stress_score,
            'audio_confidence': self.audio_confidence,
            'stress_detected': self.stress_detected,
            'combined_score': self.combined_score,
            'location': {
                'latitude': self.latitude,
                'longitude': self.longitude
            } if self.latitude and self.longitude else None,
            'battery_level': self.battery_level,
            'recorded_at': self.recorded_at.isoformat(),
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def get_recent(cls, device_id, minutes=60, limit=100):
        """Get recent sensor data for a device
        
        Args:
            device_id: Device ID
            minutes: Time window in minutes
            limit: Maximum number of records
            
        Returns:
            List of SensorData records
        """
        time_threshold = datetime.utcnow() - timedelta(minutes=minutes)
        return cls.query.filter(
            cls.device_id == device_id,
            cls.recorded_at >= time_threshold
        ).order_by(cls.recorded_at.desc()).limit(limit).all()
    
    @classmethod
    def get_time_series(cls, device_id, start_time, end_time):
        """Get sensor data for time range
        
        Args:
            device_id: Device ID
            start_time: Start datetime
            end_time: End datetime
            
        Returns:
            List of SensorData records
        """
        return cls.query.filter(
            cls.device_id == device_id,
            cls.recorded_at >= start_time,
            cls.recorded_at <= end_time
        ).order_by(cls.recorded_at.asc()).all()
    
    @classmethod
    def get_stress_events(cls, device_id, hours=24):
        """Get all stress detection events
        
        Args:
            device_id: Device ID
            hours: Time window in hours
            
        Returns:
            List of SensorData records where stress was detected
        """
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        return cls.query.filter(
            cls.device_id == device_id,
            cls.stress_detected == True,
            cls.recorded_at >= time_threshold
        ).order_by(cls.recorded_at.desc()).all()
    
    @classmethod
    def get_statistics(cls, device_id, hours=24):
        """Get statistical summary of sensor data
        
        Args:
            device_id: Device ID
            hours: Time window in hours
            
        Returns:
            Dictionary with statistics
        """
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        
        data = cls.query.filter(
            cls.device_id == device_id,
            cls.recorded_at >= time_threshold
        ).all()
        
        if not data:
            return None
        
        # Extract values
        heart_rates = [d.heart_rate for d in data if d.heart_rate is not None]
        temperatures = [d.temperature for d in data if d.temperature is not None]
        stress_scores = [d.combined_score for d in data if d.combined_score is not None]
        
        stats = {
            'time_window_hours': hours,
            'total_readings': len(data),
            'stress_events': sum(1 for d in data if d.stress_detected),
            'heart_rate': {
                'mean': sum(heart_rates) / len(heart_rates) if heart_rates else None,
                'min': min(heart_rates) if heart_rates else None,
                'max': max(heart_rates) if heart_rates else None,
                'readings_count': len(heart_rates)
            } if heart_rates else None,
            'temperature': {
                'mean': sum(temperatures) / len(temperatures) if temperatures else None,
                'min': min(temperatures) if temperatures else None,
                'max': max(temperatures) if temperatures else None,
                'readings_count': len(temperatures)
            } if temperatures else None,
            'stress_score': {
                'mean': sum(stress_scores) / len(stress_scores) if stress_scores else None,
                'max': max(stress_scores) if stress_scores else None,
                'readings_count': len(stress_scores)
            } if stress_scores else None
        }
        
        return stats
    
    @classmethod
    def cleanup_old_data(cls, days=30):
        """Delete sensor data older than specified days
        
        Args:
            days: Number of days to retain
            
        Returns:
            Number of records deleted
        """
        time_threshold = datetime.utcnow() - timedelta(days=days)
        old_data = cls.query.filter(cls.recorded_at < time_threshold).all()
        count = len(old_data)
        
        for data in old_data:
            db.session.delete(data)
        
        db.session.commit()
        return count
    
    def __repr__(self):
        return f"<SensorData Device {self.device_id} - HR:{self.heart_rate} T:{self.temperature}>"