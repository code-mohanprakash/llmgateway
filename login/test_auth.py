#!/usr/bin/env python3
"""
Enterprise Authentication Test Suite
Tests all authentication endpoints to ensure they work correctly
"""
import asyncio
import httpx
import json
from datetime import datetime

class AuthTestSuite:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.test_email = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
        self.test_password = "TestPassword123"
        self.test_user_data = {
            "email": self.test_email,
            "password": self.test_password,
            "firstName": "Test",
            "lastName": "User",
            "organizationName": "Test Organization"
        }
        self.access_token = None
        self.refresh_token = None
    
    async def test_register(self):
        """Test user registration"""
        print(f"🔧 Testing user registration with email: {self.test_email}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/auth/register",
                json=self.test_user_data
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.access_token = data.get("access_token")
                    self.refresh_token = data.get("refresh_token")
                    print("✅ Registration successful!")
                    return True
                else:
                    print(f"❌ Registration failed: {data.get('message')}")
                    return False
            else:
                print(f"❌ Registration failed with status {response.status_code}")
                return False
    
    async def test_login(self):
        """Test user login"""
        print(f"🔧 Testing user login with email: {self.test_email}")
        
        async with httpx.AsyncClient() as client:
            # Send as form data for OAuth2PasswordRequestForm
            response = await client.post(
                f"{self.base_url}/api/auth/login",
                data={
                    "username": self.test_email,
                    "password": self.test_password
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.access_token = data.get("access_token")
                    self.refresh_token = data.get("refresh_token")
                    print("✅ Login successful!")
                    return True
                else:
                    print(f"❌ Login failed: {data.get('message')}")
                    return False
            else:
                print(f"❌ Login failed with status {response.status_code}")
                return False
    
    async def test_me_endpoint(self):
        """Test getting user profile"""
        print("🔧 Testing /auth/me endpoint")
        
        if not self.access_token:
            print("❌ No access token available")
            return False
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/auth/me",
                headers={
                    "Authorization": f"Bearer {self.access_token}"
                }
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                print("✅ User profile retrieved successfully!")
                return True
            else:
                print(f"❌ Failed to get user profile: {response.status_code}")
                return False
    
    async def test_forgot_password(self):
        """Test forgot password"""
        print("🔧 Testing forgot password")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/auth/forgot-password",
                json={"email": self.test_email}
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print("✅ Forgot password request successful!")
                    return True
                else:
                    print(f"❌ Forgot password failed: {data.get('message')}")
                    return False
            else:
                print(f"❌ Forgot password failed with status {response.status_code}")
                return False
    
    async def test_refresh_token(self):
        """Test token refresh"""
        print("🔧 Testing token refresh")
        
        if not self.refresh_token:
            print("❌ No refresh token available")
            return False
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/auth/refresh",
                json={"refresh_token": self.refresh_token}
            )
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.access_token = data.get("access_token")
                    self.refresh_token = data.get("refresh_token")
                    print("✅ Token refresh successful!")
                    return True
                else:
                    print(f"❌ Token refresh failed: {data.get('message')}")
                    return False
            else:
                print(f"❌ Token refresh failed with status {response.status_code}")
                return False
    
    async def run_all_tests(self):
        """Run all authentication tests"""
        print("🚀 Starting Enterprise Authentication Test Suite")
        print("=" * 60)
        
        tests = [
            ("Registration", self.test_register),
            ("Login", self.test_login),
            ("User Profile", self.test_me_endpoint),
            ("Forgot Password", self.test_forgot_password),
            ("Token Refresh", self.test_refresh_token),
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n📋 Running {test_name} test...")
            try:
                result = await test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} test error: {e}")
                results.append((test_name, False))
            print("-" * 40)
        
        # Summary
        print("\n📊 Test Results Summary:")
        print("=" * 60)
        passed = 0
        total = len(results)
        
        for test_name, passed_test in results:
            status = "✅ PASSED" if passed_test else "❌ FAILED"
            print(f"{test_name:<20} {status}")
            if passed_test:
                passed += 1
        
        print(f"\nOverall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All authentication tests passed! Enterprise-level authentication is working correctly.")
        else:
            print("⚠️  Some tests failed. Please check the error messages above.")
        
        return passed == total


async def main():
    """Main test runner"""
    test_suite = AuthTestSuite()
    success = await test_suite.run_all_tests()
    return success


if __name__ == "__main__":
    asyncio.run(main())