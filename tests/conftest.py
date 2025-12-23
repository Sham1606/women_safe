"""Pytest configuration and shared fixtures."""
import os
import sys
import pytest
import tempfile
from datetime import datetime

# Add parent directory to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import config
from run import app, db, User, Device, Alert, SensorEvent, Evidence
from werkzeug.security import generate_password_hash


@pytest.fixture(scope='function')
def test_app():
    """Create and configure a test Flask application."""
    # Create temporary database
    db_fd, db_path = tempfile.mkstemp()
    evidence_dir = tempfile.mkdtemp()
    
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    app.config['EVIDENCE_DIR'] = evidence_dir
    config.EVIDENCE_DIR = evidence_dir
    
    with app.app_context():
        db.create_all()
        # Seed test users
        guardian = User(
            name='Test Guardian',
            email='guardian@test.com',
            password_hash=generate_password_hash('test123', method='pbkdf2:sha256'),
            role='GUARDIAN',
            phone='1234567890'
        )
        police = User(
            name='Test Police',
            email='police@test.com',
            password_hash=generate_password_hash('police123', method='pbkdf2:sha256'),
            role='POLICE'
        )
        admin = User(
            name='Test Admin',
            email='admin@test.com',
            password_hash=generate_password_hash('admin123', method='pbkdf2:sha256'),
            role='ADMIN'
        )
        db.session.add_all([guardian, police, admin])
        db.session.commit()
        
    yield app
    
    # Cleanup
    with app.app_context():
        db.session.remove()
        db.drop_all()
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture(scope='function')
def client(test_app):
    """Create a test client."""
    return test_app.test_client()


@pytest.fixture(scope='function')
def guardian_token(client):
    """Get JWT token for guardian user."""
    response = client.post('/api/auth/login', json={
        'email': 'guardian@test.com',
        'password': 'test123'
    })
    return response.json['access_token']


@pytest.fixture(scope='function')
def police_token(client):
    """Get JWT token for police user."""
    response = client.post('/api/auth/login', json={
        'email': 'police@test.com',
        'password': 'police123'
    })
    return response.json['access_token']


@pytest.fixture(scope='function')
def admin_token(client):
    """Get JWT token for admin user."""
    response = client.post('/api/auth/login', json={
        'email': 'admin@test.com',
        'password': 'admin123'
    })
    return response.json['access_token']


@pytest.fixture(scope='function')
def test_device(test_app, guardian_token):
    """Create a test device linked to guardian."""
    with test_app.app_context():
        guardian = User.query.filter_by(email='guardian@test.com').first()
        device = Device(
            device_uid='TEST_DEVICE_001',
            owner_id=guardian.id,
            is_active=True,
            battery_level=85,
            last_lat=11.9416,
            last_lng=79.8083
        )
        db.session.add(device)
        db.session.commit()
        return device.device_uid
