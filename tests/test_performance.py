"""Test performance and reliability."""
import pytest
import time
import concurrent.futures
from datetime import datetime


class TestPerformance:
    """Test suite for performance and reliability."""
    
    def test_event_processing_time(self, client, test_device):
        """Test that event processing completes within acceptable time."""
        start_time = time.time()
        
        response = client.post('/api/device/event', data={
            'device_uid': test_device,
            'heart_rate': 75,
            'temperature': 36.5,
            'lat': 11.9416,
            'lng': 79.8083
        })
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert response.status_code == 200
        assert duration < 2.0, f"Event processing took {duration:.2f}s, should be under 2s"
    
    def test_burst_heartbeats(self, client, test_device):
        """Test handling burst of multiple heartbeats."""
        num_requests = 30
        success_count = 0
        
        for i in range(num_requests):
            response = client.post('/api/device/event', data={
                'device_uid': test_device,
                'heart_rate': 70 + i % 10,
                'temperature': 36.0 + (i % 5) * 0.2,
                'lat': 11.9416,
                'lng': 79.8083
            })
            
            if response.status_code == 200:
                success_count += 1
        
        # At least 90% should succeed
        assert success_count >= num_requests * 0.9
    
    def test_api_response_time(self, client, guardian_token):
        """Test that API endpoints respond quickly."""
        endpoints = [
            ('/api/auth/me', 'GET'),
            ('/api/device/my-devices', 'GET'),
            ('/api/alerts', 'GET')
        ]
        
        for endpoint, method in endpoints:
            start = time.time()
            
            if method == 'GET':
                response = client.get(
                    endpoint,
                    headers={'Authorization': f'Bearer {guardian_token}'}
                )
            
            duration = time.time() - start
            
            assert response.status_code in [200, 404]
            assert duration < 1.0, f"{endpoint} took {duration:.2f}s"
    
    def test_database_consistency(self, client, test_device, test_app):
        """Test database consistency after multiple operations."""
        # Send multiple events
        for i in range(10):
            client.post('/api/device/event', data={
                'device_uid': test_device,
                'heart_rate': 70 + i,
                'temperature': 36.5,
                'lat': 11.9416,
                'lng': 79.8083
            })
        
        # Verify all events are in database
        with test_app.app_context():
            from run import SensorEvent, Device
            device = Device.query.filter_by(device_uid=test_device).first()
            event_count = SensorEvent.query.filter_by(device_id=device.id).count()
            assert event_count >= 10
