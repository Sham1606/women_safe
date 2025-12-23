"""Security Utilities

JWT token handling and password hashing.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token
    
    Args:
        data: Data to encode in token
        expires_delta: Token expiration time
        
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token data or None
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning(f"Token verification failed: {e}")
        return None


def create_device_token(device_id: str) -> str:
    """Create device authentication token for IoT devices
    
    Args:
        device_id: Unique device identifier
        
    Returns:
        Device token
    """
    data = {
        "device_id": device_id,
        "type": "device"
    }
    # Device tokens don't expire
    token = jwt.encode(data, settings.IOT_AUTH_SECRET, algorithm=settings.ALGORITHM)
    return token


def verify_device_token(token: str) -> Optional[str]:
    """Verify device token and extract device_id
    
    Args:
        token: Device token
        
    Returns:
        Device ID or None
    """
    try:
        payload = jwt.decode(token, settings.IOT_AUTH_SECRET, algorithms=[settings.ALGORITHM])
        if payload.get("type") == "device":
            return payload.get("device_id")
        return None
    except JWTError as e:
        logger.warning(f"Device token verification failed: {e}")
        return None
