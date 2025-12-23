"""Authentication routes for login, register, logout"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from backend import db
from backend.models.user import User
from backend.core.security import hash_password, verify_password
import logging

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user
    
    Body:
        email: User email
        password: User password
        name: User name
        role: User role (user, guardian, police)
        phone: Optional phone number
    """
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['email', 'password', 'name', 'role']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        name = data['name'].strip()
        role = data['role'].lower()
        phone = data.get('phone')
        
        # Validate role
        valid_roles = ['user', 'guardian', 'police']
        if role not in valid_roles:
            return jsonify({
                'success': False,
                'error': f'Invalid role. Must be one of: {", ".join(valid_roles)}'
            }), 400
        
        # Check if user exists
        if User.find_by_email(email):
            return jsonify({
                'success': False,
                'error': 'Email already registered'
            }), 409
        
        # Create user
        password_hash = hash_password(password)
        user = User(
            email=email,
            password_hash=password_hash,
            name=name,
            role=role,
            phone=phone
        )
        user.save()
        
        logger.info(f'New user registered: {email} ({role})')
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f'Registration error: {e}')
        return jsonify({
            'success': False,
            'error': 'Registration failed',
            'message': str(e)
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return JWT tokens
    
    Body:
        email: User email
        password: User password
    """
    try:
        data = request.get_json()
        
        email = data.get('email', '').lower().strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email and password required'
            }), 400
        
        # Find user
        user = User.find_by_email(email)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'Invalid email or password'
            }), 401
        
        # Check if active
        if not user.is_active:
            return jsonify({
                'success': False,
                'error': 'Account is deactivated'
            }), 403
        
        # Verify password
        if not verify_password(password, user.password_hash):
            return jsonify({
                'success': False,
                'error': 'Invalid email or password'
            }), 401
        
        # Update last login
        user.update_last_login()
        
        # Create tokens
        additional_claims = {
            'role': user.role,
            'email': user.email
        }
        
        access_token = create_access_token(
            identity=user.id,
            additional_claims=additional_claims
        )
        refresh_token = create_refresh_token(identity=user.id)
        
        logger.info(f'User logged in: {email}')
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f'Login error: {e}')
        return jsonify({
            'success': False,
            'error': 'Login failed',
            'message': str(e)
        }), 500


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token using refresh token"""
    try:
        user_id = get_jwt_identity()
        user = User.get_by_id(user_id)
        
        if not user or not user.is_active:
            return jsonify({
                'success': False,
                'error': 'Invalid or inactive user'
            }), 401
        
        additional_claims = {
            'role': user.role,
            'email': user.email
        }
        
        access_token = create_access_token(
            identity=user.id,
            additional_claims=additional_claims
        )
        
        return jsonify({
            'success': True,
            'access_token': access_token
        }), 200
        
    except Exception as e:
        logger.error(f'Token refresh error: {e}')
        return jsonify({
            'success': False,
            'error': 'Token refresh failed'
        }), 500


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current authenticated user info"""
    try:
        user_id = get_jwt_identity()
        user = User.get_by_id(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f'Get current user error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to get user info'
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (client should discard tokens)"""
    # In a production app, you might want to blacklist the token
    # For now, client-side token removal is sufficient
    
    user_id = get_jwt_identity()
    logger.info(f'User logged out: {user_id}')
    
    return jsonify({
        'success': True,
        'message': 'Logout successful'
    }), 200


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password
    
    Body:
        current_password: Current password
        new_password: New password
    """
    try:
        user_id = get_jwt_identity()
        user = User.get_by_id(user_id)
        
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({
                'success': False,
                'error': 'Current password and new password required'
            }), 400
        
        # Verify current password
        if not verify_password(current_password, user.password_hash):
            return jsonify({
                'success': False,
                'error': 'Current password is incorrect'
            }), 401
        
        # Update password
        user.password_hash = hash_password(new_password)
        db.session.commit()
        
        logger.info(f'Password changed for user: {user.email}')
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        }), 200
        
    except Exception as e:
        logger.error(f'Change password error: {e}')
        return jsonify({
            'success': False,
            'error': 'Password change failed'
        }), 500