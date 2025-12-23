"""Test authentication and authorization functionality."""
import pytest
import jwt
from datetime import datetime, timedelta


class TestAuthentication:
    """Test suite for authentication endpoints."""
    
    def test_register_success(self, client):
        """Test successful user registration."""
        response = client.post('/api/auth/register', json={
            'name': 'New User',
            'email': 'newuser@test.com',
            'password': 'newpass123',
            'role': 'GUARDIAN'
        })
        
        assert response.status_code == 201
        assert 'message' in response.json
    
    def test_register_duplicate_email(self, client):
        """Test registration with existing email fails."""
        response = client.post('/api/auth/register', json={
            'name': 'Duplicate',
            'email': 'guardian@test.com',  # Already exists
            'password': 'pass123'
        })
        
        assert response.status_code == 400
        assert 'already exists' in response.json['message'].lower()
    
    def test_register_missing_fields(self, client):
        """Test registration with missing required fields."""
        response = client.post('/api/auth/register', json={
            'email': 'incomplete@test.com'
            # Missing name and password
        })
        
        assert response.status_code == 400
    
    def test_login_success(self, client):
        """Test successful login."""
        response = client.post('/api/auth/login', json={
            'email': 'guardian@test.com',
            'password': 'test123'
        })
        
        assert response.status_code == 200
        assert 'access_token' in response.json
        assert 'user' in response.json
        assert response.json['user']['email'] == 'guardian@test.com'
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        response = client.post('/api/auth/login', json={
            'email': 'guardian@test.com',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
    
    def test_login_missing_fields(self, client):
        """Test login with missing fields."""
        response = client.post('/api/auth/login', json={
            'email': 'guardian@test.com'
            # Missing password
        })
        
        assert response.status_code == 400
    
    def test_jwt_token_structure(self, client, guardian_token):
        """Test JWT token contains correct claims."""
        # Decode token without verification (for testing)
        decoded = jwt.decode(guardian_token, options={"verify_signature": False})
        
        assert 'sub' in decoded  # Subject (user_id)
        assert 'role' in decoded  # Role claim
        assert decoded['role'] == 'GUARDIAN'
    
    def test_get_me_authenticated(self, client, guardian_token):
        """Test getting current user info with valid token."""
        response = client.get(
            '/api/auth/me',
            headers={'Authorization': f'Bearer {guardian_token}'}
        )
        
        assert response.status_code == 200
        assert response.json['email'] == 'guardian@test.com'
        assert response.json['role'] == 'GUARDIAN'
    
    def test_get_me_unauthenticated(self, client):
        """Test getting current user without token."""
        response = client.get('/api/auth/me')
        
        assert response.status_code == 401
    
    def test_get_me_invalid_token(self, client):
        """Test getting current user with invalid token."""
        response = client.get(
            '/api/auth/me',
            headers={'Authorization': 'Bearer invalid_token'}
        )
        
        assert response.status_code == 422  # Unprocessable Entity
