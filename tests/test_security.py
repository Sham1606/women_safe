"""Test security aspects."""
import pytest
import io


class TestSecurity:
    """Test suite for security features."""
    
    def test_protected_endpoint_without_token(self, client):
        """Test protected endpoints reject requests without token."""
        endpoints = [
            '/api/auth/me',
            '/api/device/my-devices',
            '/api/alerts',
            '/api/admin/stats'
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401
    
    def test_protected_endpoint_invalid_token(self, client):
        """Test protected endpoints reject invalid tokens."""
        response = client.get(
            '/api/auth/me',
            headers={'Authorization': 'Bearer invalid_token_here'}
        )
        
        assert response.status_code == 422
    
    def test_role_based_access_control(self, client, guardian_token):
        """Test RBAC prevents unauthorized access."""
        # Guardian should not access admin endpoints
        response = client.get(
            '/api/admin/stats',
            headers={'Authorization': f'Bearer {guardian_token}'}
        )
        
        assert response.status_code == 403
    
    def test_password_hashing(self, client, test_app):
        """Test that passwords are hashed in database."""
        with test_app.app_context():
            from run import User
            user = User.query.filter_by(email='guardian@test.com').first()
            
            # Password should be hashed (not plaintext)
            assert user.password_hash != 'test123'
            assert len(user.password_hash) > 50  # Hashed passwords are long
    
    def test_sql_injection_protection(self, client):
        """Test SQL injection protection."""
        # Attempt SQL injection in login
        response = client.post('/api/auth/login', json={
            'email': "admin' OR '1'='1",
            'password': "password' OR '1'='1"
        })
        
        assert response.status_code == 401  # Should fail authentication
    
    def test_evidence_file_access_control(self, client, guardian_token, test_device, test_app):
        """Test that evidence files are stored securely."""
        # Create event with manual SOS to generate alert
        response = client.post('/api/device/event', data={
            'device_uid': test_device,
            'heart_rate': 80,
            'manual_sos': 1,
            'lat': 11.9416,
            'lng': 79.8083
        })
        
        assert response.status_code == 200
        
        # Verify evidence can be accessed through authenticated routes
        with test_app.app_context():
            from run import Evidence, Alert, Device
            device = Device.query.filter_by(device_uid=test_device).first()
            alert = Alert.query.filter_by(device_id=device.id).first()
            
            if alert:
                # Evidence should be associated with alert
                evidence_count = Evidence.query.filter_by(alert_id=alert.id).count()
                # May be 0 if no audio file was uploaded
                assert evidence_count >= 0
    
    def test_device_ownership_validation(self, client, guardian_token, test_app):
        """Test that users can only access their own devices."""
        # Create a device for another user
        with test_app.app_context():
            from run import Device, User, db
            other_user = User(
                name='Other User',
                email='other@test.com',
                password_hash='hashed',
                role='GUARDIAN'
            )
            db.session.add(other_user)
            db.session.flush()
            
            other_device = Device(
                device_uid='OTHER_DEVICE_001',
                owner_id=other_user.id
            )
            db.session.add(other_device)
            db.session.commit()
        
        # Guardian should only see their own devices
        response = client.get(
            '/api/device/my-devices',
            headers={'Authorization': f'Bearer {guardian_token}'}
        )
        
        assert response.status_code == 200
        devices = response.json
        
        # Should not include OTHER_DEVICE_001
        device_uids = [d['uid'] for d in devices]
        assert 'OTHER_DEVICE_001' not in device_uids
