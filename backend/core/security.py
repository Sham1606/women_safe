"""Security utilities for authentication and authorization"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt
from backend import bcrypt
import secrets
import string


def hash_password(password: str) -> str:
    """Hash a password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return bcrypt.generate_password_hash(password).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash
    
    Args:
        password: Plain text password
        password_hash: Hashed password
        
    Returns:
        True if password matches, False otherwise
    """
    return bcrypt.check_password_hash(password_hash, password)


def generate_device_token(length: int = 32) -> str:
    """Generate a secure random token for IoT devices
    
    Args:
        length: Token length
        
    Returns:
        Random token string
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def role_required(*allowed_roles):
    """Decorator to require specific user roles
    
    Args:
        *allowed_roles: Variable number of allowed roles
        
    Example:
        @role_required('admin', 'police')
        def admin_only_route():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get('role')
            
            if user_role not in allowed_roles:
                return jsonify({
                    'success': False,
                    'error': 'Forbidden',
                    'message': f'This endpoint requires one of these roles: {", ".join(allowed_roles)}'
                }), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def device_token_required(fn):
    """Decorator to require valid device token (for IoT endpoints)
    
    Checks for 'X-Device-Token' header
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        from flask import request
        from backend.models.device import Device
        
        device_token = request.headers.get('X-Device-Token')
        
        if not device_token:
            return jsonify({
                'success': False,
                'error': 'Unauthorized',
                'message': 'Device token required'
            }), 401
        
        # Verify device token
        device = Device.query.filter_by(device_token=device_token).first()
        
        if not device:
            return jsonify({
                'success': False,
                'error': 'Unauthorized',
                'message': 'Invalid device token'
            }), 401
        
        # Add device to request context
        request.device = device
        
        return fn(*args, **kwargs)
    return wrapper


def get_current_user():
    """Get current authenticated user from JWT
    
    Returns:
        User object or None
    """
    from backend.models.user import User
    
    user_id = get_jwt_identity()
    if user_id:
        return User.query.get(user_id)
    return None