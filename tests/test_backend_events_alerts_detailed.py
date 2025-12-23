"""Additional detailed tests for event processing with different scenarios."""
import pytest


class TestEventProcessingDetailed:
    """Detailed test cases for various event processing scenarios."""
    
    def test_event_normal_vitals(self, client, test_device):
        """Test event with normal vitals (no alert expected)."""
        response = client.post('/api/device/event', data={
            'device_uid': test_device,
            'heart_rate': 75,
            'temperature': 36.8,
            'lat': 11.9416,
            'lng': 79.8083
        })
        
        assert response.status_code == 200
        assert response.json['alert_triggered'] is False
        assert response.json['distress_score'] < 0.5
    
    def test_event_missing_vitals(self, client, test_device):
        """Test event with missing vital signs."""
        response = client.post('/api/device/event', data={
            'device_uid': test_device,
            'lat': 11.9416,
            'lng': 79.8083
        })
        
        assert response.status_code == 200
        # Should handle gracefully with default values
    
    def test_event_missing_gps(self, client, test_device):
        """Test event without GPS coordinates."""
        response = client.post('/api/device/event', data={
            'device_uid': test_device,
            'heart_rate': 75,
            'temperature': 36.5
        })
        
        assert response.status_code == 200
        # Should work without GPS (optional field)
    
    def test_manual_sos_override(self, client, test_device):
        """Test that manual SOS overrides all other factors."""
        response = client.post('/api/device/event', data={
            'device_uid': test_device,
            'heart_rate': 60,  # Low/normal HR
            'temperature': 36.0,  # Normal temp
            'manual_sos': 1,  # But manual SOS pressed
            'lat': 11.9416,
            'lng': 79.8083
        })
        
        assert response.status_code == 200
        assert response.json['alert_triggered'] is True
    
    def test_distress_score_calculation(self, client, test_device):
        """Test distress score calculation formula."""
        # Test case: HR=110 (>100), Temp=39.0 (>38.5)
        # Expected: (0 * 0.6) + (1.0 * 0.3) + (1.0 * 0.1) = 0.4
        response = client.post('/api/device/event', data={
            'device_uid': test_device,
            'heart_rate': 110,
            'temperature': 39.0,
            'lat': 11.9416,
            'lng': 79.8083
        })
        
        assert response.status_code == 200
        # Distress score should be around 0.4
        assert 0.35 <= response.json['distress_score'] <= 0.45
    
    def test_extreme_vitals(self, client, test_device):
        """Test handling of extreme vital values."""
        response = client.post('/api/device/event', data={
            'device_uid': test_device,
            'heart_rate': 200,  # Extremely high
            'temperature': 42.0,  # Dangerously high
            'lat': 11.9416,
            'lng': 79.8083
        })
        
        assert response.status_code == 200
        # Should create alert with HIGH severity
    
    def test_device_location_update(self, client, test_device, test_app):
        """Test that device location is updated on event."""
        new_lat = 12.9716
        new_lng = 77.5946
        
        response = client.post('/api/device/event', data={
            'device_uid': test_device,
            'heart_rate': 75,
            'temperature': 36.5,
            'lat': new_lat,
            'lng': new_lng
        })
        
        assert response.status_code == 200
        
        # Verify location updated in database
        with test_app.app_context():
            from run import Device
            device = Device.query.filter_by(device_uid=test_device).first()
            assert device.last_lat == new_lat
            assert device.last_lng == new_lng
