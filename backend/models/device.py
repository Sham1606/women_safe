"""Device Model - ESP32 Device Registration"""

from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from backend.core.database import Base


class DeviceStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    ALERT = "alert"
    MAINTENANCE = "maintenance"


class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_token = Column(String, unique=True, nullable=False, index=True)
    device_name = Column(String)
    device_model = Column(String, default="ESP32-CAM")
    status = Column(SQLEnum(DeviceStatus), default=DeviceStatus.OFFLINE)
    battery_level = Column(Integer)  # 0-100
    last_heartbeat = Column(DateTime(timezone=True))
    last_gps_lat = Column(Float)
    last_gps_lng = Column(Float)
    firmware_version = Column(String)
    is_active = Column(Boolean, default=True)
    registered_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="devices")
    alerts = relationship("Alert", back_populates="device")
    sensor_data = relationship("SensorData", back_populates="device")