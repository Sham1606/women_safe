"""Evidence model for photos, videos, and audio recordings"""

from backend import db
from backend.core.database import BaseModel
from datetime import datetime
import os


class Evidence(BaseModel):
    """Evidence (photos, videos, audio) model"""
    
    __tablename__ = 'evidence'
    
    # Associated alert
    alert_id = db.Column(db.Integer, db.ForeignKey('alerts.id'), nullable=False)
    
    # Evidence type
    evidence_type = db.Column(db.String(20), nullable=False)  # 'photo', 'video', 'audio'
    
    # File information
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=True)  # Local path
    file_url = db.Column(db.String(500), nullable=True)  # Cloud storage URL
    file_size = db.Column(db.Integer, nullable=True)  # Size in bytes
    mime_type = db.Column(db.String(50), nullable=True)
    
    # Metadata
    duration = db.Column(db.Float, nullable=True)  # Duration for video/audio in seconds
    width = db.Column(db.Integer, nullable=True)  # For images/videos
    height = db.Column(db.Integer, nullable=True)  # For images/videos
    
    # Location and timestamp
    captured_at = db.Column(db.DateTime, nullable=True)
    gps_latitude = db.Column(db.Float, nullable=True)
    gps_longitude = db.Column(db.Float, nullable=True)
    
    # Status
    upload_status = db.Column(db.String(20), default='pending')  # 'pending', 'uploaded', 'failed'
    is_encrypted = db.Column(db.Boolean, default=False)
    
    # Access control
    is_public = db.Column(db.Boolean, default=False)
    access_count = db.Column(db.Integer, default=0)
    last_accessed = db.Column(db.DateTime, nullable=True)
    
    def __init__(self, alert_id, evidence_type, file_name):
        self.alert_id = alert_id
        self.evidence_type = evidence_type
        self.file_name = file_name
    
    def to_dict(self, include_urls=True):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'alert_id': self.alert_id,
            'evidence_type': self.evidence_type,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'metadata': {
                'duration': self.duration,
                'dimensions': {
                    'width': self.width,
                    'height': self.height
                } if self.width and self.height else None
            },
            'captured_at': self.captured_at.isoformat() if self.captured_at else None,
            'location': {
                'latitude': self.gps_latitude,
                'longitude': self.gps_longitude
            } if self.gps_latitude and self.gps_longitude else None,
            'upload_status': self.upload_status,
            'is_encrypted': self.is_encrypted,
            'access_count': self.access_count,
            'created_at': self.created_at.isoformat()
        }
        
        if include_urls:
            data['file_url'] = self.file_url
            data['file_path'] = self.file_path
        
        return data
    
    def mark_uploaded(self, file_url):
        """Mark evidence as successfully uploaded"""
        self.upload_status = 'uploaded'
        self.file_url = file_url
        db.session.commit()
    
    def mark_failed(self):
        """Mark evidence upload as failed"""
        self.upload_status = 'failed'
        db.session.commit()
    
    def track_access(self):
        """Track evidence access"""
        self.access_count += 1
        self.last_accessed = datetime.utcnow()
        db.session.commit()
    
    def get_file_extension(self):
        """Get file extension"""
        return os.path.splitext(self.file_name)[1].lower()
    
    @classmethod
    def get_by_alert(cls, alert_id):
        """Get all evidence for an alert"""
        return cls.query.filter_by(alert_id=alert_id).order_by(cls.captured_at.desc()).all()
    
    @classmethod
    def get_by_type(cls, alert_id, evidence_type):
        """Get evidence by type for an alert"""
        return cls.query.filter_by(alert_id=alert_id, evidence_type=evidence_type).all()
    
    def __repr__(self):
        return f"<Evidence {self.evidence_type} - Alert {self.alert_id}>"