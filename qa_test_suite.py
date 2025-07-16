"""
QA Test Suite for Model Bridge SaaS - Production Readiness Check
Tests all enterprise features and frontend integration
"""
import os
import sys
import json
import subprocess
import importlib.util
from pathlib import Path

class QATestSuite:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.errors = []
        self.warnings = []
        self.passed_tests = []
        
    def log_error(self, test_name, error):
        self.errors.append(f"❌ {test_name}: {error}")
        print(f"❌ {test_name}: {error}")
        
    def log_warning(self, test_name, warning):
        self.warnings.append(f"⚠️  {test_name}: {warning}")
        print(f"⚠️  {test_name}: {warning}")
        
    def log_pass(self, test_name):
        self.passed_tests.append(f"✅ {test_name}")
        print(f"✅ {test_name}")

    def test_python_imports(self):
        """Test if all Python modules can be imported"""
        print("\n🔍 Testing Python module imports...")
        
        modules_to_test = [
            ("api.main", "Main FastAPI app"),
            ("models.user", "User models"),
            ("models.rbac", "RBAC models"),
            ("auth.jwt_handler", "JWT handler"),
            ("auth.dependencies", "Auth dependencies"),
            ("auth.rbac_middleware", "RBAC middleware"),
            ("auth.sso", "SSO authentication"),
            ("api.routers.dashboard", "Dashboard router"),
            ("api.routers.rbac", "RBAC router"),
            ("api.routers.workflow", "Workflow router"),
            ("api.routers.ab_testing", "A/B testing router"),
            ("api.routers.sso", "SSO router"),
            ("database.database", "Database config"),
            ("model_bridge", "Model bridge core"),
        ]
        
        for module_name, description in modules_to_test:
            try:
                spec = importlib.util.find_spec(module_name)
                if spec is None:
                    self.log_error(f"Import {description}", f"Module {module_name} not found")
                else:
                    self.log_pass(f"Import {description}")
            except Exception as e:
                self.log_error(f"Import {description}", str(e))

    def test_file_structure(self):
        """Test if all required files exist"""
        print("\n🔍 Testing file structure...")
        
        required_files = [
            # Backend files
            ("api/main.py", "Main FastAPI application"),
            ("api/routers/auth.py", "Authentication router"),
            ("api/routers/dashboard.py", "Dashboard router"),
            ("api/routers/rbac.py", "RBAC router"),
            ("api/routers/workflow.py", "Workflow router"),
            ("api/routers/ab_testing.py", "A/B testing router"),
            ("api/routers/sso.py", "SSO router"),
            ("models/user.py", "User models"),
            ("models/rbac.py", "RBAC models"),
            ("auth/jwt_handler.py", "JWT handler"),
            ("auth/dependencies.py", "Auth dependencies"),
            ("auth/rbac_middleware.py", "RBAC middleware"),
            ("auth/sso.py", "SSO authentication"),
            ("database/database.py", "Database configuration"),
            ("model_bridge.py", "Model bridge core"),
            
            # Frontend files
            ("web/src/App.js", "Main React app"),
            ("web/src/components/Navigation.js", "Navigation component"),
            ("web/src/pages/Dashboard.js", "Dashboard page"),
            ("web/src/pages/RBAC.js", "RBAC management page"),
            ("web/src/pages/WorkflowBuilder.js", "Workflow builder page"),
            ("web/src/pages/ABTesting.js", "A/B testing page"),
            ("web/src/pages/APIPlayground.js", "API playground page"),
            ("web/src/contexts/AuthContext.js", "Auth context"),
            ("web/src/services/api.js", "API service"),
            
            # Configuration files
            ("requirements-saas.txt", "Python dependencies"),
            ("web/package.json", "Frontend dependencies"),
            ("alembic.ini", "Database migration config"),
            ("models_config.yaml", "Model configuration"),
        ]
        
        for file_path, description in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.log_pass(f"File exists: {description}")
            else:
                self.log_error(f"Missing file: {description}", f"File not found: {file_path}")

    def test_database_models(self):
        """Test database model definitions"""
        print("\n🔍 Testing database models...")
        
        try:
            # Test user models
            from models.user import User, Organization, APIKey, UsageRecord
            self.log_pass("User models defined correctly")
            
            # Test RBAC models
            from models.rbac import Role, Permission, UserRole, AuditLog, CostCenter, Workflow, ABTest
            self.log_pass("RBAC models defined correctly")
            
            # Check if models have required attributes
            required_user_attrs = ['id', 'email', 'full_name', 'organization_id']
            for attr in required_user_attrs:
                if hasattr(User, attr):
                    self.log_pass(f"User model has {attr} attribute")
                else:
                    self.log_error("User model validation", f"Missing attribute: {attr}")
                    
            # Check RBAC model attributes
            required_role_attrs = ['id', 'name', 'permissions', 'organization_id']
            for attr in required_role_attrs:
                if hasattr(Role, attr):
                    self.log_pass(f"Role model has {attr} attribute")
                else:
                    self.log_error("Role model validation", f"Missing attribute: {attr}")
                    
        except ImportError as e:
            self.log_error("Database models import", str(e))

    def test_api_routers(self):
        """Test API router definitions"""
        print("\n🔍 Testing API routers...")
        
        try:
            from api.routers import auth, dashboard, rbac, workflow, ab_testing, sso
            self.log_pass("All API routers imported successfully")
            
            # Check if routers have required endpoints
            dashboard_routes = [route.path for route in dashboard.router.routes]
            expected_dashboard_routes = ['/analytics', '/executive', '/cost-centers']
            
            for route in expected_dashboard_routes:
                if any(route in path for path in dashboard_routes):
                    self.log_pass(f"Dashboard router has {route} endpoint")
                else:
                    self.log_error("Dashboard router validation", f"Missing endpoint: {route}")
                    
        except ImportError as e:
            self.log_error("API routers import", str(e))

    def test_frontend_components(self):
        """Test frontend React components"""
        print("\n🔍 Testing frontend components...")
        
        # Check React component files
        react_components = [
            ("web/src/App.js", "Main App component"),
            ("web/src/components/Navigation.js", "Navigation component"),
            ("web/src/pages/Dashboard.js", "Dashboard page"),
            ("web/src/pages/RBAC.js", "RBAC page"),
            ("web/src/pages/WorkflowBuilder.js", "Workflow builder"),
            ("web/src/pages/ABTesting.js", "A/B testing page"),
            ("web/src/pages/APIPlayground.js", "API playground"),
        ]
        
        for file_path, description in react_components:
            full_path = self.project_root / file_path
            if full_path.exists():
                # Check if it's a valid React component
                try:
                    with open(full_path, 'r') as f:
                        content = f.read()
                        if 'import React' in content and 'export default' in content:
                            self.log_pass(f"Valid React component: {description}")
                        else:
                            self.log_warning(f"React component structure: {description}", 
                                           "Missing standard React imports/exports")
                except Exception as e:
                    self.log_error(f"Reading React component: {description}", str(e))
            else:
                self.log_error(f"Missing React component: {description}", f"File not found: {file_path}")

    def test_package_dependencies(self):
        """Test if required packages are installed"""
        print("\n🔍 Testing package dependencies...")
        
        # Python dependencies
        python_deps = [
            'fastapi', 'uvicorn', 'sqlalchemy', 'alembic', 'pydantic',
            'passlib', 'jose', 'redis', 'prometheus_client', 'httpx'
        ]
        
        for dep in python_deps:
            try:
                __import__(dep)
                self.log_pass(f"Python dependency available: {dep}")
            except ImportError:
                self.log_error(f"Missing Python dependency: {dep}", "Package not installed")

    def test_configuration_files(self):
        """Test configuration files"""
        print("\n🔍 Testing configuration files...")
        
        # Check models_config.yaml
        models_config_path = self.project_root / "models_config.yaml"
        if models_config_path.exists():
            try:
                import yaml
                with open(models_config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    if 'models' in config and 'providers' in config:
                        self.log_pass("Models configuration file valid")
                    else:
                        self.log_error("Models config validation", "Missing required sections")
            except Exception as e:
                self.log_error("Models config parsing", str(e))
        else:
            self.log_error("Models configuration", "models_config.yaml not found")
        
        # Check package.json
        package_json_path = self.project_root / "web" / "package.json"
        if package_json_path.exists():
            try:
                with open(package_json_path, 'r') as f:
                    package_config = json.load(f)
                    required_deps = ['react', 'react-dom', 'react-router-dom']
                    for dep in required_deps:
                        if dep in package_config.get('dependencies', {}):
                            self.log_pass(f"Frontend dependency available: {dep}")
                        else:
                            self.log_error(f"Missing frontend dependency: {dep}", "Not in package.json")
            except Exception as e:
                self.log_error("Package.json parsing", str(e))

    def test_enterprise_features_integration(self):
        """Test enterprise features integration"""
        print("\n🔍 Testing enterprise features integration...")
        
        # Check if enterprise routers are properly included in main app
        try:
            from api.main import app
            
            # Get all routes
            routes = [route.path for route in app.routes]
            
            expected_enterprise_routes = [
                '/api/rbac',
                '/api/workflow', 
                '/api/ab-testing',
                '/api/sso'
            ]
            
            for route_prefix in expected_enterprise_routes:
                if any(route_prefix in route for route in routes):
                    self.log_pass(f"Enterprise route integrated: {route_prefix}")
                else:
                    self.log_error("Enterprise integration", f"Missing route prefix: {route_prefix}")
                    
        except Exception as e:
            self.log_error("Enterprise features integration", str(e))

    def test_security_configurations(self):
        """Test security configurations"""
        print("\n🔍 Testing security configurations...")
        
        try:
            from auth.jwt_handler import SECRET_KEY, ALGORITHM
            
            if SECRET_KEY and SECRET_KEY != "your-secret-key-change-in-production":
                self.log_pass("JWT secret key configured")
            else:
                self.log_warning("JWT secret key", "Using default secret key - change in production")
                
            if ALGORITHM == "HS256":
                self.log_pass("JWT algorithm configured correctly")
            else:
                self.log_warning("JWT algorithm", f"Using {ALGORITHM} - verify this is intended")
                
        except Exception as e:
            self.log_error("Security configuration", str(e))

    def run_syntax_check(self):
        """Run Python syntax check on all Python files"""
        print("\n🔍 Running Python syntax checks...")
        
        python_files = list(self.project_root.rglob("*.py"))
        syntax_errors = 0
        
        for py_file in python_files:
            if 'venv' in str(py_file) or '__pycache__' in str(py_file):
                continue
                
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                compile(content, py_file, 'exec')
                
            except SyntaxError as e:
                syntax_errors += 1
                self.log_error(f"Syntax error in {py_file.name}", f"Line {e.lineno}: {e.msg}")
            except Exception as e:
                self.log_warning(f"Could not check {py_file.name}", str(e))
        
        if syntax_errors == 0:
            self.log_pass("All Python files have valid syntax")

    def run_all_tests(self):
        """Run all QA tests"""
        print("🚀 Starting comprehensive QA testing for Model Bridge SaaS...\n")
        
        # Run all test suites
        self.test_file_structure()
        self.test_python_imports()
        self.test_database_models()
        self.test_api_routers()
        self.test_frontend_components()
        self.test_package_dependencies()
        self.test_configuration_files()
        self.test_enterprise_features_integration()
        self.test_security_configurations()
        self.run_syntax_check()
        
        # Generate summary report
        self.generate_summary_report()

    def generate_summary_report(self):
        """Generate final QA report"""
        print("\n" + "="*80)
        print("🎯 QA TEST SUMMARY REPORT")
        print("="*80)
        
        print(f"\n✅ PASSED TESTS: {len(self.passed_tests)}")
        for test in self.passed_tests[-10:]:  # Show last 10 passed tests
            print(f"   {test}")
        if len(self.passed_tests) > 10:
            print(f"   ... and {len(self.passed_tests) - 10} more")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"   {warning}")
        
        if self.errors:
            print(f"\n❌ ERRORS: {len(self.errors)}")
            for error in self.errors:
                print(f"   {error}")
        
        # Production readiness assessment
        total_tests = len(self.passed_tests) + len(self.warnings) + len(self.errors)
        pass_rate = (len(self.passed_tests) / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n📊 OVERALL HEALTH: {pass_rate:.1f}% ({len(self.passed_tests)}/{total_tests} tests passed)")
        
        if len(self.errors) == 0 and len(self.warnings) <= 3:
            print("\n🎉 PRODUCTION READY: Application appears ready for production deployment!")
            print("✅ All critical components are present and properly integrated")
        elif len(self.errors) <= 2:
            print("\n⚠️  MOSTLY READY: Application is mostly ready with minor issues to address")
            print("🔧 Fix the errors above before production deployment")
        else:
            print("\n🚨 NOT READY: Application has significant issues that need to be addressed")
            print("🛠️  Please fix the errors above before considering production deployment")
        
        print("\n" + "="*80)


if __name__ == "__main__":
    qa_suite = QATestSuite()
    qa_suite.run_all_tests()