"""User models for authentication and role management"""

from backend import db
from backend.core.database import BaseModel
from datetime import datetime


class User(BaseModel):
    """User model for device owners, guardians, and police"""
    
    __tablename__ = 'users'
    
    # Basic info
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    
    # Role: 'user', 'guardian', 'police'
    role = db.Column(db.String(20), nullable=False, default='user')
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    devices = db.relationship('Device', backref='owner', lazy=True, cascade='all, delete-orphan')
    emergency_contacts = db.relationship('EmergencyContact', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, email, password_hash, name, role='user', phone=None):
        self.email = email
        self.password_hash = password_hash
        self.name = name
        self.role = role
        self.phone = phone
    
    def to_dict(self, include_sensitive=False):
        """Convert to dictionary"""
        data = {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'phone': self.phone,
            'role': self.role,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_sensitive:
            data['password_hash'] = self.password_hash
        
        return data
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    @classmethod
    def find_by_email(cls, email):
        """Find user by email"""
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def find_by_role(cls, role):
        """Find all users with specific role"""
        return cls.query.filter_by(role=role, is_active=True).all()
    
    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class Guardian(BaseModel):
    """Guardian/Family member association with device owner"""
    
    __tablename__ = 'guardians'
    
    # User who owns the device
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Guardian user account (optional - can just be contact info)
    guardian_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Contact info (if no user account)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    relationship = db.Column(db.String(50), nullable=True)  # mother, father, friend, etc.
    
    # Alert preferences
    receive_sms = db.Column(db.Boolean, default=True)
    receive_email = db.Column(db.Boolean, default=True)
    receive_push = db.Column(db.Boolean, default=True)
    
    is_primary = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'guardian_user_id': self.guardian_user_id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'relationship': self.relationship,
            'receive_sms': self.receive_sms,
            'receive_email': self.receive_email,
            'receive_push': self.receive_push,
            'is_primary': self.is_primary,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f"<Guardian {self.name} for User {self.user_id}>"


class EmergencyContact(BaseModel):
    """Emergency contact for alerts (Police, NGO, etc.)"""
    
    __tablename__ = 'emergency_contacts'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    contact_type = db.Column(db.String(20), nullable=False)  # 'police', 'ngo', 'hospital', 'personal'
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    address = db.Column(db.Text, nullable=True)
    
    # Priority order (1 = highest)
    priority = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'contact_type': self.contact_type,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'priority': self.priority,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f"<EmergencyContact {self.name} ({self.contact_type})>"