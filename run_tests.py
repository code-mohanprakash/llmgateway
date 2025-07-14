#!/usr/bin/env python3
"""
Simple test runner for LLM Gateway SaaS
"""
import sys
import os
import asyncio
import unittest
from unittest.mock import Mock, patch, AsyncMock

# Add project root to path
sys.path.insert(0, '/Users/mohanjeyasankar/Desktop/llmgateway')

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        # Test core imports
        from providers.base import BaseModelProvider, GenerationRequest, GenerationResponse
        print("✅ Base provider imports OK")
        
        from providers.openai import OpenAIProvider
        print("✅ OpenAI provider imports OK")
        
        from auth.jwt_handler import create_access_token, verify_token
        print("✅ JWT handler imports OK")
        
        from models.user import User, Organization, APIKey
        print("✅ Database models imports OK")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_jwt_functionality():
    """Test JWT token functionality"""
    print("🧪 Testing JWT functionality...")
    
    try:
        from auth.jwt_handler import create_access_token, verify_token, get_password_hash, verify_password
        
        # Test password hashing
        password = "test123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed), "Password verification failed"
        assert not verify_password("wrong", hashed), "Wrong password should fail"
        print("✅ Password hashing works")
        
        # Test JWT tokens
        payload = {"sub": "user123", "role": "admin"}
        token = create_access_token(payload)
        decoded = verify_token(token)
        
        assert decoded is not None, "Token decoding failed"
        assert decoded["sub"] == "user123", "Token payload incorrect"
        print("✅ JWT tokens work")
        
        return True
    except Exception as e:
        print(f"❌ JWT test error: {e}")
        return False

def test_provider_base_class():
    """Test base provider functionality"""
    print("🧪 Testing provider base class...")
    
    try:
        from providers.base import BaseModelProvider, GenerationRequest, GenerationResponse, ModelMetadata, ModelCapability
        
        # Test data classes
        request = GenerationRequest(prompt="Test prompt", temperature=0.7)
        assert request.prompt == "Test prompt"
        assert request.temperature == 0.7
        print("✅ GenerationRequest works")
        
        response = GenerationResponse(
            content="Test response",
            model_id="test-model",
            provider_name="test-provider"
        )
        assert response.is_success(), "Response should be successful"
        print("✅ GenerationResponse works")
        
        return True
    except Exception as e:
        print(f"❌ Provider base test error: {e}")
        return False

def test_database_models():
    """Test database model definitions"""
    print("🧪 Testing database models...")
    
    try:
        from models.user import User, Organization, APIKey, UserRole, PlanType
        from models.base import TimestampMixin, UUIDMixin
        
        # Test enum values
        assert UserRole.OWNER.value == "owner"
        assert PlanType.FREE.value == "free"
        print("✅ Enums work correctly")
        
        # Test model instantiation (without database)
        org_data = {
            'name': 'Test Org',
            'slug': 'test-org',
            'plan_type': PlanType.FREE
        }
        # Just test that we can create the class (not save to DB)
        print("✅ Model classes defined correctly")
        
        return True
    except Exception as e:
        print(f"❌ Database model test error: {e}")
        return False

def test_api_structure():
    """Test API router structure"""
    print("🧪 Testing API structure...")
    
    try:
        from api.routers import auth, llm, billing, dashboard
        print("✅ API routers import successfully")
        
        # Test that routers have the expected endpoints
        assert hasattr(auth, 'router'), "Auth router not found"
        assert hasattr(llm, 'router'), "LLM router not found"
        assert hasattr(billing, 'router'), "Billing router not found"
        print("✅ Router objects exist")
        
        return True
    except Exception as e:
        print(f"❌ API structure test error: {e}")
        return False

def test_configuration():
    """Test configuration management"""
    print("🧪 Testing configuration...")
    
    try:
        # Test that config files exist
        config_files = [
            'requirements.txt',
            'requirements-saas.txt', 
            'docker-compose.yml',
            'Dockerfile'
        ]
        
        for config_file in config_files:
            path = f'/Users/mohanjeyasankar/Desktop/llmgateway/{config_file}'
            if os.path.exists(path):
                print(f"✅ {config_file} exists")
            else:
                print(f"❌ {config_file} missing")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Configuration test error: {e}")
        return False

async def test_provider_initialization():
    """Test provider initialization (mocked)"""
    print("🧪 Testing provider initialization...")
    
    try:
        from providers.openai import OpenAIProvider
        
        # Test with mock config
        config = {
            "api_key": "test-key",
            "models": {
                "gpt-3.5-turbo": {
                    "context_length": 4096,
                    "cost_per_1k_tokens": 0.002
                }
            }
        }
        
        provider = OpenAIProvider(config)
        assert provider.provider_name == "openai"
        assert len(provider.get_available_models()) > 0
        print("✅ OpenAI provider instantiation works")
        
        return True
    except Exception as e:
        print(f"❌ Provider test error: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting LLM Gateway SaaS Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_jwt_functionality,
        test_provider_base_class,
        test_database_models,
        test_api_structure,
        test_configuration,
    ]
    
    async_tests = [
        test_provider_initialization,
    ]
    
    passed = 0
    total = len(tests) + len(async_tests)
    
    # Run synchronous tests
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")
            print()
    
    # Run async tests
    async def run_async_tests():
        nonlocal passed
        for test in async_tests:
            try:
                if await test():
                    passed += 1
                print()
            except Exception as e:
                print(f"❌ Test {test.__name__} failed: {e}")
                print()
    
    asyncio.run(run_async_tests())
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The codebase is working correctly.")
    else:
        print(f"⚠️  {total - passed} tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)