"""Test device management functionality."""
import pytest
import io
from datetime import datetime


class TestDeviceManagement:
    """Test suite for device endpoints."""
    
    def test_register_device_with_token(self, client, guardian_token):
        """Test device registration with JWT token."""
        response = client.post(
            '/api/device/register',
            headers={'Authorization': f'Bearer {guardian_token}'},
            json={'device_uid': 'NEW_DEVICE_001'}
        )
        
        assert response.status_code == 201
        assert 'id' in response.json
    
    def test_register_device_with_email(self, client):
        """Test device registration with email (no token)."""
        response = client.post('/api/device/register', json={
            'device_uid': 'EMAIL_DEVICE_001',
            'email': 'guardian@test.com'
        })
        
        assert response.status_code == 201
    
    def test_register_device_missing_uid(self, client, guardian_token):
        """Test device registration without device_uid."""
        response = client.post(
            '/api/device/register',
            headers={'Authorization': f'Bearer {guardian_token}'},
            json={}
        )
        
        assert response.status_code == 400
    
    def test_get_my_devices(self, client, guardian_token, test_device):
        """Test retrieving user's devices."""
        response = client.get(
            '/api/device/my-devices',
            headers={'Authorization': f'Bearer {guardian_token}'}
        )
        
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) > 0
        
        device = response.json[0]
        assert 'uid' in device
        assert 'battery' in device
        assert 'location' in device
        assert 'latest_vitals' in device
    
    def test_device_heartbeat(self, client, test_device):
        """Test device heartbeat/status update."""
        response = client.post('/api/device/event', data={
            'device_uid': test_device,
            'heart_rate': 75,
            'temperature': 36.5,
            'lat': 11.9416,
            'lng': 79.8083
        })
        
        assert response.status_code == 200
        assert 'status' in response.json
        assert response.json['status'] == 'success'
    
    def test_device_event_unknown_device(self, client):
        """Test sending event from unknown device."""
        response = client.post('/api/device/event', data={
            'device_uid': 'UNKNOWN_DEVICE',
            'heart_rate': 75
        })
        
        assert response.status_code == 404
