"""Alert Model - Distress Alerts"""

from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, Float, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from backend.core.database import Base


class AlertType(str, enum.Enum):
    AI_DETECTED = "ai_detected"  # AI stress detection
    MANUAL_TRIGGER = "manual_trigger"  # User pressed button
    SENSOR_ABNORMAL = "sensor_abnormal"  # Abnormal sensor readings


class AlertStatus(str, enum.Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    FALSE_ALARM = "false_alarm"


class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    alert_type = Column(SQLEnum(AlertType), nullable=False)
    status = Column(SQLEnum(AlertStatus), default=AlertStatus.ACTIVE)
    
    # Location
    latitude = Column(Float)
    longitude = Column(Float)
    location_address = Column(String)
    
    # AI Analysis
    audio_stress_score = Column(Float)  # 0.0-1.0
    physio_stress_score = Column(Float)  # 0.0-1.0
    combined_confidence = Column(Float)  # 0.0-1.0
    ai_decision_reason = Column(Text)
    
    # Sensor readings at time of alert
    heart_rate = Column(Integer)
    temperature = Column(Float)
    
    # Alert details
    description = Column(Text)
    notes = Column(Text)
    
    # Timestamps
    triggered_at = Column(DateTime(timezone=True), server_default=func.now())
    acknowledged_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True))
    
    # Relationships
    device = relationship("Device", back_populates="alerts")
    evidence = relationship("Evidence", back_populates="alert")