"""
Frontend Component Testing Script
Tests React components for syntax and structure
"""
import os
import re
from pathlib import Path

class FrontendTester:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.web_src = self.project_root / "web" / "src"
        self.issues = []
        self.passes = []
        
    def test_react_component(self, file_path, component_name):
        """Test a React component file"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check basic React structure
            checks = [
                ("React import", "import React" in content),
                ("Component export", "export default" in content),
                ("JSX return", "return (" in content or "return <" in content),
                ("Component function", f"const {component_name}" in content or f"function {component_name}" in content),
            ]
            
            passed = 0
            for check_name, check_result in checks:
                if check_result:
                    passed += 1
                    self.passes.append(f"✅ {component_name}: {check_name}")
                else:
                    self.issues.append(f"❌ {component_name}: Missing {check_name}")
            
            # Check for common issues
            if "class " in content and "extends Component" not in content:
                self.issues.append(f"⚠️  {component_name}: Uses 'class' but not React.Component")
            
            if "useState" in content and "import { useState" not in content and "import React, { useState" not in content:
                self.issues.append(f"⚠️  {component_name}: Uses useState but not imported")
                
            if "useEffect" in content and "useEffect" not in content.split("import")[1].split("\n")[0]:
                self.issues.append(f"⚠️  {component_name}: Uses useEffect but not imported")
            
            return passed >= 3  # At least 3 out of 4 basic checks should pass
            
        except Exception as e:
            self.issues.append(f"❌ {component_name}: Error reading file - {str(e)}")
            return False
    
    def test_api_service(self):
        """Test API service configuration"""
        api_file = self.web_src / "services" / "api.js"
        try:
            with open(api_file, 'r') as f:
                content = f.read()
            
            if "baseURL" in content or "base_url" in content:
                self.passes.append("✅ API Service: Base URL configured")
            else:
                self.issues.append("❌ API Service: Missing base URL configuration")
                
            if "Authorization" in content or "Bearer" in content:
                self.passes.append("✅ API Service: Auth headers configured")
            else:
                self.issues.append("❌ API Service: Missing auth configuration")
                
            if "axios" in content:
                self.passes.append("✅ API Service: Uses axios for HTTP")
            else:
                self.issues.append("⚠️  API Service: Not using axios")
                
        except Exception as e:
            self.issues.append(f"❌ API Service: Error reading file - {str(e)}")
    
    def test_routing(self):
        """Test React Router configuration"""
        app_file = self.web_src / "App.js"
        try:
            with open(app_file, 'r') as f:
                content = f.read()
            
            if "BrowserRouter" in content or "Router" in content:
                self.passes.append("✅ Routing: Router configured")
            else:
                self.issues.append("❌ Routing: Missing router configuration")
                
            if "Route" in content:
                self.passes.append("✅ Routing: Routes defined")
            else:
                self.issues.append("❌ Routing: No routes found")
                
            # Check for enterprise routes
            enterprise_routes = ["rbac", "workflow", "ab-testing", "analytics"]
            for route in enterprise_routes:
                if route in content.lower():
                    self.passes.append(f"✅ Routing: {route.upper()} route exists")
                else:
                    self.issues.append(f"⚠️  Routing: {route.upper()} route missing")
                    
        except Exception as e:
            self.issues.append(f"❌ Routing: Error reading App.js - {str(e)}")
    
    def test_package_json(self):
        """Test package.json configuration"""
        package_file = self.project_root / "web" / "package.json"
        try:
            import json
            with open(package_file, 'r') as f:
                package_data = json.load(f)
            
            # Check dependencies
            deps = package_data.get('dependencies', {})
            required_deps = [
                'react', 'react-dom', 'react-router-dom', 'axios'
            ]
            
            for dep in required_deps:
                if dep in deps:
                    self.passes.append(f"✅ Dependencies: {dep} installed")
                else:
                    self.issues.append(f"❌ Dependencies: {dep} missing")
            
            # Check scripts
            scripts = package_data.get('scripts', {})
            required_scripts = ['start', 'build']
            
            for script in required_scripts:
                if script in scripts:
                    self.passes.append(f"✅ Scripts: {script} script exists")
                else:
                    self.issues.append(f"❌ Scripts: {script} script missing")
                    
        except Exception as e:
            self.issues.append(f"❌ Package.json: Error reading file - {str(e)}")
    
    def run_all_tests(self):
        """Run all frontend tests"""
        print("🚀 Testing Frontend Components and Integration...\n")
        
        # Test individual components
        components_to_test = [
            ("App.js", "App"),
            ("components/Navigation.js", "Navigation"),
            ("pages/Dashboard.js", "Dashboard"),
            ("pages/RBAC.js", "RBAC"),
            ("pages/WorkflowBuilder.js", "WorkflowBuilder"),
            ("pages/ABTesting.js", "ABTesting"),
            ("pages/APIPlayground.js", "APIPlayground"),
            ("contexts/AuthContext.js", "AuthProvider"),
        ]
        
        print("🔍 Testing React Components...")
        for file_path, component_name in components_to_test:
            full_path = self.web_src / file_path
            if full_path.exists():
                self.test_react_component(full_path, component_name)
            else:
                self.issues.append(f"❌ {component_name}: File not found - {file_path}")
        
        print("\n🔍 Testing API Service...")
        self.test_api_service()
        
        print("\n🔍 Testing Routing Configuration...")
        self.test_routing()
        
        print("\n🔍 Testing Package Configuration...")
        self.test_package_json()
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "="*80)
        print("🎯 FRONTEND TESTING REPORT")
        print("="*80)
        
        if self.passes:
            print(f"\n✅ PASSED TESTS: {len(self.passes)}")
            for test in self.passes[-10:]:  # Show last 10
                print(f"   {test}")
            if len(self.passes) > 10:
                print(f"   ... and {len(self.passes) - 10} more")
        
        if self.issues:
            print(f"\n❌ ISSUES FOUND: {len(self.issues)}")
            for issue in self.issues:
                print(f"   {issue}")
        
        # Assessment
        total_tests = len(self.passes) + len(self.issues)
        if total_tests > 0:
            success_rate = (len(self.passes) / total_tests) * 100
            print(f"\n📊 SUCCESS RATE: {success_rate:.1f}% ({len(self.passes)}/{total_tests})")
            
            if len(self.issues) == 0:
                print("\n🎉 FRONTEND READY: All components are properly structured!")
            elif len(self.issues) <= 3:
                print("\n⚠️  MOSTLY READY: Minor issues to address")
            else:
                print("\n🚨 NEEDS WORK: Significant frontend issues found")
        
        print("\n" + "="*80)

if __name__ == "__main__":
    tester = FrontendTester()
    tester.run_all_tests()