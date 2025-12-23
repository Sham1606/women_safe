from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import os
import uuid
import sys

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from backend.models import db, User, Device, SensorEvent, Alert, Evidence
from ai_engine.inference import predict_stress

device_bp = Blueprint('device', __name__)

@device_bp.route('/my-devices', methods=['GET'])
@jwt_required()
def get_my_devices():
    current_user = get_jwt_identity()
    devices = Device.query.filter_by(owner_id=current_user['id']).all()
    
    result = []
    for d in devices:
        # Get latest event
        latest_event = SensorEvent.query.filter_by(device_id=d.id).order_by(SensorEvent.timestamp.desc()).first()
        # Get latest alert
        latest_alert = Alert.query.filter_by(device_id=d.id).order_by(Alert.timestamp.desc()).first()
        
        result.append({
            'id': d.id,
            'uid': d.device_uid,
            'is_active': d.is_active,
            'last_seen': d.last_seen.isoformat() if d.last_seen else None,
            'battery': d.battery_level,
            'location': {'lat': d.last_lat, 'lng': d.last_lng},
            'latest_vitals': {
                'hr': latest_event.heart_rate if latest_event else None,
                'spo2': latest_event.spo2 if latest_event else None,
                'temp': latest_event.temperature if latest_event else None,
                'ai_label': latest_event.ai_label if latest_event else 'NORMAL',
                'ai_conf': latest_event.ai_confidence if latest_event else 0
            },
            'active_alert': {
                'id': latest_alert.id if latest_alert and latest_alert.status != 'RESOLVED' else None,
                'status': latest_alert.status if latest_alert and latest_alert.status != 'RESOLVED' else None,
                'reason': latest_alert.reason if latest_alert and latest_alert.status != 'RESOLVED' else None
            }
        })
    return jsonify(result), 200

@device_bp.route('/register', methods=['POST'])
def register_device():
    # Helper for frontend to link device
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
        
    device_uid = data.get('device_uid')
    device = Device.query.filter_by(device_uid=device_uid).first()
    
    if device:
        # Re-link or update
        device.owner_id = user.id
    else:
        device = Device(device_uid=device_uid, owner_id=user.id, is_active=True)
        db.session.add(device)
        
    db.session.commit()
    return jsonify({'message': 'Device registered', 'id': device.id}), 201

@device_bp.route('/event', methods=['POST'])
def receive_event():
    device_uid = request.form.get('device_uid')
    if not device_uid:
        return jsonify({'message': 'Missing device_uid'}), 400
        
    device = Device.query.filter_by(device_uid=device_uid).first()
    if not device:
        return jsonify({'message': 'Device not registered'}), 404

    # Extract Sensor Data
    heart_rate = request.form.get('heart_rate', type=float) or 0
    spo2 = request.form.get('spo2', type=float) or 0
    temp = request.form.get('temperature', type=float) or 0
    lat = request.form.get('lat', type=float)
    lng = request.form.get('lng', type=float)
    battery = request.form.get('battery', type=int)
    
    # Update Device Status
    device.last_seen = datetime.utcnow()
    if lat and lng:
        device.last_lat = lat
        device.last_lng = lng
    if battery is not None:
        device.battery_level = battery
    db.session.commit()

    # Process Audio with AI
    ai_result = {'label': 'normal', 'confidence': 0.0}
    has_audio = False
    audio_filename = None
    ai_error = None
    
    if 'audio' in request.files:
        audio_file = request.files['audio']
        if audio_file.filename != '':
            has_audio = True
            try:
                audio_bytes = audio_file.read()
                audio_file.seek(0)
                ai_result = predict_stress(audio_bytes=audio_bytes)
                if 'error' in ai_result: raise Exception(ai_result['error'])
            except Exception as e:
                print(f"AI Error: {e}")
                ai_error = str(e)
                ai_result = {'label': 'unknown', 'confidence': 0.0}
            
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                audio_filename = f"{device_uid}_{timestamp}.wav"
                save_path = os.path.join(config.EVIDENCE_DIR, audio_filename)
                audio_file.save(save_path)
            except Exception as e: print(f"File Save Error: {e}")

    # === DISTRESS SCORE CALCULATION ===
    ai_score = ai_result.get('confidence', 0) if ai_result.get('label') == 'stressed' else 0
    hr_score = 1.0 if heart_rate > 100 else (0.5 if heart_rate > 90 else 0)
    temp_score = 1.0 if temp > 38.5 else 0
    
    distress_score = (ai_score * 0.6) + (hr_score * 0.3) + (temp_score * 0.1)
    manual_sos = request.form.get('manual_sos', type=int) == 1
    is_stressed = (distress_score > 0.5) or manual_sos
    
    # Create Event Record
    event = SensorEvent(
        device_id=device.id,
        heart_rate=heart_rate,
        spo2=spo2,
        temperature=temp,
        raw_stress_score=distress_score,
        ai_label=ai_result.get('label'),
        ai_confidence=ai_result.get('confidence'),
        has_audio=has_audio,
        audio_path=audio_filename
    )
    db.session.add(event)
    
    # Trigger Alert
    if is_stressed:
        reason = 'AUTO_STRESS' if not manual_sos else 'MANUAL_SOS'
        if ai_error and not manual_sos: reason = 'VITALS_ANOMALY'
            
        existing_alert = Alert.query.filter_by(device_id=device.id, status='NEW').first()
        if not existing_alert:
            alert = Alert(
                device_id=device.id,
                reason=reason,
                status='NEW',
                severity='HIGH' if distress_score > 0.8 else 'MEDIUM',
                gps_lat=lat,
                gps_lng=lng
            )
            db.session.add(alert)
            db.session.flush()
            
            if has_audio and audio_filename:
                evidence = Evidence(alert_id=alert.id, file_type='AUDIO', file_path=audio_filename)
                db.session.add(evidence)
            
    db.session.commit()
    return jsonify({'status': 'success', 'distress_score': round(distress_score, 2), 'alert_triggered': is_stressed}), 200
