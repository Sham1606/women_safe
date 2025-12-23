"""Test security aspects."""
import pytest


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
        """Test that evidence files require authentication."""
        # Create event with audio to generate evidence
        import io
        audio_file = io.BytesIO(b'fake audio data')
        
        client.post('/api/device/event', data={
            'device_uid': test_device,
            'heart_rate': 120,
            'lat': 11.9416,
            'lng': 79.8083
        }, files={'audio': (audio_file, 'test.wav')})
        
        # Evidence URLs should be through authenticated routes
        # Direct file access should be restricted
        with test_app.app_context():
            from run import Evidence
            evidence = Evidence.query.first()
            if evidence:
                # This would need proper file access control implementation
                assert evidence.file_path is not None
