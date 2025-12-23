"""Alert model for distress incidents"""

from backend import db
from backend.core.database import BaseModel
from datetime import datetime


class Alert(BaseModel):
    """Alert/Incident model"""
    
    __tablename__ = 'alerts'
    
    # Device and user
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Alert type
    alert_type = db.Column(db.String(20), nullable=False)  # 'ai_detected', 'manual_trigger'
    trigger_source = db.Column(db.String(50), nullable=True)  # 'audio', 'physiological', 'hybrid', 'button'
    
    # AI Analysis
    stress_score = db.Column(db.Float, nullable=True)  # 0.0 to 1.0
    confidence = db.Column(db.Float, nullable=True)  # 0.0 to 1.0
    ai_analysis = db.Column(db.JSON, nullable=True)  # Full AI analysis results
    
    # Location
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    location_address = db.Column(db.Text, nullable=True)  # Reverse geocoded address
    
    # Physiological data at time of alert
    heart_rate = db.Column(db.Integer, nullable=True)
    temperature = db.Column(db.Float, nullable=True)
    
    # Status
    status = db.Column(db.String(20), default='active')  # 'active', 'acknowledged', 'resolved', 'false_alarm'
    priority = db.Column(db.String(20), default='high')  # 'low', 'medium', 'high', 'critical'
    
    # Response tracking
    acknowledged_at = db.Column(db.DateTime, nullable=True)
    acknowledged_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    resolution_notes = db.Column(db.Text, nullable=True)
    
    # Notifications sent
    notifications_sent = db.Column(db.JSON, nullable=True)  # Track who was notified
    
    # Relationships
    evidence = db.relationship('Evidence', backref='alert', lazy=True, cascade='all, delete-orphan')
    user = db.relationship('User', foreign_keys=[user_id], backref='alerts')
    
    def __init__(self, device_id, user_id, alert_type, trigger_source=None):
        self.device_id = device_id
        self.user_id = user_id
        self.alert_type = alert_type
        self.trigger_source = trigger_source
    
    def to_dict(self, include_evidence=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'device_id': self.device_id,
            'user_id': self.user_id,
            'alert_type': self.alert_type,
            'trigger_source': self.trigger_source,
            'stress_score': self.stress_score,
            'confidence': self.confidence,
            'ai_analysis': self.ai_analysis,
            'location': {
                'latitude': self.latitude,
                'longitude': self.longitude,
                'address': self.location_address
            } if self.latitude and self.longitude else None,
            'physiological': {
                'heart_rate': self.heart_rate,
                'temperature': self.temperature
            } if self.heart_rate or self.temperature else None,
            'status': self.status,
            'priority': self.priority,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'acknowledged_by': self.acknowledged_by,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolved_by': self.resolved_by,
            'resolution_notes': self.resolution_notes,
            'notifications_sent': self.notifications_sent,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_evidence:
            data['evidence'] = [e.to_dict() for e in self.evidence]
        
        return data
    
    def acknowledge(self, user_id, notes=None):
        """Acknowledge alert"""
        self.status = 'acknowledged'
        self.acknowledged_at = datetime.utcnow()
        self.acknowledged_by = user_id
        if notes:
            self.resolution_notes = notes
        db.session.commit()
    
    def resolve(self, user_id, notes=None):
        """Resolve alert"""
        self.status = 'resolved'
        self.resolved_at = datetime.utcnow()
        self.resolved_by = user_id
        if notes:
            self.resolution_notes = notes
        db.session.commit()
    
    def mark_false_alarm(self, user_id, notes=None):
        """Mark as false alarm"""
        self.status = 'false_alarm'
        self.resolved_at = datetime.utcnow()
        self.resolved_by = user_id
        if notes:
            self.resolution_notes = notes
        db.session.commit()
    
    @classmethod
    def get_active_alerts(cls, user_id=None):
        """Get all active alerts"""
        query = cls.query.filter_by(status='active')
        if user_id:
            query = query.filter_by(user_id=user_id)
        return query.order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_recent_alerts(cls, user_id=None, limit=10):
        """Get recent alerts"""
        query = cls.query
        if user_id:
            query = query.filter_by(user_id=user_id)
        return query.order_by(cls.created_at.desc()).limit(limit).all()
    
    def __repr__(self):
        return f"<Alert {self.id} ({self.alert_type}) - {self.status}>"