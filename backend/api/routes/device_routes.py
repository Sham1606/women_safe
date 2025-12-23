"""Device management routes for ESP32 IoT devices"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend import db
from backend.models.device import Device
from backend.models.sensor_data import SensorData
from backend.core.security import generate_device_token, role_required, device_token_required
import logging

logger = logging.getLogger(__name__)

device_bp = Blueprint('devices', __name__)


@device_bp.route('/', methods=['GET'])
@jwt_required()
def get_devices():
    """Get all devices for current user"""
    try:
        user_id = get_jwt_identity()
        devices = Device.find_by_user(user_id)
        
        return jsonify({
            'success': True,
            'devices': [d.to_dict() for d in devices]
        }), 200
        
    except Exception as e:
        logger.error(f'Get devices error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to get devices'
        }), 500


@device_bp.route('/<int:device_id>', methods=['GET'])
@jwt_required()
def get_device(device_id):
    """Get device details"""
    try:
        user_id = get_jwt_identity()
        device = Device.query.filter_by(id=device_id, user_id=user_id).first()
        
        if not device:
            return jsonify({
                'success': False,
                'error': 'Device not found'
            }), 404
        
        return jsonify({
            'success': True,
            'device': device.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f'Get device error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to get device'
        }), 500


@device_bp.route('/register', methods=['POST'])
@jwt_required()
def register_device():
    """Register a new IoT device
    
    Body:
        device_name: Device name
        device_type: Optional device type (default: ESP32-CAM)
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if 'device_name' not in data:
            return jsonify({
                'success': False,
                'error': 'device_name is required'
            }), 400
        
        # Generate unique device token
        device_token = generate_device_token()
        
        device = Device(
            user_id=user_id,
            device_token=device_token,
            device_name=data['device_name'].strip(),
            device_type=data.get('device_type', 'ESP32-CAM')
        )
        device.save()
        
        logger.info(f'Device registered for user {user_id}: {device.device_name}')
        
        return jsonify({
            'success': True,
            'message': 'Device registered successfully',
            'device': device.to_dict(include_token=True)
        }), 201
        
    except Exception as e:
        logger.error(f'Register device error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to register device'
        }), 500


@device_bp.route('/<int:device_id>', methods=['PUT'])
@jwt_required()
def update_device(device_id):
    """Update device configuration
    
    Body:
        device_name: Optional new name
        alert_threshold: Optional alert threshold (0.0-1.0)
        auto_alert_enabled: Optional boolean
    """
    try:
        user_id = get_jwt_identity()
        device = Device.query.filter_by(id=device_id, user_id=user_id).first()
        
        if not device:
            return jsonify({
                'success': False,
                'error': 'Device not found'
            }), 404
        
        data = request.get_json()
        
        if 'device_name' in data:
            device.device_name = data['device_name'].strip()
        
        if 'alert_threshold' in data:
            threshold = float(data['alert_threshold'])
            if 0.0 <= threshold <= 1.0:
                device.alert_threshold = threshold
        
        if 'auto_alert_enabled' in data:
            device.auto_alert_enabled = bool(data['auto_alert_enabled'])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Device updated successfully',
            'device': device.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f'Update device error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to update device'
        }), 500


@device_bp.route('/<int:device_id>', methods=['DELETE'])
@jwt_required()
def delete_device(device_id):
    """Delete a device"""
    try:
        user_id = get_jwt_identity()
        device = Device.query.filter_by(id=device_id, user_id=user_id).first()
        
        if not device:
            return jsonify({
                'success': False,
                'error': 'Device not found'
            }), 404
        
        device.delete()
        
        logger.info(f'Device {device_id} deleted for user {user_id}')
        
        return jsonify({
            'success': True,
            'message': 'Device deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f'Delete device error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to delete device'
        }), 500


@device_bp.route('/<int:device_id>/status', methods=['GET'])
@jwt_required()
def get_device_status(device_id):
    """Get device status and recent sensor data"""
    try:
        user_id = get_jwt_identity()
        device = Device.query.filter_by(id=device_id, user_id=user_id).first()
        
        if not device:
            return jsonify({
                'success': False,
                'error': 'Device not found'
            }), 404
        
        # Get recent sensor data
        recent_data = SensorData.get_recent(device_id, minutes=60, limit=10)
        
        # Get statistics
        stats = SensorData.get_statistics(device_id, hours=24)
        
        return jsonify({
            'success': True,
            'device': device.to_dict(),
            'is_online': device.is_online(),
            'recent_sensor_data': [d.to_dict() for d in recent_data],
            'statistics_24h': stats
        }), 200
        
    except Exception as e:
        logger.error(f'Get device status error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to get device status'
        }), 500


# ===== IoT Device Endpoints (for ESP32) =====

@device_bp.route('/heartbeat', methods=['POST'])
@device_token_required
def device_heartbeat():
    """Device heartbeat endpoint
    
    Headers:
        X-Device-Token: Device authentication token
    
    Body:
        battery_level: Optional battery percentage
        latitude: Optional GPS latitude
        longitude: Optional GPS longitude
    """
    try:
        device = request.device
        data = request.get_json() or {}
        
        device.update_heartbeat(
            battery_level=data.get('battery_level'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude')
        )
        
        return jsonify({
            'success': True,
            'message': 'Heartbeat received',
            'device_status': device.status
        }), 200
        
    except Exception as e:
        logger.error(f'Device heartbeat error: {e}')
        return jsonify({
            'success': False,
            'error': 'Heartbeat failed'
        }), 500


@device_bp.route('/sensor-data', methods=['POST'])
@device_token_required
def receive_sensor_data():
    """Receive sensor data from IoT device
    
    Headers:
        X-Device-Token: Device authentication token
    
    Body:
        heart_rate: Heart rate in bpm
        temperature: Temperature in Celsius
        latitude: Optional GPS latitude
        longitude: Optional GPS longitude
        battery_level: Optional battery percentage
    """
    try:
        device = request.device
        data = request.get_json()
        
        # Create sensor data record
        sensor_data = SensorData(
            device_id=device.id,
            heart_rate=data.get('heart_rate'),
            temperature=data.get('temperature')
        )
        
        if 'latitude' in data and 'longitude' in data:
            sensor_data.latitude = data['latitude']
            sensor_data.longitude = data['longitude']
        
        if 'battery_level' in data:
            sensor_data.battery_level = data['battery_level']
        
        sensor_data.save()
        
        # Update device heartbeat
        device.update_heartbeat(
            battery_level=data.get('battery_level'),
            latitude=data.get('latitude'),
            longitude=data.get('longitude')
        )
        
        return jsonify({
            'success': True,
            'message': 'Sensor data received',
            'sensor_data_id': sensor_data.id
        }), 201
        
    except Exception as e:
        logger.error(f'Receive sensor data error: {e}')
        return jsonify({
            'success': False,
            'error': 'Failed to receive sensor data'
        }), 500