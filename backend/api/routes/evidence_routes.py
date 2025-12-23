"""Evidence management routes for photos, videos, audio"""

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from werkzeug.utils import secure_filename
from backend import db
from backend.models.evidence import Evidence
from backend.models.alert import Alert
from backend.core.security import device_token_required, role_required
import os
import logging
import base64
from datetime import datetime

logger = logging.getLogger(__name__)

evidence_bp = Blueprint('evidence', __name__)


def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


@evidence_bp.route('/alert/<int:alert_id>', methods=['GET'])
@jwt_required()
def get_evidence_by_alert(alert_id):
    """Get all evidence for an alert"""
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get('role')
        
        # Get alert
        alert = Alert.query.get(alert_id)
        if not alert:
            return jsonify({
                'success': False,
                'error': 'Alert not found'
            }), 404
        
        # Check permission
        if user_role not in ['police'] and alert.user_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403
        
        # Get evidence
        evidence_list = Evidence.get_by_alert(alert_id)
        
        return jsonify({
            'success': True,
            'evidence': [e.to_dict() for e in evidence_list],
            'count': len(evidence_list)
        }), 200
        
    except Exception as e:
        logger.error(f'Get evidence error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to get evidence'
        }), 500


@evidence_bp.route('/<int:evidence_id>', methods=['GET'])
@jwt_required()
def get_evidence(evidence_id):
    """Get specific evidence details"""
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get('role')
        
        evidence = Evidence.query.get(evidence_id)
        if not evidence:
            return jsonify({
                'success': False,
                'error': 'Evidence not found'
            }), 404
        
        # Check permission through alert
        alert = Alert.query.get(evidence.alert_id)
        if user_role not in ['police'] and alert.user_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403
        
        # Track access
        evidence.track_access()
        
        return jsonify({
            'success': True,
            'evidence': evidence.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f'Get evidence error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to get evidence'
        }), 500


@evidence_bp.route('/<int:evidence_id>/download', methods=['GET'])
@jwt_required()
def download_evidence(evidence_id):
    """Download evidence file"""
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get('role')
        
        evidence = Evidence.query.get(evidence_id)
        if not evidence:
            return jsonify({
                'success': False,
                'error': 'Evidence not found'
            }), 404
        
        # Check permission
        alert = Alert.query.get(evidence.alert_id)
        if user_role not in ['police'] and alert.user_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403
        
        # Track access
        evidence.track_access()
        
        # If cloud storage URL, redirect
        if evidence.file_url:
            return jsonify({
                'success': True,
                'download_url': evidence.file_url
            }), 200
        
        # If local file, send file
        if evidence.file_path and os.path.exists(evidence.file_path):
            return send_file(
                evidence.file_path,
                as_attachment=True,
                download_name=evidence.file_name
            )
        
        return jsonify({
            'success': False,
            'error': 'Evidence file not found'
        }), 404
        
    except Exception as e:
        logger.error(f'Download evidence error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to download evidence'
        }), 500


# ===== IoT Device Endpoints =====

@evidence_bp.route('/upload', methods=['POST'])
@device_token_required
def upload_evidence():
    """Upload evidence from IoT device
    
    Headers:
        X-Device-Token: Device authentication token
    
    Body (JSON):
        alert_id: Alert ID
        evidence_type: 'photo', 'video', or 'audio'
        file_name: Original filename
        file_base64: Base64 encoded file data
        latitude: Optional GPS latitude
        longitude: Optional GPS longitude
        captured_at: Optional capture timestamp (ISO format)
    """
    try:
        device = request.device
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['alert_id', 'evidence_type', 'file_name', 'file_base64']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        alert_id = data['alert_id']
        evidence_type = data['evidence_type']
        file_name = secure_filename(data['file_name'])
        file_base64 = data['file_base64']
        
        # Validate evidence type
        if evidence_type not in ['photo', 'video', 'audio']:
            return jsonify({
                'success': False,
                'error': 'Invalid evidence_type'
            }), 400
        
        # Verify alert belongs to this device
        alert = Alert.query.filter_by(id=alert_id, device_id=device.id).first()
        if not alert:
            return jsonify({
                'success': False,
                'error': 'Alert not found or does not belong to this device'
            }), 404
        
        # Decode base64 file
        try:
            file_data = base64.b64decode(file_base64)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Invalid base64 encoding'
            }), 400
        
        # Create evidence record
        evidence = Evidence(
            alert_id=alert_id,
            evidence_type=evidence_type,
            file_name=file_name
        )
        
        evidence.file_size = len(file_data)
        
        # Location
        if 'latitude' in data and 'longitude' in data:
            evidence.gps_latitude = float(data['latitude'])
            evidence.gps_longitude = float(data['longitude'])
        
        # Capture timestamp
        if 'captured_at' in data:
            try:
                evidence.captured_at = datetime.fromisoformat(data['captured_at'].replace('Z', '+00:00'))
            except:
                evidence.captured_at = datetime.utcnow()
        else:
            evidence.captured_at = datetime.utcnow()
        
        # Save file locally
        upload_folder = os.path.join('backend', 'uploads', 'evidence')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"alert_{alert_id}_{evidence_type}_{timestamp}_{file_name}"
        file_path = os.path.join(upload_folder, unique_filename)
        
        # Write file
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        evidence.file_path = file_path
        evidence.upload_status = 'uploaded'
        evidence.save()
        
        logger.info(f'Evidence uploaded: Alert {alert_id}, Type {evidence_type}, Size {len(file_data)} bytes')
        
        return jsonify({
            'success': True,
            'message': 'Evidence uploaded successfully',
            'evidence_id': evidence.id,
            'file_size': evidence.file_size
        }), 201
        
    except Exception as e:
        logger.error(f'Upload evidence error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to upload evidence',
            'message': str(e)
        }), 500


@evidence_bp.route('/<int:evidence_id>', methods=['DELETE'])
@jwt_required()
@role_required('user', 'police')
def delete_evidence(evidence_id):
    """Delete evidence (restricted to owner and police)"""
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get('role')
        
        evidence = Evidence.query.get(evidence_id)
        if not evidence:
            return jsonify({
                'success': False,
                'error': 'Evidence not found'
            }), 404
        
        # Check permission
        alert = Alert.query.get(evidence.alert_id)
        if user_role != 'police' and alert.user_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403
        
        # Delete physical file if exists
        if evidence.file_path and os.path.exists(evidence.file_path):
            os.remove(evidence.file_path)
        
        evidence.delete()
        
        logger.info(f'Evidence {evidence_id} deleted by user {user_id}')
        
        return jsonify({
            'success': True,
            'message': 'Evidence deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f'Delete evidence error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to delete evidence'
        }), 500