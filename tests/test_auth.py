"""
Tests for authentication functionality
"""
import pytest
from httpx import AsyncClient


class TestUserRegistration:
    """Test user registration functionality"""
    
    async def test_register_new_user(self, client: AsyncClient):
        """Test registering a new user"""
        user_data = {
            "email": "newuser@example.com",
            "full_name": "New User",
            "password": "securepassword123",
            "organization_name": "New Organization"
        }
        
        response = await client.post("/api/auth/register", json=user_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        """Test registering with existing email fails"""
        user_data = {
            "email": test_user.email,
            "full_name": "Duplicate User",
            "password": "password123",
            "organization_name": "Duplicate Org"
        }
        
        response = await client.post("/api/auth/register", json=user_data)
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]


class TestUserLogin:
    """Test user login functionality"""
    
    async def test_login_valid_credentials(self, client: AsyncClient, test_user):
        """Test login with valid credentials"""
        response = await client.post("/api/auth/login", data={
            "username": test_user.email,
            "password": "testpassword123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    async def test_login_invalid_credentials(self, client: AsyncClient, test_user):
        """Test login with invalid credentials"""
        response = await client.post("/api/auth/login", data={
            "username": test_user.email,
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]
    
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with non-existent user"""
        response = await client.post("/api/auth/login", data={
            "username": "nonexistent@example.com",
            "password": "password123"
        })
        
        assert response.status_code == 401


class TestAPIKeys:
    """Test API key management"""
    
    async def test_create_api_key(self, authenticated_client: AsyncClient):
        """Test creating a new API key"""
        key_data = {
            "name": "Test API Key",
            "scopes": ["llm:generate"],
            "rate_limit_per_minute": 100
        }
        
        response = await authenticated_client.post("/api/auth/api-keys", json=key_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == key_data["name"]
        assert "api_key" in data
        assert data["api_key"].startswith("llm_")
    
    async def test_list_api_keys(self, authenticated_client: AsyncClient, test_api_key):
        """Test listing API keys"""
        response = await authenticated_client.get("/api/auth/api-keys")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    async def test_delete_api_key(self, authenticated_client: AsyncClient, test_api_key):
        """Test deleting an API key"""
        api_key_obj, _ = test_api_key
        
        response = await authenticated_client.delete(f"/api/auth/api-keys/{api_key_obj.id}")
        assert response.status_code == 200
        
        # Verify it's no longer in the list
        response = await authenticated_client.get("/api/auth/api-keys")
        data = response.json()
        
        # Should not find the deleted key (or should be marked as deleted)
        active_keys = [key for key in data if key["is_active"]]
        assert not any(key["id"] == str(api_key_obj.id) for key in active_keys)


class TestUserProfile:
    """Test user profile functionality"""
    
    async def test_get_current_user(self, authenticated_client: AsyncClient, test_user):
        """Test getting current user information"""
        response = await authenticated_client.get("/api/auth/me")
        assert response.status_code == 200
        
        data = response.json()
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name
        assert data["role"] == test_user.role.value