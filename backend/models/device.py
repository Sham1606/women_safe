"""Device model for ESP32 IoT devices"""

from backend import db
from backend.core.database import BaseModel
from datetime import datetime


class Device(BaseModel):
    """IoT Device (ESP32) model"""
    
    __tablename__ = 'devices'
    
    # Owner
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Device identification
    device_token = db.Column(db.String(64), unique=True, nullable=False, index=True)
    device_name = db.Column(db.String(100), nullable=False)
    device_type = db.Column(db.String(50), default='ESP32-CAM')  # ESP32-CAM, ESP32, etc.
    firmware_version = db.Column(db.String(20), nullable=True)
    
    # Status
    status = db.Column(db.String(20), default='offline')  # 'online', 'offline', 'alert', 'maintenance'
    battery_level = db.Column(db.Integer, nullable=True)  # 0-100%
    last_heartbeat = db.Column(db.DateTime, nullable=True)
    last_location_lat = db.Column(db.Float, nullable=True)
    last_location_lng = db.Column(db.Float, nullable=True)
    
    # Configuration
    alert_threshold = db.Column(db.Float, default=0.7)  # AI confidence threshold for alert
    auto_alert_enabled = db.Column(db.Boolean, default=True)
    
    # Sensors
    has_heart_rate_sensor = db.Column(db.Boolean, default=True)
    has_temperature_sensor = db.Column(db.Boolean, default=True)
    has_microphone = db.Column(db.Boolean, default=True)
    has_camera = db.Column(db.Boolean, default=True)
    has_gps = db.Column(db.Boolean, default=True)
    has_buzzer = db.Column(db.Boolean, default=True)
    
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    alerts = db.relationship('Alert', backref='device', lazy=True)
    sensor_data = db.relationship('SensorData', backref='device', lazy=True)
    
    def __init__(self, user_id, device_token, device_name, device_type='ESP32-CAM'):
        self.user_id = user_id
        self.device_token = device_token
        self.device_name = device_name
        self.device_type = device_type
    
    def to_dict(self, include_token=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'device_name': self.device_name,
            'device_type': self.device_type,
            'firmware_version': self.firmware_version,
            'status': self.status,
            'battery_level': self.battery_level,
            'last_heartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            'last_location': {
                'latitude': self.last_location_lat,
                'longitude': self.last_location_lng
            } if self.last_location_lat and self.last_location_lng else None,
            'alert_threshold': self.alert_threshold,
            'auto_alert_enabled': self.auto_alert_enabled,
            'sensors': {
                'heart_rate': self.has_heart_rate_sensor,
                'temperature': self.has_temperature_sensor,
                'microphone': self.has_microphone,
                'camera': self.has_camera,
                'gps': self.has_gps,
                'buzzer': self.has_buzzer
            },
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_token:
            data['device_token'] = self.device_token
        
        return data
    
    def update_heartbeat(self, battery_level=None, latitude=None, longitude=None):
        """Update device heartbeat"""
        self.last_heartbeat = datetime.utcnow()
        self.status = 'online'
        
        if battery_level is not None:
            self.battery_level = battery_level
        
        if latitude is not None and longitude is not None:
            self.last_location_lat = latitude
            self.last_location_lng = longitude
        
        db.session.commit()
    
    def is_online(self, timeout_minutes=5):
        """Check if device is online based on last heartbeat"""
        if not self.last_heartbeat:
            return False
        
        time_diff = datetime.utcnow() - self.last_heartbeat
        return time_diff.total_seconds() < (timeout_minutes * 60)
    
    @classmethod
    def find_by_token(cls, token):
        """Find device by token"""
        return cls.query.filter_by(device_token=token).first()
    
    @classmethod
    def find_by_user(cls, user_id):
        """Find all devices for a user"""
        return cls.query.filter_by(user_id=user_id, is_active=True).all()
    
    def __repr__(self):
        return f"<Device {self.device_name} ({self.status})>"