"""Test stress event processing and alert generation."""
import pytest
import io
import numpy as np
from scipy.io import wavfile
from datetime import datetime


def create_test_audio():
    """Create a test audio file."""
    sample_rate = 16000
    duration = 2.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio_data = (np.sin(2 * np.pi * 440 * t) * 32767).astype(np.int16)
    
    byte_io = io.BytesIO()
    wavfile.write(byte_io, sample_rate, audio_data)
    byte_io.seek(0)
    return byte_io


class TestEventsAndAlerts:
    """Test suite for event processing and alert generation."""
    
    def test_event_with_audio(self, client, test_device, test_app):
        """Test sending event with audio file."""
        audio_file = create_test_audio()
        
        response = client.post('/api/device/event', data={
            'device_uid': test_device,
            'heart_rate': 75,
            'temperature': 36.5,
            'lat': 11.9416,
            'lng': 79.8083
        }, content_type='multipart/form-data',
        files={'audio': (audio_file, 'test_audio.wav')})
        
        assert response.status_code == 200
        assert 'distress_score' in response.json
    
    def test_alert_creation_high_heart_rate(self, client, test_device, test_app):
        """Test alert creation when heart rate exceeds threshold."""
        response = client.post('/api/device/event', data={
            'device_uid': test_device,
            'heart_rate': 120,  # High heart rate
            'temperature': 36.5,
            'lat': 11.9416,
            'lng': 79.8083
        })
        
        assert response.status_code == 200
        assert response.json.get('alert_triggered') is True
        
        # Verify alert was created in database
        with test_app.app_context():
            from run import Alert, Device
            device = Device.query.filter_by(device_uid=test_device).first()
            alert = Alert.query.filter_by(device_id=device.id).first()
            assert alert is not None
            assert alert.status == 'NEW'
    
    def test_alert_creation_high_temperature(self, client, test_device, test_app):
        """Test alert creation when temperature exceeds threshold."""
        response = client.post('/api/device/event', data={
            'device_uid': test_device,
            'heart_rate': 75,
            'temperature': 39.5,  # High temperature
            'lat': 11.9416,
            'lng': 79.8083
        })
        
        assert response.status_code == 200
    
    def test_manual_sos_trigger(self, client, test_device, test_app):
        """Test manual SOS button trigger."""
        response = client.post('/api/device/event', data={
            'device_uid': test_device,
            'heart_rate': 75,
            'temperature': 36.5,
            'manual_sos': 1,  # Manual SOS
            'lat': 11.9416,
            'lng': 79.8083
        })
        
        assert response.status_code == 200
        assert response.json.get('alert_triggered') is True
        
        # Verify alert reason
        with test_app.app_context():
            from run import Alert, Device
            device = Device.query.filter_by(device_uid=test_device).first()
            alert = Alert.query.filter_by(device_id=device.id).order_by(Alert.timestamp.desc()).first()
            assert alert.reason == 'MANUAL_SOS'
    
    def test_no_duplicate_alerts(self, client, test_device, test_app):
        """Test that duplicate alerts are not created for same condition."""
        # Send first high heart rate event
        client.post('/api/device/event', data={
            'device_uid': test_device,
            'heart_rate': 120,
            'temperature': 36.5,
            'lat': 11.9416,
            'lng': 79.8083
        })
        
        # Send second high heart rate event (should not create new alert)
        response = client.post('/api/device/event', data={
            'device_uid': test_device,
            'heart_rate': 125,
            'temperature': 36.5,
            'lat': 11.9416,
            'lng': 79.8083
        })
        
        assert response.status_code == 200
        
        # Count alerts
        with test_app.app_context():
            from run import Alert, Device
            device = Device.query.filter_by(device_uid=test_device).first()
            alert_count = Alert.query.filter_by(device_id=device.id, status='NEW').count()
            assert alert_count == 1  # Only one NEW alert should exist
    
    def test_list_alerts_guardian(self, client, guardian_token, test_device, test_app):
        """Test guardian can list their device alerts."""
        # Create an alert first
        client.post('/api/device/event', data={
            'device_uid': test_device,
            'heart_rate': 120,
            'lat': 11.9416,
            'lng': 79.8083
        })
        
        response = client.get(
            '/api/alerts',
            headers={'Authorization': f'Bearer {guardian_token}'}
        )
        
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) > 0
    
    def test_get_alert_details(self, client, guardian_token, test_device, test_app):
        """Test getting detailed alert information."""
        # Create alert
        client.post('/api/device/event', data={
            'device_uid': test_device,
            'heart_rate': 120,
            'lat': 11.9416,
            'lng': 79.8083
        })
        
        # Get alert ID
        with test_app.app_context():
            from run import Alert, Device
            device = Device.query.filter_by(device_uid=test_device).first()
            alert = Alert.query.filter_by(device_id=device.id).first()
            alert_id = alert.id
        
        response = client.get(
            f'/api/alerts/{alert_id}',
            headers={'Authorization': f'Bearer {guardian_token}'}
        )
        
        assert response.status_code == 200
        assert 'device_uid' in response.json
        assert 'status' in response.json
        assert 'evidence' in response.json
    
    def test_update_alert_status_police(self, client, police_token, test_device, test_app):
        """Test police can update alert status."""
        # Create alert
        client.post('/api/device/event', data={
            'device_uid': test_device,
            'heart_rate': 120,
            'lat': 11.9416,
            'lng': 79.8083
        })
        
        # Get alert ID
        with test_app.app_context():
            from run import Alert, Device
            device = Device.query.filter_by(device_uid=test_device).first()
            alert = Alert.query.filter_by(device_id=device.id).first()
            alert_id = alert.id
        
        response = client.patch(
            f'/api/alerts/{alert_id}/status',
            headers={'Authorization': f'Bearer {police_token}'},
            json={'status': 'IN_PROGRESS'}
        )
        
        assert response.status_code == 200
    
    def test_update_alert_status_guardian_denied(self, client, guardian_token, test_device, test_app):
        """Test guardian cannot update alert status."""
        # Create alert
        client.post('/api/device/event', data={
            'device_uid': test_device,
            'heart_rate': 120,
            'lat': 11.9416,
            'lng': 79.8083
        })
        
        # Get alert ID
        with test_app.app_context():
            from run import Alert, Device
            device = Device.query.filter_by(device_uid=test_device).first()
            alert = Alert.query.filter_by(device_id=device.id).first()
            alert_id = alert.id
        
        response = client.patch(
            f'/api/alerts/{alert_id}/status',
            headers={'Authorization': f'Bearer {guardian_token}'},
            json={'status': 'RESOLVED'}
        )
        
        assert response.status_code == 403
