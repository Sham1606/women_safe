"""User Model - User, Guardian, Police"""

from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from backend.core.database import Base


class UserRole(str, enum.Enum):
    USER = "user"  # Device owner
    GUARDIAN = "guardian"  # Family/Emergency contact
    POLICE = "police"  # Admin/Law enforcement


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String)
    role = Column(SQLEnum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    devices = relationship("Device", back_populates="owner")
    guardian_links = relationship("GuardianLink", foreign_keys="GuardianLink.user_id", back_populates="user")


class GuardianLink(Base):
    """Links users with their guardians/emergency contacts"""
    __tablename__ = "guardian_links"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    guardian_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    relationship_type = Column(String)  # "family", "friend", "police"
    priority = Column(Integer, default=1)  # 1 = highest priority
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    guardian = relationship("User", foreign_keys=[guardian_id])