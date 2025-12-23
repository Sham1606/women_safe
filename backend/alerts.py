from flask import Blueprint, jsonify, request
from backend.models import db, Alert, Device, Evidence
from backend.auth import jwt_required  # Assumed helper or import directly
from flask_jwt_extended import jwt_required, get_jwt_identity

alert_bp = Blueprint('alert', __name__)

@alert_bp.route('/', methods=['GET'])
@jwt_required()
def list_alerts():
    current_user = get_jwt_identity()
    user_role = current_user.get('role', 'GUARDIAN')
    user_id = current_user.get('id')
    
    query = Alert.query
    
    # Guardian only sees own devices
    if user_role == 'GUARDIAN':
        query = query.join(Device).filter(Device.owner_id == user_id)
        
    alerts = query.order_by(Alert.timestamp.desc()).all()
    
    return jsonify([{
        'id': a.id,
        'device_uid': a.device.device_uid,
        'reason': a.reason,
        'status': a.status,
        'severity': a.severity,
        'timestamp': a.timestamp.isoformat(),
        'lat': a.gps_lat,
        'lng': a.gps_lng
    } for a in alerts]), 200

@alert_bp.route('/<int:alert_id>', methods=['GET'])
@jwt_required()
def get_alert(alert_id):
    alert = Alert.query.get_or_404(alert_id)
    # TODO: Add ownership check here for Guardians
    
    evidence_list = [{
        'type': e.file_type,
        'path': e.file_path,
        'captured_at': e.captured_at.isoformat()
    } for e in alert.evidence]
    
    return jsonify({
        'id': alert.id,
        'device_uid': alert.device.device_uid,
        'reason': alert.reason,
        'status': alert.status,
        'timestamp': alert.timestamp.isoformat(),
        'evidence': evidence_list
    }), 200

@alert_bp.route('/<int:alert_id>/status', methods=['PATCH'])
@jwt_required()
def update_status(alert_id):
    current_user = get_jwt_identity()
    if current_user['role'] not in ['POLICE', 'ADMIN']:
        return jsonify({'message': 'Unauthorized'}), 403
        
    data = request.get_json()
    alert = Alert.query.get_or_404(alert_id)
    
    if 'status' in data:
        alert.status = data['status']
        
    db.session.commit()
    return jsonify({'message': 'Status updated'}), 200
