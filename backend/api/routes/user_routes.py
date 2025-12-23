"""User management routes"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from backend import db
from backend.models.user import User, Guardian, EmergencyContact
from backend.core.security import role_required
import logging

logger = logging.getLogger(__name__)

user_bp = Blueprint('users', __name__)


@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile"""
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
        logger.error(f'Get profile error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to get profile'
        }), 500


@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile
    
    Body:
        name: Optional new name
        phone: Optional new phone
    """
    try:
        user_id = get_jwt_identity()
        user = User.get_by_id(user_id)
        
        data = request.get_json()
        
        if 'name' in data:
            user.name = data['name'].strip()
        
        if 'phone' in data:
            user.phone = data['phone']
        
        db.session.commit()
        
        logger.info(f'Profile updated for user: {user.email}')
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f'Update profile error: {e}')
        return jsonify({
            'success': False,
            'error': 'Profile update failed'
        }), 500


@user_bp.route('/guardians', methods=['GET'])
@jwt_required()
def get_guardians():
    """Get all guardians for current user"""
    try:
        user_id = get_jwt_identity()
        
        guardians = Guardian.query.filter_by(
            user_id=user_id,
            is_active=True
        ).all()
        
        return jsonify({
            'success': True,
            'guardians': [g.to_dict() for g in guardians]
        }), 200
        
    except Exception as e:
        logger.error(f'Get guardians error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to get guardians'
        }), 500


@user_bp.route('/guardians', methods=['POST'])
@jwt_required()
def add_guardian():
    """Add a new guardian
    
    Body:
        name: Guardian name
        phone: Guardian phone
        email: Optional guardian email
        relationship: Optional relationship
        receive_sms: Optional (default: true)
        receive_email: Optional (default: true)
        receive_push: Optional (default: true)
        is_primary: Optional (default: false)
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validation
        if 'name' not in data or 'phone' not in data:
            return jsonify({
                'success': False,
                'error': 'Name and phone are required'
            }), 400
        
        guardian = Guardian(
            user_id=user_id,
            name=data['name'].strip(),
            phone=data['phone'].strip(),
            email=data.get('email'),
            relationship=data.get('relationship'),
            receive_sms=data.get('receive_sms', True),
            receive_email=data.get('receive_email', True),
            receive_push=data.get('receive_push', True),
            is_primary=data.get('is_primary', False)
        )
        guardian.save()
        
        logger.info(f'Guardian added for user {user_id}: {guardian.name}')
        
        return jsonify({
            'success': True,
            'message': 'Guardian added successfully',
            'guardian': guardian.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f'Add guardian error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to add guardian'
        }), 500


@user_bp.route('/guardians/<int:guardian_id>', methods=['PUT'])
@jwt_required()
def update_guardian(guardian_id):
    """Update guardian information"""
    try:
        user_id = get_jwt_identity()
        guardian = Guardian.query.filter_by(
            id=guardian_id,
            user_id=user_id
        ).first()
        
        if not guardian:
            return jsonify({
                'success': False,
                'error': 'Guardian not found'
            }), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'name' in data:
            guardian.name = data['name'].strip()
        if 'phone' in data:
            guardian.phone = data['phone'].strip()
        if 'email' in data:
            guardian.email = data['email']
        if 'relationship' in data:
            guardian.relationship = data['relationship']
        if 'receive_sms' in data:
            guardian.receive_sms = data['receive_sms']
        if 'receive_email' in data:
            guardian.receive_email = data['receive_email']
        if 'receive_push' in data:
            guardian.receive_push = data['receive_push']
        if 'is_primary' in data:
            guardian.is_primary = data['is_primary']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Guardian updated successfully',
            'guardian': guardian.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f'Update guardian error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to update guardian'
        }), 500


@user_bp.route('/guardians/<int:guardian_id>', methods=['DELETE'])
@jwt_required()
def delete_guardian(guardian_id):
    """Delete a guardian"""
    try:
        user_id = get_jwt_identity()
        guardian = Guardian.query.filter_by(
            id=guardian_id,
            user_id=user_id
        ).first()
        
        if not guardian:
            return jsonify({
                'success': False,
                'error': 'Guardian not found'
            }), 404
        
        guardian.delete()
        
        logger.info(f'Guardian {guardian_id} deleted for user {user_id}')
        
        return jsonify({
            'success': True,
            'message': 'Guardian deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f'Delete guardian error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to delete guardian'
        }), 500


@user_bp.route('/emergency-contacts', methods=['GET'])
@jwt_required()
def get_emergency_contacts():
    """Get all emergency contacts"""
    try:
        user_id = get_jwt_identity()
        
        contacts = EmergencyContact.query.filter_by(
            user_id=user_id,
            is_active=True
        ).order_by(EmergencyContact.priority).all()
        
        return jsonify({
            'success': True,
            'contacts': [c.to_dict() for c in contacts]
        }), 200
        
    except Exception as e:
        logger.error(f'Get emergency contacts error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to get emergency contacts'
        }), 500


@user_bp.route('/emergency-contacts', methods=['POST'])
@jwt_required()
def add_emergency_contact():
    """Add emergency contact
    
    Body:
        contact_type: 'police', 'ngo', 'hospital', 'personal'
        name: Contact name
        phone: Contact phone
        email: Optional email
        address: Optional address
        priority: Optional priority (default: 1)
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if 'contact_type' not in data or 'name' not in data or 'phone' not in data:
            return jsonify({
                'success': False,
                'error': 'contact_type, name, and phone are required'
            }), 400
        
        contact = EmergencyContact(
            user_id=user_id,
            contact_type=data['contact_type'],
            name=data['name'].strip(),
            phone=data['phone'].strip(),
            email=data.get('email'),
            address=data.get('address'),
            priority=data.get('priority', 1)
        )
        contact.save()
        
        logger.info(f'Emergency contact added for user {user_id}: {contact.name}')
        
        return jsonify({
            'success': True,
            'message': 'Emergency contact added successfully',
            'contact': contact.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f'Add emergency contact error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to add emergency contact'
        }), 500