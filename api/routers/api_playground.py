from fastapi import APIRouter, Query, Body, HTTPException
from typing import Dict, Any
from developer_experience.api_playground import APIPlaygroundEngine, CodeGenerator, RequestBuilder, CodeLanguage

router = APIRouter(tags=["playground"])

# Use a simple API spec for testing
api_spec = {
    "paths": {
        "/api/v1/generate": {
            "post": {
                "summary": "Generate text",
                "description": "Generate text using the model bridge"
            },
            "get": {
                "summary": "Generate text",
                "description": "Generate text using the model bridge"
            }
        },
        "/api/v1/chat": {
            "post": {
                "summary": "Chat completion",
                "description": "Generate chat completion"
            },
            "get": {
                "summary": "Chat completion",
                "description": "Generate chat completion"
            }
        }
    }
}

playground_engine = APIPlaygroundEngine(base_url="http://localhost:8000", api_spec=api_spec)
code_generator = CodeGenerator()
request_builder = RequestBuilder(api_spec)

@router.post("/execute-request")
async def execute_request(request: Dict[str, Any] = Body(...)) -> Dict[str, Any]:
    """Execute an API request via the playground."""
    try:
        req_obj = request_builder.create_request(**request)
        response = await playground_engine.execute_request(req_obj)
        return response.__dict__
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing request: {str(e)}")

@router.get("/code-sample")
def get_code_sample(endpoint: str = Query(...), method: str = Query(...), language: str = Query(...)) -> str:
    """Generate code sample for an endpoint and method in a given language."""
    try:
        template = request_builder.get_request_template(endpoint, method)
        # Extract method from template to avoid conflict
        template_method = template.pop("method", method)
        template_endpoint = template.pop("endpoint", endpoint)
        req_obj = request_builder.create_request(template_endpoint, template_method, **template)
        lang_enum = CodeLanguage[language.upper()]
        return code_generator.generate_code(req_obj, lang_enum)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating code sample: {str(e)}")

@router.get("/endpoints")
def list_endpoints():
    """List all available API endpoints."""
    try:
        return list(request_builder.api_spec.get('paths', {}).keys())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing endpoints: {str(e)}")

@router.get("/request-template")
def get_request_template(endpoint: str = Query(...), method: str = Query(...)) -> Dict[str, Any]:
    """Get a request template for an endpoint and method."""
    try:
        return request_builder.get_request_template(endpoint, method)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting request template: {str(e)}") 