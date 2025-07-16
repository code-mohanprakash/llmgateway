"""
Model Bridge Python SDK - Enterprise Edition
"""
import asyncio
import aiohttp
import json
import time
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


class ModelProvider(Enum):
    """Supported model providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    COHERE = "cohere"
    GROQ = "groq"
    DEEPSEEK = "deepseek"
    MISTRAL = "mistral"
    PERPLEXITY = "perplexity"
    TOGETHER = "together"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"


class WorkflowStatus(Enum):
    """Workflow execution status"""
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ModelResponse:
    """Model response data"""
    content: str
    model: str
    provider: str
    usage: Dict[str, Any]
    metadata: Dict[str, Any]


@dataclass
class WorkflowExecution:
    """Workflow execution data"""
    id: str
    workflow_id: str
    status: WorkflowStatus
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    started_at: datetime
    completed_at: Optional[datetime]
    execution_time_ms: Optional[int]
    total_cost: Optional[float]


class ModelBridgeClient:
    """Enterprise Model Bridge Python SDK Client"""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8000",
        organization_id: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.organization_id = organization_id
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session = None
        self._cache = {}
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic"""
        if not self.session:
            raise RuntimeError("Client not initialized. Use async context manager.")
        
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                async with self.session.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 401:
                        raise AuthenticationError("Invalid API key")
                    elif response.status == 403:
                        raise PermissionError("Insufficient permissions")
                    elif response.status == 429:
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(self.retry_delay * (2 ** attempt))
                            continue
                        raise RateLimitError("Rate limit exceeded")
                    else:
                        error_data = await response.json()
                        raise APIError(f"API error: {error_data.get('detail', 'Unknown error')}")
                        
            except aiohttp.ClientError as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    continue
                raise ConnectionError(f"Connection error: {str(e)}")
        
        raise APIError("Max retries exceeded")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        provider: Optional[ModelProvider] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> ModelResponse:
        """Send chat completion request"""
        data = {
            "messages": messages,
            "model": model,
            "temperature": temperature,
            "stream": stream,
            **kwargs
        }
        
        if provider:
            data["provider"] = provider.value
        
        if max_tokens:
            data["max_tokens"] = max_tokens
        
        if self.organization_id:
            data["organization_id"] = self.organization_id
        
        response = await self._make_request("POST", "/api/llm/chat", data=data)
        
        return ModelResponse(
            content=response["choices"][0]["message"]["content"],
            model=response["model"],
            provider=response.get("provider", "unknown"),
            usage=response.get("usage", {}),
            metadata=response.get("metadata", {})
        )
    
    async def completion(
        self,
        prompt: str,
        model: str = "gpt-3.5-turbo",
        provider: Optional[ModelProvider] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> ModelResponse:
        """Send completion request"""
        data = {
            "prompt": prompt,
            "model": model,
            "temperature": temperature,
            **kwargs
        }
        
        if provider:
            data["provider"] = provider.value
        
        if max_tokens:
            data["max_tokens"] = max_tokens
        
        if self.organization_id:
            data["organization_id"] = self.organization_id
        
        response = await self._make_request("POST", "/api/llm/completion", data=data)
        
        return ModelResponse(
            content=response["choices"][0]["text"],
            model=response["model"],
            provider=response.get("provider", "unknown"),
            usage=response.get("usage", {}),
            metadata=response.get("metadata", {})
        )
    
    async def get_models(self) -> List[Dict[str, Any]]:
        """Get available models"""
        response = await self._make_request("GET", "/api/llm/models")
        return response.get("models", [])
    
    async def get_providers(self) -> List[Dict[str, Any]]:
        """Get available providers"""
        response = await self._make_request("GET", "/api/llm/providers")
        return response.get("providers", [])
    
    async def create_workflow(
        self,
        name: str,
        definition: Dict[str, Any],
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new workflow"""
        data = {
            "name": name,
            "definition": definition
        }
        
        if description:
            data["description"] = description
        
        if self.organization_id:
            data["organization_id"] = self.organization_id
        
        response = await self._make_request("POST", "/api/workflows", data=data)
        return response
    
    async def execute_workflow(
        self,
        workflow_id: str,
        input_data: Dict[str, Any]
    ) -> WorkflowExecution:
        """Execute a workflow"""
        data = {
            "workflow_id": workflow_id,
            "input_data": input_data
        }
        
        if self.organization_id:
            data["organization_id"] = self.organization_id
        
        response = await self._make_request("POST", "/api/workflows/execute", data=data)
        
        return WorkflowExecution(
            id=response["id"],
            workflow_id=response["workflow_id"],
            status=WorkflowStatus(response["status"]),
            input_data=response["input_data"],
            output_data=response.get("output_data", {}),
            started_at=datetime.fromisoformat(response["started_at"]),
            completed_at=datetime.fromisoformat(response["completed_at"]) if response.get("completed_at") else None,
            execution_time_ms=response.get("execution_time_ms"),
            total_cost=response.get("total_cost")
        )
    
    async def get_workflow_execution(self, execution_id: str) -> WorkflowExecution:
        """Get workflow execution status"""
        response = await self._make_request("GET", f"/api/workflows/executions/{execution_id}")
        
        return WorkflowExecution(
            id=response["id"],
            workflow_id=response["workflow_id"],
            status=WorkflowStatus(response["status"]),
            input_data=response["input_data"],
            output_data=response.get("output_data", {}),
            started_at=datetime.fromisoformat(response["started_at"]),
            completed_at=datetime.fromisoformat(response["completed_at"]) if response.get("completed_at") else None,
            execution_time_ms=response.get("execution_time_ms"),
            total_cost=response.get("total_cost")
        )
    
    async def get_usage_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        group_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get usage analytics"""
        params = {}
        
        if start_date:
            params["start_date"] = start_date.isoformat()
        
        if end_date:
            params["end_date"] = end_date.isoformat()
        
        if group_by:
            params["group_by"] = group_by
        
        if self.organization_id:
            params["organization_id"] = self.organization_id
        
        response = await self._make_request("GET", "/api/analytics/usage", params=params)
        return response
    
    async def get_cost_analytics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        cost_center: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get cost analytics"""
        params = {}
        
        if start_date:
            params["start_date"] = start_date.isoformat()
        
        if end_date:
            params["end_date"] = end_date.isoformat()
        
        if cost_center:
            params["cost_center"] = cost_center
        
        if self.organization_id:
            params["organization_id"] = self.organization_id
        
        response = await self._make_request("GET", "/api/analytics/costs", params=params)
        return response
    
    async def get_audit_logs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get audit logs"""
        params = {"limit": limit}
        
        if start_date:
            params["start_date"] = start_date.isoformat()
        
        if end_date:
            params["end_date"] = end_date.isoformat()
        
        if user_id:
            params["user_id"] = user_id
        
        if action:
            params["action"] = action
        
        if self.organization_id:
            params["organization_id"] = self.organization_id
        
        response = await self._make_request("GET", "/api/audit/logs", params=params)
        return response.get("logs", [])
    
    async def create_role(
        self,
        name: str,
        permissions: List[str],
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new role"""
        data = {
            "name": name,
            "permissions": permissions
        }
        
        if description:
            data["description"] = description
        
        if self.organization_id:
            data["organization_id"] = self.organization_id
        
        response = await self._make_request("POST", "/api/rbac/roles", data=data)
        return response
    
    async def assign_role(
        self,
        user_id: str,
        role_id: str
    ) -> Dict[str, Any]:
        """Assign role to user"""
        data = {
            "user_id": user_id,
            "role_id": role_id
        }
        
        if self.organization_id:
            data["organization_id"] = self.organization_id
        
        response = await self._make_request("POST", "/api/rbac/assignments", data=data)
        return response
    
    async def get_roles(self) -> List[Dict[str, Any]]:
        """Get all roles"""
        params = {}
        
        if self.organization_id:
            params["organization_id"] = self.organization_id
        
        response = await self._make_request("GET", "/api/rbac/roles", params=params)
        return response.get("roles", [])
    
    async def get_permissions(self) -> List[Dict[str, Any]]:
        """Get all permissions"""
        response = await self._make_request("GET", "/api/rbac/permissions")
        return response.get("permissions", [])


# Exception classes
class ModelBridgeError(Exception):
    """Base exception for Model Bridge SDK"""
    pass


class AuthenticationError(ModelBridgeError):
    """Authentication error"""
    pass


class PermissionError(ModelBridgeError):
    """Permission error"""
    pass


class RateLimitError(ModelBridgeError):
    """Rate limit error"""
    pass


class APIError(ModelBridgeError):
    """API error"""
    pass


class ConnectionError(ModelBridgeError):
    """Connection error"""
    pass


# Convenience functions for synchronous usage
def create_client(
    api_key: str,
    base_url: str = "http://localhost:8000",
    organization_id: Optional[str] = None,
    timeout: int = 30,
    max_retries: int = 3,
    retry_delay: float = 1.0
) -> ModelBridgeClient:
    """Create a Model Bridge client"""
    return ModelBridgeClient(
        api_key=api_key,
        base_url=base_url,
        organization_id=organization_id,
        timeout=timeout,
        max_retries=max_retries,
        retry_delay=retry_delay
    )


async def chat_completion(
    api_key: str,
    messages: List[Dict[str, str]],
    model: str = "gpt-3.5-turbo",
    provider: Optional[ModelProvider] = None,
    **kwargs
) -> ModelResponse:
    """Quick chat completion"""
    async with create_client(api_key) as client:
        return await client.chat_completion(messages, model, provider, **kwargs)


async def completion(
    api_key: str,
    prompt: str,
    model: str = "gpt-3.5-turbo",
    provider: Optional[ModelProvider] = None,
    **kwargs
) -> ModelResponse:
    """Quick completion"""
    async with create_client(api_key) as client:
        return await client.completion(prompt, model, provider, **kwargs) 