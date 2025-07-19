from fastapi import APIRouter, Query, HTTPException
from typing import Dict, Any
from developer_experience.documentation_system import DocumentationGenerator

router = APIRouter(tags=["documentation"])

# Use a simple API spec for testing
api_spec = {
    "paths": {
        "/api/v1/generate": {
            "post": {
                "summary": "Generate text",
                "description": "Generate text using the model bridge"
            }
        },
        "/api/v1/chat": {
            "post": {
                "summary": "Chat completion",
                "description": "Generate chat completion"
            }
        }
    }
}

doc_gen = DocumentationGenerator(api_spec)

@router.get("/endpoints")
def get_all_docs() -> Dict[str, Any]:
    """Get documentation for all endpoints."""
    try:
        return doc_gen.generate_all_docs()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating docs: {str(e)}")

@router.get("/endpoint")
def get_endpoint_docs(endpoint: str = Query(..., description="Endpoint path")) -> Dict[str, Any]:
    """Get documentation for a specific endpoint."""
    try:
        return doc_gen.generate_endpoint_docs(endpoint)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating endpoint docs: {str(e)}")

@router.get("/code-example")
def get_code_example(endpoint: str = Query(...), language: str = Query(...)) -> str:
    """Get code example for an endpoint in a specific language."""
    try:
        return doc_gen.get_code_examples(endpoint, language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating code example: {str(e)}")

@router.get("/enterprise-guides")
def get_enterprise_guides():
    """Get enterprise use case guides."""
    try:
        return doc_gen.get_enterprise_guides()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading enterprise guides: {str(e)}")

@router.get("/best-practices")
def get_best_practices():
    """Get best practices documentation."""
    try:
        return doc_gen.get_best_practices()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading best practices: {str(e)}") 