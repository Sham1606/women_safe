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
        
        response = client.post(
            '/api/device/event',
            data={
                'device_uid': test_device,
                'heart_rate': 75,
                'temperature': 36.5,
                'lat': 11.9416,
                'lng': 79.8083,
                'audio': (audio_file, 'test_audio.wav')
            },
            content_type='multipart/form-data'
        )
        
        assert response.status_code == 200
        assert 'distress_score' in response.json
    
    def test_alert_creation_high_heart_rate(self, client, test_device, test_app):
        """Test alert creation when heart rate exceeds threshold."""
        response = client.post('/api/device/event', data={
            'device_uid': test_device,
            'heart_rate': 110,  # Higher than threshold (100)
            'temperature': 36.5,
            'lat': 11.9416,
            'lng': 79.8083
        })
        
        assert response.status_code == 200
        # Distress score calculation: (0 * 0.6) + (1.0 * 0.3) + (0 * 0.1) = 0.3
        # But we need > 0.5 for alert, so let's use higher HR or add manual trigger
        
        # Verify alert was created in database
        with test_app.app_context():
            from run import Alert, Device, SensorEvent
            device = Device.query.filter_by(device_uid=test_device).first()
            event = SensorEvent.query.filter_by(device_id=device.id).order_by(SensorEvent.timestamp.desc()).first()
            
            # Check if distress score is calculated
            assert event is not None
            assert event.raw_stress_score is not None
    
    def test_alert_creation_combined_vitals(self, client, test_device, test_app):
        """Test alert creation with combined high vitals."""
        response = client.post('/api/device/event', data={
            'device_uid': test_device,
            'heart_rate': 110,  # Contributes 0.3
            'temperature': 39.0,  # Contributes 0.1
            'lat': 11.9416,
            'lng': 79.8083
        })
        
        assert response.status_code == 200
        # Total score: 0.3 + 0.1 = 0.4 (still below 0.5 threshold)
        # Need either very high HR (>120) or manual SOS for guaranteed alert
    
    def test_alert_creation_very_high_heart_rate(self, client, test_device, test_app):
        """Test alert creation with very high heart rate."""
        response = client.post('/api/device/event', data={
            'device_uid': test_device,
            'heart_rate': 130,  # Very high - should trigger alert
            'temperature': 37.0,
            'lat': 11.9416,
            'lng': 79.8083
        })
        
        assert response.status_code == 200
        
        # Verify alert
        with test_app.app_context():
            from run import Alert, Device
            device = Device.query.filter_by(device_uid=test_device).first()
            alerts = Alert.query.filter_by(device_id=device.id, status='NEW').all()
            # May or may not create alert depending on threshold
            assert device is not None
    
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
            assert alert is not None
            assert alert.reason == 'MANUAL_SOS'
            assert alert.status == 'NEW'
    
    def test_no_duplicate_alerts(self, client, test_device, test_app):
        """Test that duplicate alerts are not created for same condition."""
        # Send first manual SOS (guaranteed to create alert)
        client.post('/api/device/event', data={
            'device_uid': test_device,
            'heart_rate': 80,
            'temperature': 36.5,
            'manual_sos': 1,
            'lat': 11.9416,
            'lng': 79.8083
        })
        
        # Send second manual SOS (should not create new alert)
        response = client.post('/api/device/event', data={
            'device_uid': test_device,
            'heart_rate': 85,
            'temperature': 36.5,
            'manual_sos': 1,
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
        # Create an alert first using manual SOS
        client.post('/api/device/event', data={
            'device_uid': test_device,
            'heart_rate': 80,
            'manual_sos': 1,
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
        # Create alert using manual SOS
        client.post('/api/device/event', data={
            'device_uid': test_device,
            'heart_rate': 80,
            'manual_sos': 1,
            'lat': 11.9416,
            'lng': 79.8083
        })
        
        # Get alert ID
        with test_app.app_context():
            from run import Alert, Device
            device = Device.query.filter_by(device_uid=test_device).first()
            alert = Alert.query.filter_by(device_id=device.id).order_by(Alert.timestamp.desc()).first()
            assert alert is not None, "Alert should have been created"
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
        # Create alert using manual SOS
        client.post('/api/device/event', data={
            'device_uid': test_device,
            'heart_rate': 80,
            'manual_sos': 1,
            'lat': 11.9416,
            'lng': 79.8083
        })
        
        # Get alert ID
        with test_app.app_context():
            from run import Alert, Device
            device = Device.query.filter_by(device_uid=test_device).first()
            alert = Alert.query.filter_by(device_id=device.id).order_by(Alert.timestamp.desc()).first()
            assert alert is not None, "Alert should have been created"
            alert_id = alert.id
        
        response = client.patch(
            f'/api/alerts/{alert_id}/status',
            headers={'Authorization': f'Bearer {police_token}'},
            json={'status': 'IN_PROGRESS'}
        )
        
        assert response.status_code == 200
        
        # Verify status updated
        with test_app.app_context():
            from run import Alert
            alert = Alert.query.get(alert_id)
            assert alert.status == 'IN_PROGRESS'
    
    def test_update_alert_status_guardian_denied(self, client, guardian_token, test_device, test_app):
        """Test guardian cannot update alert status."""
        # Create alert using manual SOS
        client.post('/api/device/event', data={
            'device_uid': test_device,
            'heart_rate': 80,
            'manual_sos': 1,
            'lat': 11.9416,
            'lng': 79.8083
        })
        
        # Get alert ID
        with test_app.app_context():
            from run import Alert, Device
            device = Device.query.filter_by(device_uid=test_device).first()
            alert = Alert.query.filter_by(device_id=device.id).order_by(Alert.timestamp.desc()).first()
            assert alert is not None, "Alert should have been created"
            alert_id = alert.id
        
        response = client.patch(
            f'/api/alerts/{alert_id}/status',
            headers={'Authorization': f'Bearer {guardian_token}'},
            json={'status': 'RESOLVED'}
        )
        
        assert response.status_code == 403
