import os
import sys
import uuid
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func

def get_current_user_data():
    """Helper to safely get user_id and role from JWT, handling both string and dict identities."""
    identity = get_jwt_identity()
    claims = get_jwt()
    
    # If identity is a dictionary (from old tokens), extract ID
    if isinstance(identity, dict):
        user_id = identity.get('id')
        role = identity.get('role', 'GUARDIAN')
    else:
        user_id = int(identity) if identity else None
        role = claims.get('role', 'GUARDIAN')
        
    return user_id, role

# Add parent directory to path for config/ai_engine
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

import config
from ai_engine.inference import predict_stress

# Initialize Flask App
app = Flask(__name__, 
            template_folder=os.path.join('backend', 'templates'),
            static_folder=os.path.join('backend', 'static'))
app.config.from_object(config)

# Initialize Extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
CORS(app)

# ==========================================
# MODELS
# ==========================================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='GUARDIAN') # GUARDIAN, POLICE, ADMIN
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    devices = db.relationship('Device', backref='owner', lazy=True)

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_uid = db.Column(db.String(50), unique=True, nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    last_seen = db.Column(db.DateTime)
    battery_level = db.Column(db.Integer)
    last_lat = db.Column(db.Float)
    last_lng = db.Column(db.Float)
    events = db.relationship('SensorEvent', backref='device', lazy=True)
    alerts = db.relationship('Alert', backref='device', lazy=True)

class SensorEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    heart_rate = db.Column(db.Float)
    spo2 = db.Column(db.Float)
    temperature = db.Column(db.Float)
    raw_stress_score = db.Column(db.Float)
    ai_label = db.Column(db.String(20)) 
    ai_confidence = db.Column(db.Float)
    has_audio = db.Column(db.Boolean, default=False)
    audio_path = db.Column(db.String(200))

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False, index=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    reason = db.Column(db.String(50)) 
    status = db.Column(db.String(20), default='NEW', index=True) 
    severity = db.Column(db.String(20), default='HIGH')
    gps_lat = db.Column(db.Float)
    gps_lng = db.Column(db.Float)
    evidence = db.relationship('Evidence', backref='alert', lazy=True)

class Evidence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alert_id = db.Column(db.Integer, db.ForeignKey('alert.id'), nullable=False)
    file_type = db.Column(db.String(10)) 
    file_path = db.Column(db.String(200))
    captured_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==========================================
# REGISTER BLUEPRINTS
# ==========================================

# Import and register the views blueprint
from backend.views import views_bp
app.register_blueprint(views_bp)

print("✅ Registered views blueprint with routes:")
for rule in app.url_map.iter_rules():
    if rule.endpoint.startswith('views.'):
        print(f"   {rule.rule} -> {rule.endpoint}")

# ==========================================
# AUTH ROUTES
# ==========================================

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    device_uid = data.get('device_uid') # Optional unified registration
    
    if not email or not password or not name:
        return jsonify({'message': 'Missing required fields'}), 400
        
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already exists'}), 400
        
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(
        name=name, email=email,
        password_hash=hashed_password, role=data.get('role', 'GUARDIAN')
    )
    db.session.add(new_user)
    db.session.flush() # Get user ID
    
    # Optional: Automatically register device if UID provided
    if device_uid:
        existing_device = Device.query.filter_by(device_uid=device_uid).first()
        if existing_device:
            existing_device.owner_id = new_user.id
        else:
            db.session.add(Device(device_uid=device_uid, owner_id=new_user.id))
            
    db.session.commit()
    return jsonify({'message': 'User and device registered successfully' if device_uid else 'User registered successfully'}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'message': 'Email and password required'}), 400
        
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'message': 'Invalid credentials'}), 401
        
    # Create access token with user ID as identity and role as additional claim
    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={'role': user.role}
    )
    return jsonify({
        'access_token': access_token,
        'user': {'id': user.id, 'name': user.name, 'email': user.email, 'role': user.role}
    }), 200

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_me():
    user_id, _ = get_current_user_data()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'role': user.role,
        'phone': user.phone
    }), 200

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# ==========================================
# DEVICE ROUTES
# ==========================================

@app.route('/api/device/register', methods=['POST'])
@jwt_required(optional=True)
def register_device():
    data = request.get_json() or {}
    device_uid = data.get('device_uid')
    email = data.get('email')
    
    # 1. Try to get owner from JWT (Logged in user)
    user_id = None
    identity = get_jwt_identity()
    if identity:
        user_id = int(identity) if not isinstance(identity, dict) else identity.get('id')
    
    # 2. If not logged in, use provided email
    if not user_id:
        if not email:
            return jsonify({'message': 'Authentication required or provide an email'}), 401
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'message': 'User not found'}), 404
        user_id = user.id
        
    if not device_uid:
        return jsonify({'message': 'device_uid is required'}), 400
        
    device = Device.query.filter_by(device_uid=device_uid).first()
    if device: 
        device.owner_id = user_id
    else:
        device = Device(device_uid=device_uid, owner_id=user_id)
        db.session.add(device)
        
    db.session.commit()
    return jsonify({'message': 'Device successfully linked to account', 'id': device.id}), 201

@app.route('/api/device/my-devices', methods=['GET'])
@jwt_required()
def get_my_devices():
    user_id, _ = get_current_user_data()
    devices = Device.query.filter_by(owner_id=user_id).all()
    res = []
    for d in devices:
        latest_ev = SensorEvent.query.filter_by(device_id=d.id).order_by(SensorEvent.timestamp.desc()).first()
        latest_al = Alert.query.filter_by(device_id=d.id).order_by(Alert.timestamp.desc()).first()
        res.append({
            'uid': d.device_uid, 'is_active': d.is_active, 'battery': d.battery_level,
            'location': {'lat': d.last_lat, 'lng': d.last_lng},
            'latest_vitals': {
                'hr': latest_ev.heart_rate if latest_ev else None,
                'temp': latest_ev.temperature if latest_ev else None,
                'spo2': latest_ev.spo2 if latest_ev else None,
                'ai_label': latest_ev.ai_label if latest_ev else 'normal',
                'ai_conf': latest_ev.ai_confidence if latest_ev else 0
            },
            'active_alert': {
                'id': latest_al.id if latest_al and latest_al.status != 'RESOLVED' else None,
                'status': latest_al.status if latest_al and latest_al.status != 'RESOLVED' else None,
                'reason': latest_al.reason if latest_al and latest_al.status != 'RESOLVED' else None
            },
            'last_update': d.last_seen.isoformat() if d.last_seen else None
        })
    return jsonify(res), 200

@app.route('/api/device/event', methods=['POST'])
def receive_event():
    uid = request.form.get('device_uid')
    device = Device.query.filter_by(device_uid=uid).first()
    if not device: return jsonify({'message': 'Device not found'}), 404
    
    hr = request.form.get('heart_rate', type=float) or 0
    temp = request.form.get('temperature', type=float) or 0
    spo2 = request.form.get('spo2', type=float) or 0
    lat = request.form.get('lat', type=float)
    lng = request.form.get('lng', type=float)
    
    device.last_seen = datetime.utcnow()
    if lat and lng: device.last_lat, device.last_lng = lat, lng
    
    ai_res = {'label': 'normal', 'confidence': 0.0}
    audio_filename = None
    if 'audio' in request.files:
        audio_file = request.files['audio']
        if audio_file.filename != '':
            audio_bytes = audio_file.read()
            audio_file.seek(0)
            ai_res = predict_stress(audio_bytes=audio_bytes)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_filename = f"{uid}_{timestamp}.wav"
            audio_file.save(os.path.join(config.EVIDENCE_DIR, audio_filename))

    distress_score = (ai_res.get('confidence', 0) if ai_res.get('label') == 'stressed' else 0) * 0.6 \
                     + (1.0 if hr > 100 else 0) * 0.3 + (1.0 if temp > 38.5 else 0) * 0.1
    
    manual_sos = request.form.get('manual_sos', type=int) == 1
    is_stressed = (distress_score > 0.5) or manual_sos
    
    event = SensorEvent(
        device_id=device.id, heart_rate=hr, temperature=temp, spo2=spo2,
        raw_stress_score=distress_score, ai_label=ai_res.get('label'),
        ai_confidence=ai_res.get('confidence'), has_audio=(audio_filename is not None),
        audio_path=audio_filename
    )
    db.session.add(event)

    if is_stressed:
        existing = Alert.query.filter_by(device_id=device.id, status='NEW').first()
        if not existing:
            alert = Alert(device_id=device.id, reason='AUTO_STRESS' if not manual_sos else 'MANUAL_SOS',
                          status='NEW', severity='HIGH' if distress_score > 0.8 else 'MEDIUM',
                          gps_lat=lat, gps_lng=lng)
            db.session.add(alert)
            db.session.flush()
            if audio_filename:
                db.session.add(Evidence(alert_id=alert.id, file_type='AUDIO', file_path=audio_filename))
    
    db.session.commit()
    return jsonify({'status': 'success', 'distress_score': round(distress_score, 2), 'alert_triggered': is_stressed}), 200

# ==========================================
# ALERT & ADMIN ROUTES
# ==========================================

@app.route('/api/alerts', methods=['GET'])
@jwt_required()
def list_alerts():
    user_id, role = get_current_user_data()
    
    query = Alert.query
    if role == 'GUARDIAN': 
        query = query.join(Device).filter(Device.owner_id == user_id)
    alerts = query.order_by(Alert.timestamp.desc()).all()
    return jsonify([{'id': a.id, 'device_uid': a.device.device_uid, 'reason': a.reason, 'status': a.status,
                     'severity': a.severity, 'timestamp': a.timestamp.isoformat(), 'lat': a.gps_lat, 'lng': a.gps_lng}
                    for a in alerts]), 200

@app.route('/api/alerts/<int:alert_id>', methods=['GET'])
@jwt_required()
def get_alert(alert_id):
    a = Alert.query.get_or_404(alert_id)
    ev = [{'type': e.file_type, 'path': e.file_path, 'captured_at': e.captured_at.isoformat()} for e in a.evidence]
    return jsonify({'id': a.id, 'device_uid': a.device.device_uid, 'reason': a.reason, 'status': a.status,
                    'timestamp': a.timestamp.isoformat(), 'evidence': ev}), 200

@app.route('/api/alerts/<int:alert_id>/status', methods=['PATCH'])
@jwt_required()
def update_status(alert_id):
    _, role = get_current_user_data()
    if role not in ['POLICE', 'ADMIN']: 
        return jsonify({'message': 'Unauthorized'}), 403
    a = Alert.query.get_or_404(alert_id)
    a.status = request.get_json().get('status', a.status)
    db.session.commit()
    return jsonify({'message': 'Updated'}), 200

@app.route('/api/admin/stats', methods=['GET'])
@jwt_required()
def get_stats():
    _, role = get_current_user_data()
    if role not in ['POLICE', 'ADMIN']: 
        return jsonify({'message': 'Unauthorized'}), 403
    return jsonify({
        'total_users': User.query.count(),
        'active_devices': Device.query.filter_by(is_active=True).count(),
        'alerts_by_status': dict(db.session.query(Alert.status, func.count(Alert.id)).group_by(Alert.status).all()),
        'latest_alerts': [{'id': a.id, 'device': a.device.device_uid, 'reason': a.reason, 'time': a.timestamp.isoformat()}
                          for a in Alert.query.order_by(Alert.timestamp.desc()).limit(5).all()]
    }), 200

@app.route('/static/evidence/<path:filename>')
def serve_evidence(filename):
    return send_from_directory(config.EVIDENCE_DIR, filename)

# ==========================================
# SEED & RUN
# ==========================================

def seed_data():
    with app.app_context():
        db.create_all()
        # Admin User
        if not User.query.filter_by(email='admin@safety.com').first():
            admin = User(name="System Admin", email="admin@safety.com",
                         password_hash=generate_password_hash("admin123", method='pbkdf2:sha256'), role="ADMIN")
            db.session.add(admin)
        
        # Guardian User for Testing
        if not User.query.filter_by(email='guardian@safe.com').first():
            guardian = User(name="Test Guardian", email="guardian@safe.com",
                           password_hash=generate_password_hash("guardian123", method='pbkdf2:sha256'), role="GUARDIAN")
            db.session.add(guardian)
            
        db.session.commit()
        print("✅ Database seeded with test users")

if __name__ == "__main__":
    seed_data()
    print("\n🛡️  Shield System starting...")
    print("📍 Server: http://localhost:5000")
    print("\n📄 Available pages:")
    print("   / (Landing Page)")
    print("   /dashboard")
    print("   /alerts")
    print("   /profile")
    print("   /notifications")
    print("   /monitor")
    print("   /devices")
    print("   /settings")
    print("   /admin")
    print("   /analytics")
    print("   /evidence")
    print("   /simulator")
    print("   /help\n")
    app.run(debug=True, port=5000)
