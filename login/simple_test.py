#!/usr/bin/env python3
"""
Simple test to verify authentication is working
"""
import requests
import json
from datetime import datetime

def test_endpoints():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing authentication endpoints...")
    
    # Test 1: Try to register a user using the existing endpoint
    print("\n1. Testing registration...")
    test_email = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
    
    register_data = {
        "email": test_email,
        "password": "TestPassword123",
        "firstName": "Test",
        "lastName": "User",
        "organizationName": "Test Org"
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/register", json=register_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Registration successful!")
            data = response.json()
            access_token = data.get("access_token")
            
            # Test 2: Try to get user profile
            if access_token:
                print("\n2. Testing user profile...")
                headers = {"Authorization": f"Bearer {access_token}"}
                me_response = requests.get(f"{base_url}/api/auth/me", headers=headers)
                print(f"Status: {me_response.status_code}")
                print(f"Response: {me_response.text}")
                
                if me_response.status_code == 200:
                    print("✅ User profile retrieved successfully!")
                else:
                    print("❌ Failed to get user profile")
            
            # Test 3: Try login
            print("\n3. Testing login...")
            login_data = {
                "username": test_email,
                "password": "TestPassword123"
            }
            login_response = requests.post(
                f"{base_url}/api/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            print(f"Status: {login_response.status_code}")
            print(f"Response: {login_response.text}")
            
            if login_response.status_code == 200:
                print("✅ Login successful!")
            else:
                print("❌ Login failed")
        else:
            print("❌ Registration failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_endpoints()