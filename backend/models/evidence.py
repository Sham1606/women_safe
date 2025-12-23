"""Evidence Model - Photos, Videos, Audio"""

from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from backend.core.database import Base


class EvidenceType(str, enum.Enum):
    PHOTO = "photo"
    VIDEO = "video"
    AUDIO = "audio"


class Evidence(Base):
    __tablename__ = "evidence"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=False)
    evidence_type = Column(SQLEnum(EvidenceType), nullable=False)
    
    # File information
    file_url = Column(String, nullable=False)  # S3/Firebase URL or local path
    file_name = Column(String)
    file_size = Column(Integer)  # bytes
    mime_type = Column(String)
    
    # Metadata
    duration = Column(Float)  # For video/audio in seconds
    resolution = Column(String)  # For photo/video
    
    # GPS at capture time
    gps_latitude = Column(Float)
    gps_longitude = Column(Float)
    
    # Timestamps
    captured_at = Column(DateTime(timezone=True), server_default=func.now())
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    alert = relationship("Alert", back_populates="evidence")