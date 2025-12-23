"""Alert management routes"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from backend import db
from backend.models.alert import Alert
from backend.models.device import Device
from backend.core.security import role_required, device_token_required
import logging

logger = logging.getLogger(__name__)

alert_bp = Blueprint('alerts', __name__)


@alert_bp.route('/', methods=['GET'])
@jwt_required()
def get_alerts():
    """Get alerts for current user
    
    Query params:
        status: Optional filter by status (active, acknowledged, resolved, false_alarm)
        limit: Optional limit (default: 50)
    """
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get('role')
        
        # Build query
        if user_role == 'police':
            # Police can see all alerts
            query = Alert.query
        else:
            # Users and guardians see only their own
            query = Alert.query.filter_by(user_id=user_id)
        
        # Filter by status
        status = request.args.get('status')
        if status:
            query = query.filter_by(status=status)
        
        # Limit
        limit = int(request.args.get('limit', 50))
        
        alerts = query.order_by(Alert.created_at.desc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'alerts': [a.to_dict(include_evidence=False) for a in alerts],
            'count': len(alerts)
        }), 200
        
    except Exception as e:
        logger.error(f'Get alerts error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to get alerts'
        }), 500


@alert_bp.route('/<int:alert_id>', methods=['GET'])
@jwt_required()
def get_alert(alert_id):
    """Get alert details with evidence"""
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get('role')
        
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
        
        return jsonify({
            'success': True,
            'alert': alert.to_dict(include_evidence=True)
        }), 200
        
    except Exception as e:
        logger.error(f'Get alert error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to get alert'
        }), 500


@alert_bp.route('/active', methods=['GET'])
@jwt_required()
def get_active_alerts():
    """Get all active alerts"""
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get('role')
        
        if user_role == 'police':
            alerts = Alert.get_active_alerts()
        else:
            alerts = Alert.get_active_alerts(user_id=user_id)
        
        return jsonify({
            'success': True,
            'alerts': [a.to_dict() for a in alerts],
            'count': len(alerts)
        }), 200
        
    except Exception as e:
        logger.error(f'Get active alerts error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to get active alerts'
        }), 500


@alert_bp.route('/<int:alert_id>/acknowledge', methods=['POST'])
@jwt_required()
@role_required('police', 'guardian')
def acknowledge_alert(alert_id):
    """Acknowledge an alert
    
    Body:
        notes: Optional acknowledgment notes
    """
    try:
        user_id = get_jwt_identity()
        alert = Alert.query.get(alert_id)
        
        if not alert:
            return jsonify({
                'success': False,
                'error': 'Alert not found'
            }), 404
        
        data = request.get_json() or {}
        notes = data.get('notes')
        
        alert.acknowledge(user_id, notes)
        
        logger.info(f'Alert {alert_id} acknowledged by user {user_id}')
        
        return jsonify({
            'success': True,
            'message': 'Alert acknowledged successfully',
            'alert': alert.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f'Acknowledge alert error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to acknowledge alert'
        }), 500


@alert_bp.route('/<int:alert_id>/resolve', methods=['POST'])
@jwt_required()
@role_required('police', 'user')
def resolve_alert(alert_id):
    """Resolve an alert
    
    Body:
        notes: Optional resolution notes
    """
    try:
        user_id = get_jwt_identity()
        alert = Alert.query.get(alert_id)
        
        if not alert:
            return jsonify({
                'success': False,
                'error': 'Alert not found'
            }), 404
        
        data = request.get_json() or {}
        notes = data.get('notes')
        
        alert.resolve(user_id, notes)
        
        logger.info(f'Alert {alert_id} resolved by user {user_id}')
        
        return jsonify({
            'success': True,
            'message': 'Alert resolved successfully',
            'alert': alert.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f'Resolve alert error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to resolve alert'
        }), 500


@alert_bp.route('/<int:alert_id>/false-alarm', methods=['POST'])
@jwt_required()
def mark_false_alarm(alert_id):
    """Mark alert as false alarm
    
    Body:
        notes: Optional notes
    """
    try:
        user_id = get_jwt_identity()
        alert = Alert.query.get(alert_id)
        
        if not alert:
            return jsonify({
                'success': False,
                'error': 'Alert not found'
            }), 404
        
        # Only alert owner can mark as false alarm
        if alert.user_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Only alert owner can mark as false alarm'
            }), 403
        
        data = request.get_json() or {}
        notes = data.get('notes')
        
        alert.mark_false_alarm(user_id, notes)
        
        logger.info(f'Alert {alert_id} marked as false alarm by user {user_id}')
        
        return jsonify({
            'success': True,
            'message': 'Alert marked as false alarm',
            'alert': alert.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f'Mark false alarm error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to mark as false alarm'
        }), 500


# ===== IoT Device Endpoints =====

@alert_bp.route('/trigger', methods=['POST'])
@device_token_required
def trigger_alert():
    """Trigger alert from IoT device (manual or AI-detected)
    
    Headers:
        X-Device-Token: Device authentication token
    
    Body:
        alert_type: 'ai_detected' or 'manual_trigger'
        trigger_source: Optional ('audio', 'physiological', 'hybrid', 'button')
        stress_score: Optional AI stress score
        confidence: Optional AI confidence
        ai_analysis: Optional full AI analysis JSON
        latitude: Optional GPS latitude
        longitude: Optional GPS longitude
        heart_rate: Optional heart rate
        temperature: Optional temperature
        priority: Optional priority level
    """
    try:
        device = request.device
        data = request.get_json()
        
        # Validate alert type
        alert_type = data.get('alert_type')
        if alert_type not in ['ai_detected', 'manual_trigger']:
            return jsonify({
                'success': False,
                'error': 'Invalid alert_type. Must be ai_detected or manual_trigger'
            }), 400
        
        # Create alert
        alert = Alert(
            device_id=device.id,
            user_id=device.user_id,
            alert_type=alert_type,
            trigger_source=data.get('trigger_source')
        )
        
        # AI analysis data
        if 'stress_score' in data:
            alert.stress_score = float(data['stress_score'])
        if 'confidence' in data:
            alert.confidence = float(data['confidence'])
        if 'ai_analysis' in data:
            alert.ai_analysis = data['ai_analysis']
        
        # Location
        if 'latitude' in data and 'longitude' in data:
            alert.latitude = float(data['latitude'])
            alert.longitude = float(data['longitude'])
        
        # Physiological data
        if 'heart_rate' in data:
            alert.heart_rate = int(data['heart_rate'])
        if 'temperature' in data:
            alert.temperature = float(data['temperature'])
        
        # Priority
        if 'priority' in data:
            alert.priority = data['priority']
        
        alert.save()
        
        # Update device status
        device.status = 'alert'
        db.session.commit()
        
        logger.warning(f'ALERT TRIGGERED: Device {device.id}, Alert {alert.id}, Type: {alert_type}')
        
        # Return commands for device
        commands = {
            'activate_camera': True,
            'activate_buzzer': True if alert.priority in ['high', 'critical'] else False,
            'gps_required': True,
            'alert_id': alert.id
        }
        
        return jsonify({
            'success': True,
            'message': 'Alert triggered successfully',
            'alert_id': alert.id,
            'commands': commands
        }), 201
        
    except Exception as e:
        logger.error(f'Trigger alert error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to trigger alert',
            'message': str(e)
        }), 500