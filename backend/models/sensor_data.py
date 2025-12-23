"""Sensor Data Model - Continuous sensor logging"""

from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.core.database import Base


class SensorData(Base):
    __tablename__ = "sensor_data"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    
    # Sensor readings
    heart_rate = Column(Integer)  # BPM
    temperature = Column(Float)  # Celsius
    audio_stress_score = Column(Float)  # 0.0-1.0 from AI
    
    # Additional metrics
    battery_level = Column(Integer)  # 0-100
    
    # GPS
    gps_latitude = Column(Float)
    gps_longitude = Column(Float)
    
    # Analysis result
    stress_detected = Column(Integer)  # 0 or 1
    analysis_confidence = Column(Float)
    analysis_notes = Column(Text)
    
    # Timestamp
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    device = relationship("Device", back_populates="sensor_data")