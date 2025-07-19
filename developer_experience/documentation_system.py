"""
Comprehensive API Documentation System - Phase 4.4

This module provides:
- Interactive API explorer
- Code examples for all endpoints
- Enterprise use case guides
- Integration tutorials
- Best practices documentation
"""

from typing import Dict, List, Any, Optional

class DocumentationGenerator:
    """
    Generates comprehensive API documentation including:
    - Endpoint details
    - Request/response schemas
    - Code examples
    - Authentication guides
    - Enterprise use cases
    """
    def __init__(self, api_spec: Dict[str, Any]):
        self.api_spec = api_spec

    def generate_endpoint_docs(self, endpoint: str) -> Dict[str, Any]:
        """Return documentation for a specific endpoint."""
        paths = self.api_spec.get('paths', {})
        for path, methods in paths.items():
            if path == endpoint:
                return {path: methods}
        return {}

    def generate_all_docs(self) -> Dict[str, Any]:
        """Return documentation for all endpoints."""
        return self.api_spec.get('paths', {})

    def get_code_examples(self, endpoint: str, language: str) -> str:
        """Return code examples for an endpoint in the specified language."""
        try:
            from .api_playground import CodeGenerator, CodeLanguage, PlaygroundRequest, APIEndpoint, HTTPMethod
            from datetime import datetime
            
            # Create a sample request for code generation
            sample_endpoint = APIEndpoint(
                path=endpoint,
                method=HTTPMethod.GET,
                name=f"Sample {endpoint}",
                description=f"Sample request for {endpoint}",
                parameters={},
                auth_required=True
            )
            
            sample_request = PlaygroundRequest(
                id="sample",
                endpoint=sample_endpoint,
                headers={"Authorization": "Bearer YOUR_API_KEY"},
                query_params={},
                body=None,
                auth_config={"api_key": "YOUR_API_KEY"},
                timestamp=datetime.utcnow()
            )
            
            code_generator = CodeGenerator()
            lang_enum = CodeLanguage[language.upper()]
            return code_generator.generate_code(sample_request, lang_enum)
        except Exception as e:
            # Fallback to basic example
            example = f"# Example for {endpoint} in {language}\n"
            example += f"import requests\n\n"
            example += f"url = 'http://localhost:8000{endpoint}'\n"
            example += f"headers = {{'Authorization': 'Bearer YOUR_API_KEY'}}\n"
            example += f"response = requests.get(url, headers=headers)\n"
            example += f"print(response.json())\n"
            return example

    def get_enterprise_guides(self) -> List[Dict[str, Any]]:
        """Return enterprise use case guides."""
        return [
            {"title": "Multi-Tenant Integration", "content": "How to use the API in a multi-tenant environment."},
            {"title": "Enterprise Authentication", "content": "Guide to SSO and API key management."}
        ]

    def get_best_practices(self) -> List[str]:
        """Return best practices documentation."""
        return [
            "Use API keys securely and rotate regularly.",
            "Implement proper error handling for all API calls.",
            "Leverage async SDKs for high-throughput workloads.",
            "Follow rate limits and monitor usage."
        ]

class APIExplorer:
    """
    Interactive API explorer for browsing and testing endpoints.
    """
    def __init__(self, api_spec: Dict[str, Any]):
        self.api_spec = api_spec

    def list_endpoints(self) -> List[str]:
        """List all available API endpoints."""
        return list(self.api_spec.get('paths', {}).keys())

    def get_endpoint_details(self, endpoint: str) -> Dict[str, Any]:
        """Get details for a specific endpoint."""
        paths = self.api_spec.get('paths', {})
        if endpoint in paths:
            return {
                "path": endpoint,
                "methods": paths[endpoint],
                "description": f"API endpoint: {endpoint}"
            }
        return {}

class TutorialManager:
    """
    Manages integration tutorials and code walkthroughs.
    """
    def __init__(self):
        self.tutorials = []

    def add_tutorial(self, title: str, content: str):
        """Add a new tutorial."""
        self.tutorials.append({"title": title, "content": content})

    def get_tutorials(self) -> List[Dict[str, str]]:
        """Return all tutorials."""
        return self.tutorials 