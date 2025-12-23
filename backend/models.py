from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='GUARDIAN') # GUARDIAN, POLICE, ADMIN
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    devices = db.relationship('Device', backref='owner', lazy=True)

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_uid = db.Column(db.String(50), unique=True, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    last_seen = db.Column(db.DateTime)
    battery_level = db.Column(db.Integer)
    last_lat = db.Column(db.Float)
    last_lng = db.Column(db.Float)
    
    events = db.relationship('SensorEvent', backref='device', lazy=True)
    alerts = db.relationship('Alert', backref='device', lazy=True)

class SensorEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    heart_rate = db.Column(db.Float)
    spo2 = db.Column(db.Float)
    temperature = db.Column(db.Float)
    raw_stress_score = db.Column(db.Float)
    
    # AI Results
    ai_label = db.Column(db.String(20)) # normal / stressed
    ai_confidence = db.Column(db.Float)
    has_audio = db.Column(db.Boolean, default=False)
    audio_path = db.Column(db.String(200))

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    reason = db.Column(db.String(50)) # AUTO_STRESS, SOS_BUTTON
    status = db.Column(db.String(20), default='NEW', index=True) # NEW, IN_PROGRESS, RESOLVED
    severity = db.Column(db.String(20), default='HIGH')
    
    gps_lat = db.Column(db.Float)
    gps_lng = db.Column(db.Float)
    
    evidence = db.relationship('Evidence', backref='alert', lazy=True)

class Evidence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alert_id = db.Column(db.Integer, db.ForeignKey('alert.id'), nullable=False)
    file_type = db.Column(db.String(10)) # AUDIO, VIDEO
    file_path = db.Column(db.String(200))
    captured_at = db.Column(db.DateTime, default=datetime.utcnow)
