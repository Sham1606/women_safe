"""Test admin functionality."""
import pytest


class TestAdminFunctionality:
    """Test suite for admin endpoints."""
    
    def test_admin_stats_access(self, client, admin_token):
        """Test admin can access statistics."""
        response = client.get(
            '/api/admin/stats',
            headers={'Authorization': f'Bearer {admin_token}'}
        )
        
        assert response.status_code == 200
        assert 'total_users' in response.json
        assert 'active_devices' in response.json
        assert 'alerts_by_status' in response.json
        assert 'latest_alerts' in response.json
    
    def test_police_stats_access(self, client, police_token):
        """Test police can access statistics."""
        response = client.get(
            '/api/admin/stats',
            headers={'Authorization': f'Bearer {police_token}'}
        )
        
        assert response.status_code == 200
    
    def test_guardian_stats_denied(self, client, guardian_token):
        """Test guardian cannot access admin statistics."""
        response = client.get(
            '/api/admin/stats',
            headers={'Authorization': f'Bearer {guardian_token}'}
        )
        
        assert response.status_code == 403
    
    def test_stats_unauthenticated(self, client):
        """Test unauthenticated access to stats is denied."""
        response = client.get('/api/admin/stats')
        
        assert response.status_code == 401
