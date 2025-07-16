"""
API Integration Test for Model Bridge SaaS
Tests all enterprise API endpoints and functionality
"""
import asyncio
import httpx
import os
import sys
import json
from typing import Dict, Any

class APIIntegrationTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.auth_headers = {}
        self.test_results = []
        
    async def setup(self):
        """Setup test environment"""
        self.session = httpx.AsyncClient(base_url=self.base_url)
        
    async def cleanup(self):
        """Cleanup test environment"""
        if self.session:
            await self.session.aclose()
    
    def log_result(self, test_name: str, success: bool, details: str = ""):
        """Log test result"""
        status = "✅" if success else "❌"
        result = f"{status} {test_name}"
        if details:
            result += f": {details}"
        print(result)
        self.test_results.append((test_name, success, details))
    
    async def test_health_endpoints(self):
        """Test basic health endpoints"""
        print("\n🔍 Testing Health Endpoints...")
        
        try:
            # Test main health endpoint
            response = await self.session.get("/health")
            success = response.status_code == 200 and "healthy" in response.text
            self.log_result("Health endpoint", success, f"Status: {response.status_code}")
            
            # Test API health endpoint
            response = await self.session.get("/api/health")
            success = response.status_code == 200 and "healthy" in response.text
            self.log_result("API health endpoint", success, f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_result("Health endpoints", False, str(e))
    
    async def test_metrics_endpoint(self):
        """Test Prometheus metrics endpoint"""
        print("\n🔍 Testing Metrics Endpoint...")
        
        try:
            response = await self.session.get("/metrics")
            success = response.status_code == 200
            self.log_result("Metrics endpoint", success, f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_result("Metrics endpoint", False, str(e))
    
    async def test_api_documentation(self):
        """Test API documentation endpoints"""
        print("\n🔍 Testing API Documentation...")
        
        try:
            # Test OpenAPI docs
            response = await self.session.get("/api/docs")
            success = response.status_code == 200
            self.log_result("OpenAPI docs", success, f"Status: {response.status_code}")
            
            # Test ReDoc
            response = await self.session.get("/api/redoc")
            success = response.status_code == 200
            self.log_result("ReDoc documentation", success, f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_result("API documentation", False, str(e))
    
    async def test_enterprise_endpoints_structure(self):
        """Test that enterprise endpoints exist (without auth)"""
        print("\n🔍 Testing Enterprise Endpoint Structure...")
        
        enterprise_endpoints = [
            "/api/rbac/roles",
            "/api/rbac/permissions", 
            "/api/workflow/workflows",
            "/api/ab-testing/tests",
            "/api/sso/providers",
            "/api/dashboard/analytics",
            "/api/dashboard/executive"
        ]
        
        for endpoint in enterprise_endpoints:
            try:
                response = await self.session.get(endpoint)
                # We expect 401 (unauthorized) for protected endpoints
                success = response.status_code in [401, 403, 422]  # Auth required responses
                details = f"Status: {response.status_code} (auth required)"
                self.log_result(f"Endpoint exists: {endpoint}", success, details)
                
            except Exception as e:
                self.log_result(f"Endpoint test: {endpoint}", False, str(e))
    
    async def test_model_endpoints(self):
        """Test LLM model endpoints"""
        print("\n🔍 Testing Model Endpoints...")
        
        try:
            # Test models list (should work without auth for discovery)
            response = await self.session.get("/api/v1/models")
            success = response.status_code in [200, 401, 403]
            self.log_result("Models list endpoint", success, f"Status: {response.status_code}")
            
            # Test providers list
            response = await self.session.get("/api/v1/providers")
            success = response.status_code in [200, 401, 403]
            self.log_result("Providers list endpoint", success, f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_result("Model endpoints", False, str(e))
    
    async def test_frontend_routing(self):
        """Test frontend route handling"""
        print("\n🔍 Testing Frontend Routing...")
        
        frontend_routes = [
            "/",
            "/dashboard", 
            "/rbac",
            "/workflows",
            "/ab-testing",
            "/analytics"
        ]
        
        for route in frontend_routes:
            try:
                response = await self.session.get(route)
                # Frontend routes should return 200 (serving React app)
                success = response.status_code == 200
                self.log_result(f"Frontend route: {route}", success, f"Status: {response.status_code}")
                
            except Exception as e:
                self.log_result(f"Frontend route: {route}", False, str(e))
    
    async def test_cors_headers(self):
        """Test CORS configuration"""
        print("\n🔍 Testing CORS Configuration...")
        
        try:
            # Test OPTIONS request for CORS
            response = await self.session.options("/api/health")
            has_cors = "access-control-allow-origin" in [h.lower() for h in response.headers.keys()]
            self.log_result("CORS headers present", has_cors, "CORS middleware configured")
            
        except Exception as e:
            self.log_result("CORS configuration", False, str(e))
    
    async def test_request_id_middleware(self):
        """Test request ID middleware"""
        print("\n🔍 Testing Request ID Middleware...")
        
        try:
            response = await self.session.get("/api/health")
            has_request_id = "x-request-id" in [h.lower() for h in response.headers.keys()]
            has_process_time = "x-process-time" in [h.lower() for h in response.headers.keys()]
            
            self.log_result("Request ID header", has_request_id, "Middleware working")
            self.log_result("Process time header", has_process_time, "Timing middleware working")
            
        except Exception as e:
            self.log_result("Request middleware", False, str(e))
    
    async def test_error_handling(self):
        """Test error handling"""
        print("\n🔍 Testing Error Handling...")
        
        try:
            # Test 404 for non-existent API route
            response = await self.session.get("/api/nonexistent")
            success = response.status_code == 404
            self.log_result("404 handling", success, f"Status: {response.status_code}")
            
            # Test method not allowed
            response = await self.session.delete("/api/health")  # Should not be allowed
            success = response.status_code == 405
            self.log_result("405 handling", success, f"Status: {response.status_code}")
            
        except Exception as e:
            self.log_result("Error handling", False, str(e))
    
    async def run_all_tests(self):
        """Run all API integration tests"""
        print("🚀 Starting API Integration Testing...")
        
        await self.setup()
        
        try:
            await self.test_health_endpoints()
            await self.test_metrics_endpoint()
            await self.test_api_documentation()
            await self.test_enterprise_endpoints_structure()
            await self.test_model_endpoints()
            await self.test_frontend_routing()
            await self.test_cors_headers()
            await self.test_request_id_middleware()
            await self.test_error_handling()
            
        finally:
            await self.cleanup()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        print("\n" + "="*80)
        print("🎯 API INTEGRATION TEST SUMMARY")
        print("="*80)
        
        passed = sum(1 for _, success, _ in self.test_results if success)
        total = len(self.test_results)
        
        print(f"\n📊 RESULTS: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED: API is fully functional!")
        elif passed >= total * 0.9:
            print("\n✅ MOSTLY FUNCTIONAL: Minor issues to address")
        else:
            print("\n⚠️  NEEDS ATTENTION: Several API issues found")
        
        # Show failed tests
        failed = [(name, details) for name, success, details in self.test_results if not success]
        if failed:
            print(f"\n❌ FAILED TESTS ({len(failed)}):")
            for name, details in failed:
                print(f"   • {name}: {details}")
        
        print("\n" + "="*80)

async def main():
    # Check if server should be started
    if len(sys.argv) > 1 and sys.argv[1] == "--start-server":
        print("🚀 Starting development server...")
        import subprocess
        import time
        
        # Start the server in background
        server_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "api.main:app", 
            "--host", "0.0.0.0", "--port", "8000"
        ])
        
        # Wait for server to start
        time.sleep(3)
        
        try:
            # Run tests
            tester = APIIntegrationTester()
            await tester.run_all_tests()
        finally:
            # Stop server
            server_process.terminate()
            server_process.wait()
    else:
        print("📡 Testing against running server at http://localhost:8000")
        print("   (Use --start-server to automatically start the server)")
        
        tester = APIIntegrationTester()
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())