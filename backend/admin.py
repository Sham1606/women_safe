from flask import Blueprint, jsonify
from backend.models import db, User, Device, Alert, SensorEvent
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    current_user = get_jwt_identity()
    if current_user['role'] not in ['POLICE', 'ADMIN']:
        return jsonify({'message': 'Unauthorized'}), 403
        
    stats = {
        'total_users': User.query.count(),
        'active_devices': Device.query.filter_by(is_active=True).count(),
        'alerts_by_status': dict(db.session.query(Alert.status, func.count(Alert.id)).group_by(Alert.status).all()),
        'latest_alerts': [{
            'id': a.id,
            'device': a.device.device_uid,
            'reason': a.reason,
            'time': a.timestamp.isoformat()
        } for a in Alert.query.order_by(Alert.timestamp.desc()).limit(5).all()]
    }
    return jsonify(stats), 200

@admin_bp.route('/heatmap', methods=['GET'])
@jwt_required()
def get_heatmap():
    current_user = get_jwt_identity()
    if current_user['role'] not in ['POLICE', 'ADMIN']:
        return jsonify({'message': 'Unauthorized'}), 403
        
    # Get coordinates of all alerts
    alerts = Alert.query.with_entities(Alert.gps_lat, Alert.gps_lng).filter(Alert.gps_lat != None).all()
    coords = [{'lat': a[0], 'lng': a[1]} for a in alerts]
    
    return jsonify(coords), 200
