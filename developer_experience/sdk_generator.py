"""
SDK Generator - Phase 4.2 & 4.3: Enterprise SDK Generation

This module generates production-ready SDKs for multiple languages:
- Enterprise Python SDK with async support
- Enterprise JavaScript/TypeScript SDK
- Comprehensive error handling and retry logic
- Built-in authentication and monitoring
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class SDKLanguage(Enum):
    """Supported SDK languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"


@dataclass
class SDKConfig:
    """SDK generation configuration"""
    language: SDKLanguage
    package_name: str
    version: str
    author: str
    description: str
    base_url: str
    auth_methods: List[str]
    include_async: bool = True
    include_retry: bool = True
    include_caching: bool = True
    include_monitoring: bool = True


class PythonSDKGenerator:
    """
    Enterprise Python SDK generator with comprehensive features.
    
    Generates a production-ready Python SDK with:
    - Async/await support
    - Automatic retry logic
    - Built-in caching
    - Error handling
    - Authentication
    - Performance monitoring
    """
    
    def __init__(self, config: SDKConfig, api_spec: Dict[str, Any]):
        """
        Initialize the Python SDK generator.
        
        Args:
            config: SDK configuration
            api_spec: OpenAPI specification
        """
        self.config = config
        self.api_spec = api_spec
    
    def generate_sdk(self, output_dir: str) -> Dict[str, str]:
        """
        Generate complete Python SDK.
        
        Args:
            output_dir: Output directory for SDK files
            
        Returns:
            Dict[str, str]: Generated files mapping
        """
        
        files = {}
        
        # Generate core client
        files["client.py"] = self._generate_client()
        
        # Generate authentication module
        files["auth.py"] = self._generate_auth_module()
        
        # Generate models
        files["models.py"] = self._generate_models()
        
        # Generate exceptions
        files["exceptions.py"] = self._generate_exceptions()
        
        # Generate utilities
        files["utils.py"] = self._generate_utils()
        
        # Generate async client
        if self.config.include_async:
            files["async_client.py"] = self._generate_async_client()
        
        # Generate package files
        files["__init__.py"] = self._generate_init_file()
        files["setup.py"] = self._generate_setup_file()
        files["requirements.txt"] = self._generate_requirements()
        files["README.md"] = self._generate_readme()
        
        return files
    
    def _generate_client(self) -> str:
        """Generate main synchronous client."""
        
        code = '"""LLM Gateway Python SDK - Synchronous Client"""\n\n'
        
        # Imports
        code += "import json\n"
        code += "import time\n"
        code += "import requests\n"
        code += "from typing import Dict, List, Any, Optional, Union\n"
        code += "from urllib.parse import urljoin\n\n"
        code += "from .auth import AuthenticationManager\n"
        code += "from .models import ChatMessage, ChatResponse, ModelInfo\n"
        code += "from .exceptions import LLMGatewayError, AuthenticationError, RateLimitError\n"
        code += "from .utils import RetryManager, CacheManager, PerformanceMonitor\n\n\n"
        
        # Main client class
        code += "class LLMGatewayClient:\n"
        code += '    """Enterprise LLM Gateway Python SDK Client.\n'
        code += '    \n'
        code += '    Provides comprehensive access to the LLM Gateway API with:\n'
        code += '    - Multiple authentication methods\n'
        code += '    - Automatic retry logic\n'
        code += '    - Built-in caching\n'
        code += '    - Performance monitoring\n'
        code += '    - Enterprise error handling\n'
        code += '    """\n\n'
        
        # Constructor
        code += "    def __init__(\n"
        code += "        self,\n"
        code += "        api_key: str,\n"
        code += f'        base_url: str = "{self.config.base_url}",\n'
        code += "        organization_id: Optional[str] = None,\n"
        code += "        timeout: int = 30,\n"
        code += "        max_retries: int = 3,\n"
        code += "        enable_caching: bool = True,\n"
        code += "        enable_monitoring: bool = True\n"
        code += "    ):\n"
        code += '        """Initialize the LLM Gateway client.\n'
        code += '        \n'
        code += '        Args:\n'
        code += '            api_key: Your API key\n'
        code += '            base_url: Base URL for the API\n'
        code += '            organization_id: Optional organization ID\n'
        code += '            timeout: Request timeout in seconds\n'
        code += '            max_retries: Maximum number of retries\n'
        code += '            enable_caching: Enable response caching\n'
        code += '            enable_monitoring: Enable performance monitoring\n'
        code += '        """\n'
        code += "        self.base_url = base_url.rstrip('/')\n"
        code += "        self.timeout = timeout\n"
        code += "        \n"
        code += "        # Initialize components\n"
        code += "        self.auth = AuthenticationManager(api_key, organization_id)\n"
        code += "        self.retry_manager = RetryManager(max_retries)\n"
        code += "        \n"
        code += "        self.cache_manager = None\n"
        code += "        if enable_caching:\n"
        code += "            self.cache_manager = CacheManager()\n"
        code += "        \n"
        code += "        self.performance_monitor = None\n"
        code += "        if enable_monitoring:\n"
        code += "            self.performance_monitor = PerformanceMonitor()\n"
        code += "        \n"
        code += "        # Initialize session\n"
        code += "        self.session = requests.Session()\n"
        code += "        self.session.headers.update(self.auth.get_headers())\n\n"
        
        # Chat completion method
        code += "    def chat_completion(\n"
        code += "        self,\n"
        code += "        messages: List[ChatMessage],\n"
        code += "        model: str,\n"
        code += "        provider: Optional[str] = None,\n"
        code += "        temperature: float = 0.7,\n"
        code += "        max_tokens: Optional[int] = None,\n"
        code += "        stream: bool = False,\n"
        code += "        **kwargs\n"
        code += "    ) -> ChatResponse:\n"
        code += '        """Generate chat completion.\n'
        code += '        \n'
        code += '        Args:\n'
        code += '            messages: List of chat messages\n'
        code += '            model: Model identifier\n'
        code += '            provider: Optional provider name\n'
        code += '            temperature: Sampling temperature (0-1)\n'
        code += '            max_tokens: Maximum tokens to generate\n'
        code += '            stream: Enable streaming response\n'
        code += '            **kwargs: Additional parameters\n'
        code += '        \n'
        code += '        Returns:\n'
        code += '            ChatResponse: Chat completion response\n'
        code += '        \n'
        code += '        Raises:\n'
        code += '            LLMGatewayError: API error occurred\n'
        code += '            AuthenticationError: Authentication failed\n'
        code += '            RateLimitError: Rate limit exceeded\n'
        code += '        """\n'
        code += "        \n"
        code += "        # Prepare request data\n"
        code += "        data = {\n"
        code += "            'messages': [msg.to_dict() for msg in messages],\n"
        code += "            'model': model,\n"
        code += "            'temperature': temperature,\n"
        code += "            'stream': stream\n"
        code += "        }\n"
        code += "        \n"
        code += "        if provider:\n"
        code += "            data['provider'] = provider\n"
        code += "        if max_tokens:\n"
        code += "            data['max_tokens'] = max_tokens\n"
        code += "        \n"
        code += "        # Add additional parameters\n"
        code += "        data.update(kwargs)\n"
        code += "        \n"
        code += "        # Check cache first\n"
        code += "        cache_key = None\n"
        code += "        if self.cache_manager and temperature == 0 and not stream:\n"
        code += "            cache_key = self.cache_manager.generate_key('chat_completion', data)\n"
        code += "            cached_response = self.cache_manager.get(cache_key)\n"
        code += "            if cached_response:\n"
        code += "                return ChatResponse.from_dict(cached_response)\n"
        code += "        \n"
        code += "        # Make request with retry logic\n"
        code += "        response_data = self._make_request(\n"
        code += "            'POST', '/v1/chat/completions', json=data\n"
        code += "        )\n"
        code += "        \n"
        code += "        # Create response object\n"
        code += "        chat_response = ChatResponse.from_dict(response_data)\n"
        code += "        \n"
        code += "        # Cache deterministic responses\n"
        code += "        if cache_key and self.cache_manager:\n"
        code += "            self.cache_manager.set(cache_key, response_data)\n"
        code += "        \n"
        code += "        return chat_response\n\n"
        
        # List models method
        code += "    def list_models(\n"
        code += "        self,\n"
        code += "        provider: Optional[str] = None,\n"
        code += "        limit: Optional[int] = None\n"
        code += "    ) -> List[ModelInfo]:\n"
        code += '        """List available models.\n'
        code += '        \n'
        code += '        Args:\n'
        code += '            provider: Filter by provider\n'
        code += '            limit: Maximum number of models to return\n'
        code += '        \n'
        code += '        Returns:\n'
        code += '            List[ModelInfo]: Available models\n'
        code += '        """\n'
        code += "        \n"
        code += "        params = {}\n"
        code += "        if provider:\n"
        code += "            params['provider'] = provider\n"
        code += "        if limit:\n"
        code += "            params['limit'] = limit\n"
        code += "        \n"
        code += "        response_data = self._make_request('GET', '/v1/models', params=params)\n"
        code += "        \n"
        code += "        models = []\n"
        code += "        for model_data in response_data.get('models', []):\n"
        code += "            models.append(ModelInfo.from_dict(model_data))\n"
        code += "        \n"
        code += "        return models\n\n"
        
        # Internal request method
        code += "    def _make_request(\n"
        code += "        self,\n"
        code += "        method: str,\n"
        code += "        endpoint: str,\n"
        code += "        **kwargs\n"
        code += "    ) -> Dict[str, Any]:\n"
        code += '        """Make HTTP request with retry logic and error handling."""\n'
        code += "        \n"
        code += "        url = urljoin(self.base_url, endpoint)\n"
        code += "        \n"
        code += "        # Start performance monitoring\n"
        code += "        if self.performance_monitor:\n"
        code += "            self.performance_monitor.start_request(method, endpoint)\n"
        code += "        \n"
        code += "        try:\n"
        code += "            # Execute request with retry logic\n"
        code += "            response = self.retry_manager.execute_with_retry(\n"
        code += "                self._execute_request, method, url, **kwargs\n"
        code += "            )\n"
        code += "            \n"
        code += "            # Record success metrics\n"
        code += "            if self.performance_monitor:\n"
        code += "                self.performance_monitor.record_success(\n"
        code += "                    response.status_code, response.elapsed.total_seconds()\n"
        code += "                )\n"
        code += "            \n"
        code += "            return response.json()\n"
        code += "            \n"
        code += "        except Exception as e:\n"
        code += "            # Record error metrics\n"
        code += "            if self.performance_monitor:\n"
        code += "                self.performance_monitor.record_error(str(e))\n"
        code += "            raise\n\n"
        
        code += "    def _execute_request(self, method: str, url: str, **kwargs) -> requests.Response:\n"
        code += '        """Execute single HTTP request."""\n'
        code += "        \n"
        code += "        response = self.session.request(\n"
        code += "            method=method,\n"
        code += "            url=url,\n"
        code += "            timeout=self.timeout,\n"
        code += "            **kwargs\n"
        code += "        )\n"
        code += "        \n"
        code += "        # Handle HTTP errors\n"
        code += "        if response.status_code == 401:\n"
        code += "            raise AuthenticationError('Invalid API key or authentication failed')\n"
        code += "        elif response.status_code == 429:\n"
        code += "            raise RateLimitError('Rate limit exceeded')\n"
        code += "        elif not response.ok:\n"
        code += "            try:\n"
        code += "                error_data = response.json()\n"
        code += "                error_message = error_data.get('message', 'Unknown error')\n"
        code += "            except:\n"
        code += "                error_message = f'HTTP {response.status_code}: {response.text}'\n"
        code += "            \n"
        code += "            raise LLMGatewayError(error_message, response.status_code)\n"
        code += "        \n"
        code += "        return response\n\n"
        
        # Performance metrics
        code += "    def get_performance_metrics(self) -> Dict[str, Any]:\n"
        code += '        """Get performance metrics."""\n'
        code += "        if self.performance_monitor:\n"
        code += "            return self.performance_monitor.get_metrics()\n"
        code += "        return {}\n\n"
        
        # Context manager support
        code += "    def __enter__(self):\n"
        code += "        return self\n\n"
        code += "    def __exit__(self, exc_type, exc_val, exc_tb):\n"
        code += "        self.session.close()\n"
        
        return code
    
    def _generate_async_client(self) -> str:
        """Generate asynchronous client."""
        
        code = '"""LLM Gateway Python SDK - Asynchronous Client"""\n\n'
        
        # Imports
        code += "import asyncio\n"
        code += "import json\n"
        code += "import time\n"
        code += "import aiohttp\n"
        code += "from typing import Dict, List, Any, Optional, Union, AsyncIterator\n"
        code += "from urllib.parse import urljoin\n\n"
        code += "from .auth import AuthenticationManager\n"
        code += "from .models import ChatMessage, ChatResponse, ModelInfo\n"
        code += "from .exceptions import LLMGatewayError, AuthenticationError, RateLimitError\n"
        code += "from .utils import AsyncRetryManager, AsyncCacheManager, AsyncPerformanceMonitor\n\n\n"
        
        # Async client class
        code += "class AsyncLLMGatewayClient:\n"
        code += '    """Enterprise LLM Gateway Python SDK Async Client.\n'
        code += '    \n'
        code += '    Provides comprehensive async access to the LLM Gateway API with:\n'
        code += '    - Multiple authentication methods\n'
        code += '    - Automatic retry logic\n'
        code += '    - Built-in caching\n'
        code += '    - Performance monitoring\n'
        code += '    - Streaming support\n'
        code += '    """\n\n'
        
        # Constructor
        code += "    def __init__(\n"
        code += "        self,\n"
        code += "        api_key: str,\n"
        code += f'        base_url: str = "{self.config.base_url}",\n'
        code += "        organization_id: Optional[str] = None,\n"
        code += "        timeout: int = 30,\n"
        code += "        max_retries: int = 3,\n"
        code += "        enable_caching: bool = True,\n"
        code += "        enable_monitoring: bool = True\n"
        code += "    ):\n"
        code += "        self.base_url = base_url.rstrip('/')\n"
        code += "        self.timeout = aiohttp.ClientTimeout(total=timeout)\n"
        code += "        \n"
        code += "        # Initialize components\n"
        code += "        self.auth = AuthenticationManager(api_key, organization_id)\n"
        code += "        self.retry_manager = AsyncRetryManager(max_retries)\n"
        code += "        \n"
        code += "        self.cache_manager = None\n"
        code += "        if enable_caching:\n"
        code += "            self.cache_manager = AsyncCacheManager()\n"
        code += "        \n"
        code += "        self.performance_monitor = None\n"
        code += "        if enable_monitoring:\n"
        code += "            self.performance_monitor = AsyncPerformanceMonitor()\n"
        code += "        \n"
        code += "        self._session: Optional[aiohttp.ClientSession] = None\n\n"
        
        # Session management
        code += "    async def __aenter__(self):\n"
        code += "        await self._ensure_session()\n"
        code += "        return self\n\n"
        code += "    async def __aexit__(self, exc_type, exc_val, exc_tb):\n"
        code += "        await self.close()\n\n"
        code += "    async def _ensure_session(self):\n"
        code += "        if self._session is None or self._session.closed:\n"
        code += "            self._session = aiohttp.ClientSession(\n"
        code += "                timeout=self.timeout,\n"
        code += "                headers=self.auth.get_headers()\n"
        code += "            )\n\n"
        code += "    async def close(self):\n"
        code += "        if self._session and not self._session.closed:\n"
        code += "            await self._session.close()\n\n"
        
        # Async chat completion
        code += "    async def chat_completion(\n"
        code += "        self,\n"
        code += "        messages: List[ChatMessage],\n"
        code += "        model: str,\n"
        code += "        provider: Optional[str] = None,\n"
        code += "        temperature: float = 0.7,\n"
        code += "        max_tokens: Optional[int] = None,\n"
        code += "        stream: bool = False,\n"
        code += "        **kwargs\n"
        code += "    ) -> Union[ChatResponse, AsyncIterator[ChatResponse]]:\n"
        code += '        """Generate chat completion asynchronously.\n'
        code += '        \n'
        code += '        Args:\n'
        code += '            messages: List of chat messages\n'
        code += '            model: Model identifier\n'
        code += '            provider: Optional provider name\n'
        code += '            temperature: Sampling temperature (0-1)\n'
        code += '            max_tokens: Maximum tokens to generate\n'
        code += '            stream: Enable streaming response\n'
        code += '            **kwargs: Additional parameters\n'
        code += '        \n'
        code += '        Returns:\n'
        code += '            ChatResponse or AsyncIterator[ChatResponse]: Response or stream\n'
        code += '        """\n'
        code += "        \n"
        code += "        data = {\n"
        code += "            'messages': [msg.to_dict() for msg in messages],\n"
        code += "            'model': model,\n"
        code += "            'temperature': temperature,\n"
        code += "            'stream': stream\n"
        code += "        }\n"
        code += "        \n"
        code += "        if provider:\n"
        code += "            data['provider'] = provider\n"
        code += "        if max_tokens:\n"
        code += "            data['max_tokens'] = max_tokens\n"
        code += "        \n"
        code += "        data.update(kwargs)\n"
        code += "        \n"
        code += "        if stream:\n"
        code += "            return self._stream_chat_completion(data)\n"
        code += "        \n"
        code += "        # Check cache first\n"
        code += "        cache_key = None\n"
        code += "        if self.cache_manager and temperature == 0:\n"
        code += "            cache_key = await self.cache_manager.generate_key('chat_completion', data)\n"
        code += "            cached_response = await self.cache_manager.get(cache_key)\n"
        code += "            if cached_response:\n"
        code += "                return ChatResponse.from_dict(cached_response)\n"
        code += "        \n"
        code += "        # Make request\n"
        code += "        response_data = await self._make_request(\n"
        code += "            'POST', '/v1/chat/completions', json=data\n"
        code += "        )\n"
        code += "        \n"
        code += "        chat_response = ChatResponse.from_dict(response_data)\n"
        code += "        \n"
        code += "        # Cache response\n"
        code += "        if cache_key and self.cache_manager:\n"
        code += "            await self.cache_manager.set(cache_key, response_data)\n"
        code += "        \n"
        code += "        return chat_response\n\n"
        
        # Streaming method
        code += "    async def _stream_chat_completion(self, data: Dict[str, Any]) -> AsyncIterator[ChatResponse]:\n"
        code += '        """Stream chat completion responses."""\n'
        code += "        await self._ensure_session()\n"
        code += "        \n"
        code += "        url = urljoin(self.base_url, '/v1/chat/completions')\n"
        code += "        \n"
        code += "        async with self._session.post(url, json=data) as response:\n"
        code += "            if not response.ok:\n"
        code += "                await self._handle_error_response(response)\n"
        code += "            \n"
        code += "            async for line in response.content:\n"
        code += "                if line.startswith(b'data: '):\n"
        code += "                    try:\n"
        code += "                        chunk_data = json.loads(line[6:].decode('utf-8'))\n"
        code += "                        if chunk_data.get('choices'):\n"
        code += "                            yield ChatResponse.from_dict(chunk_data)\n"
        code += "                    except json.JSONDecodeError:\n"
        code += "                        continue\n\n"
        
        # Internal async request method
        code += "    async def _make_request(\n"
        code += "        self,\n"
        code += "        method: str,\n"
        code += "        endpoint: str,\n"
        code += "        **kwargs\n"
        code += "    ) -> Dict[str, Any]:\n"
        code += '        """Make async HTTP request with retry logic."""\n'
        code += "        await self._ensure_session()\n"
        code += "        \n"
        code += "        url = urljoin(self.base_url, endpoint)\n"
        code += "        \n"
        code += "        if self.performance_monitor:\n"
        code += "            await self.performance_monitor.start_request(method, endpoint)\n"
        code += "        \n"
        code += "        try:\n"
        code += "            response = await self.retry_manager.execute_with_retry(\n"
        code += "                self._execute_request, method, url, **kwargs\n"
        code += "            )\n"
        code += "            \n"
        code += "            if self.performance_monitor:\n"
        code += "                await self.performance_monitor.record_success(\n"
        code += "                    response.status, response.headers.get('x-response-time', 0)\n"
        code += "                )\n"
        code += "            \n"
        code += "            return await response.json()\n"
        code += "            \n"
        code += "        except Exception as e:\n"
        code += "            if self.performance_monitor:\n"
        code += "                await self.performance_monitor.record_error(str(e))\n"
        code += "            raise\n\n"
        
        code += "    async def _execute_request(self, method: str, url: str, **kwargs) -> aiohttp.ClientResponse:\n"
        code += '        """Execute single async HTTP request."""\n'
        code += "        \n"
        code += "        response = await self._session.request(method, url, **kwargs)\n"
        code += "        \n"
        code += "        if not response.ok:\n"
        code += "            await self._handle_error_response(response)\n"
        code += "        \n"
        code += "        return response\n\n"
        
        code += "    async def _handle_error_response(self, response: aiohttp.ClientResponse):\n"
        code += '        """Handle HTTP error responses."""\n'
        code += "        if response.status == 401:\n"
        code += "            raise AuthenticationError('Invalid API key or authentication failed')\n"
        code += "        elif response.status == 429:\n"
        code += "            raise RateLimitError('Rate limit exceeded')\n"
        code += "        else:\n"
        code += "            try:\n"
        code += "                error_data = await response.json()\n"
        code += "                error_message = error_data.get('message', 'Unknown error')\n"
        code += "            except:\n"
        code += "                error_message = f'HTTP {response.status}: {await response.text()}'\n"
        code += "            \n"
        code += "            raise LLMGatewayError(error_message, response.status)\n"
        
        return code
    
    def _generate_models(self) -> str:
        """Generate data models."""
        
        code = '"""LLM Gateway Python SDK - Data Models"""\n\n'
        
        code += "from dataclasses import dataclass, asdict\n"
        code += "from typing import Dict, List, Any, Optional\n"
        code += "from datetime import datetime\n\n\n"
        
        # Chat Message model
        code += "@dataclass\n"
        code += "class ChatMessage:\n"
        code += '    """Represents a chat message."""\n'
        code += "    role: str  # 'user', 'assistant', 'system'\n"
        code += "    content: str\n"
        code += "    name: Optional[str] = None\n\n"
        code += "    def to_dict(self) -> Dict[str, Any]:\n"
        code += "        return asdict(self)\n\n"
        code += "    @classmethod\n"
        code += "    def from_dict(cls, data: Dict[str, Any]) -> 'ChatMessage':\n"
        code += "        return cls(**data)\n\n\n"
        
        # Chat Response model
        code += "@dataclass\n"
        code += "class ChatResponse:\n"
        code += '    """Represents a chat completion response."""\n'
        code += "    id: str\n"
        code += "    choices: List[Dict[str, Any]]\n"
        code += "    usage: Dict[str, int]\n"
        code += "    model: str\n"
        code += "    provider: str\n"
        code += "    created: int\n"
        code += "    cost: Optional[float] = None\n"
        code += "    response_time_ms: Optional[int] = None\n\n"
        code += "    @property\n"
        code += "    def message(self) -> Optional[ChatMessage]:\n"
        code += '        """Get the first choice message."""\n'
        code += "        if self.choices:\n"
        code += "            choice = self.choices[0]\n"
        code += "            if 'message' in choice:\n"
        code += "                return ChatMessage.from_dict(choice['message'])\n"
        code += "        return None\n\n"
        code += "    @property\n"
        code += "    def content(self) -> Optional[str]:\n"
        code += '        """Get the message content."""\n'
        code += "        message = self.message\n"
        code += "        return message.content if message else None\n\n"
        code += "    def to_dict(self) -> Dict[str, Any]:\n"
        code += "        return asdict(self)\n\n"
        code += "    @classmethod\n"
        code += "    def from_dict(cls, data: Dict[str, Any]) -> 'ChatResponse':\n"
        code += "        return cls(**data)\n\n\n"
        
        # Model Info model
        code += "@dataclass\n"
        code += "class ModelInfo:\n"
        code += '    """Represents model information."""\n'
        code += "    id: str\n"
        code += "    name: str\n"
        code += "    provider: str\n"
        code += "    description: Optional[str] = None\n"
        code += "    context_length: Optional[int] = None\n"
        code += "    input_cost_per_token: Optional[float] = None\n"
        code += "    output_cost_per_token: Optional[float] = None\n"
        code += "    capabilities: Optional[List[str]] = None\n\n"
        code += "    def to_dict(self) -> Dict[str, Any]:\n"
        code += "        return asdict(self)\n\n"
        code += "    @classmethod\n"
        code += "    def from_dict(cls, data: Dict[str, Any]) -> 'ModelInfo':\n"
        code += "        return cls(**data)\n"
        
        return code
    
    def _generate_exceptions(self) -> str:
        """Generate exception classes."""
        
        code = '"""LLM Gateway Python SDK - Exceptions"""\n\n\n'
        
        code += "class LLMGatewayError(Exception):\n"
        code += '    """Base exception for LLM Gateway errors."""\n'
        code += "    \n"
        code += "    def __init__(self, message: str, status_code: int = None):\n"
        code += "        super().__init__(message)\n"
        code += "        self.message = message\n"
        code += "        self.status_code = status_code\n\n\n"
        
        code += "class AuthenticationError(LLMGatewayError):\n"
        code += '    """Authentication failed."""\n'
        code += "    pass\n\n\n"
        
        code += "class RateLimitError(LLMGatewayError):\n"
        code += '    """Rate limit exceeded."""\n'
        code += "    pass\n\n\n"
        
        code += "class ValidationError(LLMGatewayError):\n"
        code += '    """Request validation failed."""\n'
        code += "    pass\n\n\n"
        
        code += "class ModelNotFoundError(LLMGatewayError):\n"
        code += '    """Requested model not found."""\n'
        code += "    pass\n\n\n"
        
        code += "class ProviderError(LLMGatewayError):\n"
        code += '    """Provider-specific error."""\n'
        code += "    \n"
        code += "    def __init__(self, message: str, provider: str, status_code: int = None):\n"
        code += "        super().__init__(message, status_code)\n"
        code += "        self.provider = provider\n"
        
        return code
    
    def _generate_auth_module(self) -> str:
        """Generate authentication module."""
        
        code = '"""LLM Gateway Python SDK - Authentication"""\n\n'
        
        code += "import time\n"
        code += "from typing import Dict, Optional\n\n\n"
        
        code += "class AuthenticationManager:\n"
        code += '    """Manages authentication for API requests."""\n\n'
        
        code += "    def __init__(self, api_key: str, organization_id: Optional[str] = None):\n"
        code += "        self.api_key = api_key\n"
        code += "        self.organization_id = organization_id\n\n"
        
        code += "    def get_headers(self) -> Dict[str, str]:\n"
        code += '        """Get authentication headers."""\n'
        code += "        headers = {\n"
        code += "            'Authorization': f'Bearer {self.api_key}',\n"
        code += "            'Content-Type': 'application/json',\n"
        code += "            'User-Agent': f'llm-gateway-python-sdk/{self._get_version()}'\n"
        code += "        }\n"
        code += "        \n"
        code += "        if self.organization_id:\n"
        code += "            headers['X-Organization-ID'] = self.organization_id\n"
        code += "        \n"
        code += "        return headers\n\n"
        
        code += "    def _get_version(self) -> str:\n"
        code += '        """Get SDK version."""\n'
        code += f"        return '{self.config.version}'\n"
        
        return code
    
    def _generate_utils(self) -> str:
        """Generate utility classes."""
        
        code = '"""LLM Gateway Python SDK - Utilities"""\n\n'
        
        code += "import time\n"
        code += "import hashlib\n"
        code += "import json\n"
        code += "from typing import Dict, Any, Callable, Optional\n"
        code += "from functools import wraps\n\n\n"
        
        # Retry Manager
        code += "class RetryManager:\n"
        code += '    """Manages retry logic for failed requests."""\n\n'
        
        code += "    def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0):\n"
        code += "        self.max_retries = max_retries\n"
        code += "        self.backoff_factor = backoff_factor\n\n"
        
        code += "    def execute_with_retry(self, func: Callable, *args, **kwargs):\n"
        code += '        """Execute function with retry logic."""\n'
        code += "        last_exception = None\n"
        code += "        \n"
        code += "        for attempt in range(self.max_retries + 1):\n"
        code += "            try:\n"
        code += "                return func(*args, **kwargs)\n"
        code += "            except Exception as e:\n"
        code += "                last_exception = e\n"
        code += "                \n"
        code += "                if attempt == self.max_retries:\n"
        code += "                    break\n"
        code += "                \n"
        code += "                # Calculate backoff delay\n"
        code += "                delay = self.backoff_factor ** attempt\n"
        code += "                time.sleep(delay)\n"
        code += "        \n"
        code += "        raise last_exception\n\n\n"
        
        # Cache Manager
        code += "class CacheManager:\n"
        code += '    """Simple in-memory cache for deterministic responses."""\n\n'
        
        code += "    def __init__(self, max_size: int = 1000, ttl: int = 3600):\n"
        code += "        self.max_size = max_size\n"
        code += "        self.ttl = ttl\n"
        code += "        self._cache: Dict[str, Dict[str, Any]] = {}\n\n"
        
        code += "    def generate_key(self, operation: str, data: Dict[str, Any]) -> str:\n"
        code += '        """Generate cache key from operation and data."""\n'
        code += "        cache_data = json.dumps(data, sort_keys=True)\n"
        code += "        return hashlib.md5(f'{operation}:{cache_data}'.encode()).hexdigest()\n\n"
        
        code += "    def get(self, key: str) -> Optional[Dict[str, Any]]:\n"
        code += '        """Get cached value."""\n'
        code += "        if key in self._cache:\n"
        code += "            entry = self._cache[key]\n"
        code += "            if time.time() - entry['timestamp'] < self.ttl:\n"
        code += "                return entry['data']\n"
        code += "            else:\n"
        code += "                del self._cache[key]\n"
        code += "        return None\n\n"
        
        code += "    def set(self, key: str, data: Dict[str, Any]):\n"
        code += '        """Set cached value."""\n'
        code += "        if len(self._cache) >= self.max_size:\n"
        code += "            # Remove oldest entry\n"
        code += "            oldest_key = min(self._cache.keys(), \n"
        code += "                           key=lambda k: self._cache[k]['timestamp'])\n"
        code += "            del self._cache[oldest_key]\n"
        code += "        \n"
        code += "        self._cache[key] = {\n"
        code += "            'data': data,\n"
        code += "            'timestamp': time.time()\n"
        code += "        }\n\n\n"
        
        # Performance Monitor
        code += "class PerformanceMonitor:\n"
        code += '    """Monitors API performance metrics."""\n\n'
        
        code += "    def __init__(self):\n"
        code += "        self.metrics = {\n"
        code += "            'total_requests': 0,\n"
        code += "            'successful_requests': 0,\n"
        code += "            'failed_requests': 0,\n"
        code += "            'total_response_time': 0,\n"
        code += "            'errors': []\n"
        code += "        }\n"
        code += "        self._current_request_start = None\n\n"
        
        code += "    def start_request(self, method: str, endpoint: str):\n"
        code += '        """Start timing a request."""\n'
        code += "        self._current_request_start = time.time()\n"
        code += "        self.metrics['total_requests'] += 1\n\n"
        
        code += "    def record_success(self, status_code: int, response_time: float):\n"
        code += '        """Record successful request."""\n'
        code += "        self.metrics['successful_requests'] += 1\n"
        code += "        self.metrics['total_response_time'] += response_time\n\n"
        
        code += "    def record_error(self, error_message: str):\n"
        code += '        """Record failed request."""\n'
        code += "        self.metrics['failed_requests'] += 1\n"
        code += "        self.metrics['errors'].append({\n"
        code += "            'message': error_message,\n"
        code += "            'timestamp': time.time()\n"
        code += "        })\n\n"
        
        code += "    def get_metrics(self) -> Dict[str, Any]:\n"
        code += '        """Get performance metrics."""\n'
        code += "        total_requests = self.metrics['total_requests']\n"
        code += "        if total_requests > 0:\n"
        code += "            avg_response_time = self.metrics['total_response_time'] / self.metrics['successful_requests'] if self.metrics['successful_requests'] > 0 else 0\n"
        code += "            success_rate = self.metrics['successful_requests'] / total_requests\n"
        code += "        else:\n"
        code += "            avg_response_time = 0\n"
        code += "            success_rate = 0\n"
        code += "        \n"
        code += "        return {\n"
        code += "            'total_requests': total_requests,\n"
        code += "            'success_rate': success_rate,\n"
        code += "            'average_response_time': avg_response_time,\n"
        code += "            'error_count': len(self.metrics['errors'])\n"
        code += "        }\n"
        
        return code
    
    def _generate_init_file(self) -> str:
        """Generate package __init__.py file."""
        
        code = f'"""LLM Gateway Python SDK\n\n'
        code += f'Version: {self.config.version}\n'
        code += f'Author: {self.config.author}\n'
        code += f'Description: {self.config.description}\n'
        code += '"""\n\n'
        
        code += "from .client import LLMGatewayClient\n"
        if self.config.include_async:
            code += "from .async_client import AsyncLLMGatewayClient\n"
        code += "from .models import ChatMessage, ChatResponse, ModelInfo\n"
        code += "from .exceptions import (\n"
        code += "    LLMGatewayError,\n"
        code += "    AuthenticationError,\n"
        code += "    RateLimitError,\n"
        code += "    ValidationError,\n"
        code += "    ModelNotFoundError,\n"
        code += "    ProviderError\n"
        code += ")\n\n"
        
        code += f'__version__ = "{self.config.version}"\n'
        code += f'__author__ = "{self.config.author}"\n\n'
        
        code += "__all__ = [\n"
        code += "    'LLMGatewayClient',\n"
        if self.config.include_async:
            code += "    'AsyncLLMGatewayClient',\n"
        code += "    'ChatMessage',\n"
        code += "    'ChatResponse',\n"
        code += "    'ModelInfo',\n"
        code += "    'LLMGatewayError',\n"
        code += "    'AuthenticationError',\n"
        code += "    'RateLimitError',\n"
        code += "    'ValidationError',\n"
        code += "    'ModelNotFoundError',\n"
        code += "    'ProviderError'\n"
        code += "]\n"
        
        return code
    
    def _generate_setup_file(self) -> str:
        """Generate setup.py file."""
        
        code = "from setuptools import setup, find_packages\n\n"
        code += "with open('README.md', 'r', encoding='utf-8') as fh:\n"
        code += "    long_description = fh.read()\n\n"
        code += "setup(\n"
        code += f"    name='{self.config.package_name}',\n"
        code += f"    version='{self.config.version}',\n"
        code += f"    author='{self.config.author}',\n"
        code += f"    description='{self.config.description}',\n"
        code += "    long_description=long_description,\n"
        code += "    long_description_content_type='text/markdown',\n"
        code += "    packages=find_packages(),\n"
        code += "    classifiers=[\n"
        code += "        'Development Status :: 4 - Beta',\n"
        code += "        'Intended Audience :: Developers',\n"
        code += "        'License :: OSI Approved :: MIT License',\n"
        code += "        'Operating System :: OS Independent',\n"
        code += "        'Programming Language :: Python :: 3',\n"
        code += "        'Programming Language :: Python :: 3.8',\n"
        code += "        'Programming Language :: Python :: 3.9',\n"
        code += "        'Programming Language :: Python :: 3.10',\n"
        code += "        'Programming Language :: Python :: 3.11',\n"
        code += "    ],\n"
        code += "    python_requires='>=3.8',\n"
        code += "    install_requires=[\n"
        code += "        'requests>=2.25.0',\n"
        if self.config.include_async:
            code += "        'aiohttp>=3.8.0',\n"
        code += "    ],\n"
        code += "    extras_require={\n"
        code += "        'dev': [\n"
        code += "            'pytest>=6.0',\n"
        code += "            'pytest-asyncio>=0.18.0',\n"
        code += "            'black>=22.0.0',\n"
        code += "            'isort>=5.0.0',\n"
        code += "            'mypy>=0.910',\n"
        code += "        ]\n"
        code += "    }\n"
        code += ")\n"
        
        return code
    
    def _generate_requirements(self) -> str:
        """Generate requirements.txt file."""
        
        requirements = ["requests>=2.25.0"]
        
        if self.config.include_async:
            requirements.append("aiohttp>=3.8.0")
        
        return "\n".join(requirements) + "\n"
    
    def _generate_readme(self) -> str:
        """Generate README.md file."""
        
        readme = f"# {self.config.package_name}\n\n"
        readme += f"{self.config.description}\n\n"
        readme += "## Installation\n\n"
        readme += f"```bash\npip install {self.config.package_name}\n```\n\n"
        readme += "## Quick Start\n\n"
        readme += "### Synchronous Usage\n\n"
        readme += "```python\n"
        readme += f"from {self.config.package_name} import LLMGatewayClient, ChatMessage\n\n"
        readme += "# Initialize client\n"
        readme += "client = LLMGatewayClient(api_key='your_api_key_here')\n\n"
        readme += "# Create chat message\n"
        readme += "messages = [ChatMessage(role='user', content='Hello, how are you?')]\n\n"
        readme += "# Generate completion\n"
        readme += "response = client.chat_completion(messages=messages, model='gpt-3.5-turbo')\n"
        readme += "print(response.content)\n"
        readme += "```\n\n"
        
        if self.config.include_async:
            readme += "### Asynchronous Usage\n\n"
            readme += "```python\n"
            readme += "import asyncio\n"
            readme += f"from {self.config.package_name} import AsyncLLMGatewayClient, ChatMessage\n\n"
            readme += "async def main():\n"
            readme += "    async with AsyncLLMGatewayClient(api_key='your_api_key_here') as client:\n"
            readme += "        messages = [ChatMessage(role='user', content='Hello, how are you?')]\n"
            readme += "        response = await client.chat_completion(messages=messages, model='gpt-3.5-turbo')\n"
            readme += "        print(response.content)\n\n"
            readme += "asyncio.run(main())\n"
            readme += "```\n\n"
        
        readme += "## Features\n\n"
        readme += "- ✅ Synchronous and asynchronous clients\n"
        readme += "- ✅ Automatic retry logic with exponential backoff\n"
        readme += "- ✅ Built-in response caching for deterministic requests\n"
        readme += "- ✅ Comprehensive error handling\n"
        readme += "- ✅ Performance monitoring and metrics\n"
        readme += "- ✅ Enterprise authentication support\n"
        readme += "- ✅ Streaming response support\n"
        readme += "- ✅ Type hints and IDE support\n\n"
        readme += "## Authentication\n\n"
        readme += "```python\n"
        readme += "# API Key authentication\n"
        readme += "client = LLMGatewayClient(\n"
        readme += "    api_key='your_api_key_here',\n"
        readme += "    organization_id='your_org_id'  # Optional\n"
        readme += ")\n"
        readme += "```\n\n"
        readme += "## Error Handling\n\n"
        readme += "```python\n"
        readme += f"from {self.config.package_name} import (\n"
        readme += "    LLMGatewayError,\n"
        readme += "    AuthenticationError,\n"
        readme += "    RateLimitError\n"
        readme += ")\n\n"
        readme += "try:\n"
        readme += "    response = client.chat_completion(messages=messages, model='gpt-3.5-turbo')\n"
        readme += "except AuthenticationError:\n"
        readme += "    print('Invalid API key')\n"
        readme += "except RateLimitError:\n"
        readme += "    print('Rate limit exceeded')\n"
        readme += "except LLMGatewayError as e:\n"
        readme += "    print(f'API error: {e.message}')\n"
        readme += "```\n\n"
        readme += "## Performance Monitoring\n\n"
        readme += "```python\n"
        readme += "# Get performance metrics\n"
        readme += "metrics = client.get_performance_metrics()\n"
        readme += "print(f'Success rate: {metrics[\"success_rate\"]:.2%}')\n"
        readme += "print(f'Average response time: {metrics[\"average_response_time\"]:.3f}s')\n"
        readme += "```\n\n"
        readme += "## License\n\n"
        readme += "MIT License\n"
        
        return readme


class JavaScriptSDKGenerator:
    """
    Enterprise JavaScript/TypeScript SDK generator.
    
    Generates production-ready JavaScript SDK with:
    - TypeScript definitions
    - Node.js and browser support
    - Enterprise authentication
    - Error handling
    - Performance monitoring
    """
    
    def __init__(self, config: SDKConfig, api_spec: Dict[str, Any]):
        """
        Initialize the JavaScript SDK generator.
        
        Args:
            config: SDK configuration
            api_spec: OpenAPI specification
        """
        self.config = config
        self.api_spec = api_spec
    
    def generate_sdk(self, output_dir: str) -> Dict[str, str]:
        """
        Generate complete JavaScript/TypeScript SDK.
        
        Args:
            output_dir: Output directory for SDK files
            
        Returns:
            Dict[str, str]: Generated files mapping
        """
        
        files = {}
        
        # Generate main client
        files["src/client.js"] = self._generate_client()
        
        # Generate TypeScript definitions
        if self.config.language in [SDKLanguage.TYPESCRIPT, SDKLanguage.JAVASCRIPT]:
            files["src/client.d.ts"] = self._generate_typescript_definitions()
        
        # Generate utilities
        files["src/auth.js"] = self._generate_auth_module()
        files["src/errors.js"] = self._generate_errors()
        files["src/utils.js"] = self._generate_utils()
        
        # Generate package files
        files["package.json"] = self._generate_package_json()
        files["README.md"] = self._generate_readme()
        files["index.js"] = self._generate_index()
        
        if self.config.language == SDKLanguage.TYPESCRIPT:
            files["tsconfig.json"] = self._generate_tsconfig()
        
        return files
    
    def _generate_client(self) -> str:
        """Generate main JavaScript client."""
        
        code = "/**\n"
        code += " * LLM Gateway JavaScript SDK - Main Client\n"
        code += f" * Version: {self.config.version}\n"
        code += " */\n\n"
        
        # Imports (Node.js style)
        code += "const { AuthenticationManager } = require('./auth');\n"
        code += "const { LLMGatewayError, AuthenticationError, RateLimitError } = require('./errors');\n"
        code += "const { RetryManager, CacheManager, PerformanceMonitor } = require('./utils');\n\n"
        
        # Main client class
        code += "class LLMGatewayClient {\n"
        code += "  /**\n"
        code += "   * Enterprise LLM Gateway JavaScript SDK Client.\n"
        code += "   *\n"
        code += "   * @param {Object} config - Configuration options\n"
        code += "   * @param {string} config.apiKey - Your API key\n"
        code += "   * @param {string} [config.baseUrl] - Base URL for the API\n"
        code += "   * @param {string} [config.organizationId] - Optional organization ID\n"
        code += "   * @param {number} [config.timeout] - Request timeout in milliseconds\n"
        code += "   * @param {number} [config.maxRetries] - Maximum number of retries\n"
        code += "   * @param {boolean} [config.enableCaching] - Enable response caching\n"
        code += "   * @param {boolean} [config.enableMonitoring] - Enable performance monitoring\n"
        code += "   */\n"
        code += "  constructor(config) {\n"
        code += "    if (!config.apiKey) {\n"
        code += "      throw new Error('API key is required');\n"
        code += "    }\n\n"
        code += f"    this.baseUrl = (config.baseUrl || '{self.config.base_url}').replace(/\\/$/, '');\n"
        code += "    this.timeout = config.timeout || 30000;\n\n"
        code += "    // Initialize components\n"
        code += "    this.auth = new AuthenticationManager(config.apiKey, config.organizationId);\n"
        code += "    this.retryManager = new RetryManager(config.maxRetries || 3);\n\n"
        code += "    this.cacheManager = null;\n"
        code += "    if (config.enableCaching !== false) {\n"
        code += "      this.cacheManager = new CacheManager();\n"
        code += "    }\n\n"
        code += "    this.performanceMonitor = null;\n"
        code += "    if (config.enableMonitoring !== false) {\n"
        code += "      this.performanceMonitor = new PerformanceMonitor();\n"
        code += "    }\n\n"
        code += "    // Detect environment (Node.js vs Browser)\n"
        code += "    this.isNode = typeof window === 'undefined';\n"
        code += "    \n"
        code += "    if (this.isNode) {\n"
        code += "      // Node.js environment\n"
        code += "      this.fetch = require('node-fetch');\n"
        code += "    } else {\n"
        code += "      // Browser environment\n"
        code += "      this.fetch = window.fetch.bind(window);\n"
        code += "    }\n"
        code += "  }\n\n"
        
        # Chat completion method
        code += "  /**\n"
        code += "   * Generate chat completion.\n"
        code += "   *\n"
        code += "   * @param {Object} params - Parameters for chat completion\n"
        code += "   * @param {Array} params.messages - Array of chat messages\n"
        code += "   * @param {string} params.model - Model identifier\n"
        code += "   * @param {string} [params.provider] - Optional provider name\n"
        code += "   * @param {number} [params.temperature] - Sampling temperature (0-1)\n"
        code += "   * @param {number} [params.maxTokens] - Maximum tokens to generate\n"
        code += "   * @param {boolean} [params.stream] - Enable streaming response\n"
        code += "   * @returns {Promise<Object>} Chat completion response\n"
        code += "   */\n"
        code += "  async chatCompletion(params) {\n"
        code += "    const { messages, model, provider, temperature = 0.7, maxTokens, stream = false, ...rest } = params;\n\n"
        code += "    if (!messages || !Array.isArray(messages)) {\n"
        code += "      throw new Error('Messages must be an array');\n"
        code += "    }\n"
        code += "    if (!model) {\n"
        code += "      throw new Error('Model is required');\n"
        code += "    }\n\n"
        code += "    const data = {\n"
        code += "      messages,\n"
        code += "      model,\n"
        code += "      temperature,\n"
        code += "      stream,\n"
        code += "      ...rest\n"
        code += "    };\n\n"
        code += "    if (provider) data.provider = provider;\n"
        code += "    if (maxTokens) data.max_tokens = maxTokens;\n\n"
        code += "    // Check cache for deterministic requests\n"
        code += "    let cacheKey = null;\n"
        code += "    if (this.cacheManager && temperature === 0 && !stream) {\n"
        code += "      cacheKey = this.cacheManager.generateKey('chat_completion', data);\n"
        code += "      const cachedResponse = this.cacheManager.get(cacheKey);\n"
        code += "      if (cachedResponse) {\n"
        code += "        return cachedResponse;\n"
        code += "      }\n"
        code += "    }\n\n"
        code += "    // Make request\n"
        code += "    const response = await this._makeRequest('POST', '/v1/chat/completions', data);\n\n"
        code += "    // Cache deterministic responses\n"
        code += "    if (cacheKey && this.cacheManager) {\n"
        code += "      this.cacheManager.set(cacheKey, response);\n"
        code += "    }\n\n"
        code += "    return response;\n"
        code += "  }\n\n"
        
        # List models method
        code += "  /**\n"
        code += "   * List available models.\n"
        code += "   *\n"
        code += "   * @param {Object} [params] - Optional parameters\n"
        code += "   * @param {string} [params.provider] - Filter by provider\n"
        code += "   * @param {number} [params.limit] - Maximum number of models\n"
        code += "   * @returns {Promise<Array>} Available models\n"
        code += "   */\n"
        code += "  async listModels(params = {}) {\n"
        code += "    const { provider, limit } = params;\n\n"
        code += "    const queryParams = {};\n"
        code += "    if (provider) queryParams.provider = provider;\n"
        code += "    if (limit) queryParams.limit = limit;\n\n"
        code += "    const response = await this._makeRequest('GET', '/v1/models', null, queryParams);\n"
        code += "    return response.models || [];\n"
        code += "  }\n\n"
        
        # Internal request method
        code += "  /**\n"
        code += "   * Make HTTP request with retry logic and error handling.\n"
        code += "   * @private\n"
        code += "   */\n"
        code += "  async _makeRequest(method, endpoint, body = null, queryParams = {}) {\n"
        code += "    const url = this._buildUrl(endpoint, queryParams);\n\n"
        code += "    // Start performance monitoring\n"
        code += "    if (this.performanceMonitor) {\n"
        code += "      this.performanceMonitor.startRequest(method, endpoint);\n"
        code += "    }\n\n"
        code += "    try {\n"
        code += "      const response = await this.retryManager.executeWithRetry(\n"
        code += "        () => this._executeRequest(method, url, body)\n"
        code += "      );\n\n"
        code += "      // Record success metrics\n"
        code += "      if (this.performanceMonitor) {\n"
        code += "        this.performanceMonitor.recordSuccess(response.status, response.responseTime);\n"
        code += "      }\n\n"
        code += "      return response.data;\n"
        code += "    } catch (error) {\n"
        code += "      // Record error metrics\n"
        code += "      if (this.performanceMonitor) {\n"
        code += "        this.performanceMonitor.recordError(error.message);\n"
        code += "      }\n"
        code += "      throw error;\n"
        code += "    }\n"
        code += "  }\n\n"
        
        # Execute request method
        code += "  async _executeRequest(method, url, body) {\n"
        code += "    const startTime = Date.now();\n\n"
        code += "    const options = {\n"
        code += "      method,\n"
        code += "      headers: this.auth.getHeaders(),\n"
        code += "      timeout: this.timeout\n"
        code += "    };\n\n"
        code += "    if (body) {\n"
        code += "      options.body = JSON.stringify(body);\n"
        code += "      options.headers['Content-Type'] = 'application/json';\n"
        code += "    }\n\n"
        code += "    const response = await this.fetch(url, options);\n"
        code += "    const responseTime = Date.now() - startTime;\n\n"
        code += "    // Handle HTTP errors\n"
        code += "    if (!response.ok) {\n"
        code += "      await this._handleErrorResponse(response);\n"
        code += "    }\n\n"
        code += "    const data = await response.json();\n\n"
        code += "    return {\n"
        code += "      status: response.status,\n"
        code += "      data,\n"
        code += "      responseTime\n"
        code += "    };\n"
        code += "  }\n\n"
        
        # Error handling
        code += "  async _handleErrorResponse(response) {\n"
        code += "    let errorMessage;\n"
        code += "    try {\n"
        code += "      const errorData = await response.json();\n"
        code += "      errorMessage = errorData.message || 'Unknown error';\n"
        code += "    } catch {\n"
        code += "      errorMessage = `HTTP ${response.status}: ${response.statusText}`;\n"
        code += "    }\n\n"
        code += "    switch (response.status) {\n"
        code += "      case 401:\n"
        code += "        throw new AuthenticationError('Invalid API key or authentication failed');\n"
        code += "      case 429:\n"
        code += "        throw new RateLimitError('Rate limit exceeded');\n"
        code += "      default:\n"
        code += "        throw new LLMGatewayError(errorMessage, response.status);\n"
        code += "    }\n"
        code += "  }\n\n"
        
        # URL builder
        code += "  _buildUrl(endpoint, queryParams = {}) {\n"
        code += "    const url = new URL(this.baseUrl + endpoint);\n"
        code += "    Object.keys(queryParams).forEach(key => {\n"
        code += "      if (queryParams[key] !== undefined && queryParams[key] !== null) {\n"
        code += "        url.searchParams.append(key, queryParams[key]);\n"
        code += "      }\n"
        code += "    });\n"
        code += "    return url.toString();\n"
        code += "  }\n\n"
        
        # Performance metrics
        code += "  /**\n"
        code += "   * Get performance metrics.\n"
        code += "   * @returns {Object} Performance metrics\n"
        code += "   */\n"
        code += "  getPerformanceMetrics() {\n"
        code += "    return this.performanceMonitor ? this.performanceMonitor.getMetrics() : {};\n"
        code += "  }\n"
        code += "}\n\n"
        code += "module.exports = { LLMGatewayClient };\n"
        
        return code
    
    def _generate_typescript_definitions(self) -> str:
        """Generate TypeScript type definitions."""
        
        code = "/**\n"
        code += " * LLM Gateway JavaScript SDK - TypeScript Definitions\n"
        code += " */\n\n"
        
        # Interfaces
        code += "export interface ChatMessage {\n"
        code += "  role: 'user' | 'assistant' | 'system';\n"
        code += "  content: string;\n"
        code += "  name?: string;\n"
        code += "}\n\n"
        
        code += "export interface ChatResponse {\n"
        code += "  id: string;\n"
        code += "  choices: Array<{\n"
        code += "    message: ChatMessage;\n"
        code += "    finish_reason: string;\n"
        code += "    index: number;\n"
        code += "  }>;\n"
        code += "  usage: {\n"
        code += "    prompt_tokens: number;\n"
        code += "    completion_tokens: number;\n"
        code += "    total_tokens: number;\n"
        code += "  };\n"
        code += "  model: string;\n"
        code += "  provider: string;\n"
        code += "  created: number;\n"
        code += "  cost?: number;\n"
        code += "  response_time_ms?: number;\n"
        code += "}\n\n"
        
        code += "export interface ModelInfo {\n"
        code += "  id: string;\n"
        code += "  name: string;\n"
        code += "  provider: string;\n"
        code += "  description?: string;\n"
        code += "  context_length?: number;\n"
        code += "  input_cost_per_token?: number;\n"
        code += "  output_cost_per_token?: number;\n"
        code += "  capabilities?: string[];\n"
        code += "}\n\n"
        
        code += "export interface ClientConfig {\n"
        code += "  apiKey: string;\n"
        code += "  baseUrl?: string;\n"
        code += "  organizationId?: string;\n"
        code += "  timeout?: number;\n"
        code += "  maxRetries?: number;\n"
        code += "  enableCaching?: boolean;\n"
        code += "  enableMonitoring?: boolean;\n"
        code += "}\n\n"
        
        code += "export interface ChatCompletionParams {\n"
        code += "  messages: ChatMessage[];\n"
        code += "  model: string;\n"
        code += "  provider?: string;\n"
        code += "  temperature?: number;\n"
        code += "  maxTokens?: number;\n"
        code += "  stream?: boolean;\n"
        code += "  [key: string]: any;\n"
        code += "}\n\n"
        
        code += "export interface PerformanceMetrics {\n"
        code += "  totalRequests: number;\n"
        code += "  successRate: number;\n"
        code += "  averageResponseTime: number;\n"
        code += "  errorCount: number;\n"
        code += "}\n\n"
        
        # Error classes
        code += "export declare class LLMGatewayError extends Error {\n"
        code += "  statusCode?: number;\n"
        code += "  constructor(message: string, statusCode?: number);\n"
        code += "}\n\n"
        
        code += "export declare class AuthenticationError extends LLMGatewayError {}\n"
        code += "export declare class RateLimitError extends LLMGatewayError {}\n\n"
        
        # Main client class
        code += "export declare class LLMGatewayClient {\n"
        code += "  constructor(config: ClientConfig);\n"
        code += "  \n"
        code += "  chatCompletion(params: ChatCompletionParams): Promise<ChatResponse>;\n"
        code += "  \n"
        code += "  listModels(params?: {\n"
        code += "    provider?: string;\n"
        code += "    limit?: number;\n"
        code += "  }): Promise<ModelInfo[]>;\n"
        code += "  \n"
        code += "  getPerformanceMetrics(): PerformanceMetrics;\n"
        code += "}\n"
        
        return code
    
    def _generate_auth_module(self) -> str:
        """Generate authentication module."""
        
        code = "/**\n"
        code += " * Authentication Manager\n"
        code += " */\n\n"
        
        code += "class AuthenticationManager {\n"
        code += "  constructor(apiKey, organizationId = null) {\n"
        code += "    this.apiKey = apiKey;\n"
        code += "    this.organizationId = organizationId;\n"
        code += "  }\n\n"
        
        code += "  getHeaders() {\n"
        code += "    const headers = {\n"
        code += "      'Authorization': `Bearer ${this.apiKey}`,\n"
        code += "      'Content-Type': 'application/json',\n"
        code += f"      'User-Agent': 'llm-gateway-js-sdk/{self.config.version}'\n"
        code += "    };\n\n"
        code += "    if (this.organizationId) {\n"
        code += "      headers['X-Organization-ID'] = this.organizationId;\n"
        code += "    }\n\n"
        code += "    return headers;\n"
        code += "  }\n"
        code += "}\n\n"
        code += "module.exports = { AuthenticationManager };\n"
        
        return code
    
    def _generate_errors(self) -> str:
        """Generate error classes."""
        
        code = "/**\n"
        code += " * Error Classes\n"
        code += " */\n\n"
        
        code += "class LLMGatewayError extends Error {\n"
        code += "  constructor(message, statusCode = null) {\n"
        code += "    super(message);\n"
        code += "    this.name = 'LLMGatewayError';\n"
        code += "    this.statusCode = statusCode;\n"
        code += "  }\n"
        code += "}\n\n"
        
        code += "class AuthenticationError extends LLMGatewayError {\n"
        code += "  constructor(message) {\n"
        code += "    super(message);\n"
        code += "    this.name = 'AuthenticationError';\n"
        code += "  }\n"
        code += "}\n\n"
        
        code += "class RateLimitError extends LLMGatewayError {\n"
        code += "  constructor(message) {\n"
        code += "    super(message);\n"
        code += "    this.name = 'RateLimitError';\n"
        code += "  }\n"
        code += "}\n\n"
        
        code += "module.exports = {\n"
        code += "  LLMGatewayError,\n"
        code += "  AuthenticationError,\n"
        code += "  RateLimitError\n"
        code += "};\n"
        
        return code
    
    def _generate_utils(self) -> str:
        """Generate utility classes."""
        
        code = "/**\n"
        code += " * Utility Classes\n"
        code += " */\n\n"
        
        # Retry Manager
        code += "class RetryManager {\n"
        code += "  constructor(maxRetries = 3, backoffFactor = 2) {\n"
        code += "    this.maxRetries = maxRetries;\n"
        code += "    this.backoffFactor = backoffFactor;\n"
        code += "  }\n\n"
        
        code += "  async executeWithRetry(fn) {\n"
        code += "    let lastError;\n\n"
        code += "    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {\n"
        code += "      try {\n"
        code += "        return await fn();\n"
        code += "      } catch (error) {\n"
        code += "        lastError = error;\n\n"
        code += "        if (attempt === this.maxRetries) {\n"
        code += "          break;\n"
        code += "        }\n\n"
        code += "        // Calculate backoff delay\n"
        code += "        const delay = Math.pow(this.backoffFactor, attempt) * 1000;\n"
        code += "        await new Promise(resolve => setTimeout(resolve, delay));\n"
        code += "      }\n"
        code += "    }\n\n"
        code += "    throw lastError;\n"
        code += "  }\n"
        code += "}\n\n"
        
        # Cache Manager
        code += "class CacheManager {\n"
        code += "  constructor(maxSize = 1000, ttl = 3600000) {\n" # TTL in milliseconds
        code += "    this.maxSize = maxSize;\n"
        code += "    this.ttl = ttl;\n"
        code += "    this.cache = new Map();\n"
        code += "  }\n\n"
        
        code += "  generateKey(operation, data) {\n"
        code += "    const crypto = require('crypto');\n"
        code += "    const cacheData = JSON.stringify(data, Object.keys(data).sort());\n"
        code += "    return crypto.createHash('md5').update(`${operation}:${cacheData}`).digest('hex');\n"
        code += "  }\n\n"
        
        code += "  get(key) {\n"
        code += "    const entry = this.cache.get(key);\n"
        code += "    if (entry) {\n"
        code += "      if (Date.now() - entry.timestamp < this.ttl) {\n"
        code += "        return entry.data;\n"
        code += "      } else {\n"
        code += "        this.cache.delete(key);\n"
        code += "      }\n"
        code += "    }\n"
        code += "    return null;\n"
        code += "  }\n\n"
        
        code += "  set(key, data) {\n"
        code += "    if (this.cache.size >= this.maxSize) {\n"
        code += "      // Remove oldest entry\n"
        code += "      const firstKey = this.cache.keys().next().value;\n"
        code += "      this.cache.delete(firstKey);\n"
        code += "    }\n\n"
        code += "    this.cache.set(key, {\n"
        code += "      data,\n"
        code += "      timestamp: Date.now()\n"
        code += "    });\n"
        code += "  }\n"
        code += "}\n\n"
        
        # Performance Monitor
        code += "class PerformanceMonitor {\n"
        code += "  constructor() {\n"
        code += "    this.metrics = {\n"
        code += "      totalRequests: 0,\n"
        code += "      successfulRequests: 0,\n"
        code += "      failedRequests: 0,\n"
        code += "      totalResponseTime: 0,\n"
        code += "      errors: []\n"
        code += "    };\n"
        code += "  }\n\n"
        
        code += "  startRequest(method, endpoint) {\n"
        code += "    this.metrics.totalRequests++;\n"
        code += "  }\n\n"
        
        code += "  recordSuccess(statusCode, responseTime) {\n"
        code += "    this.metrics.successfulRequests++;\n"
        code += "    this.metrics.totalResponseTime += responseTime;\n"
        code += "  }\n\n"
        
        code += "  recordError(errorMessage) {\n"
        code += "    this.metrics.failedRequests++;\n"
        code += "    this.metrics.errors.push({\n"
        code += "      message: errorMessage,\n"
        code += "      timestamp: Date.now()\n"
        code += "    });\n"
        code += "  }\n\n"
        
        code += "  getMetrics() {\n"
        code += "    const { totalRequests, successfulRequests, totalResponseTime } = this.metrics;\n"
        code += "    \n"
        code += "    return {\n"
        code += "      totalRequests,\n"
        code += "      successRate: totalRequests > 0 ? successfulRequests / totalRequests : 0,\n"
        code += "      averageResponseTime: successfulRequests > 0 ? totalResponseTime / successfulRequests : 0,\n"
        code += "      errorCount: this.metrics.errors.length\n"
        code += "    };\n"
        code += "  }\n"
        code += "}\n\n"
        
        code += "module.exports = {\n"
        code += "  RetryManager,\n"
        code += "  CacheManager,\n"
        code += "  PerformanceMonitor\n"
        code += "};\n"
        
        return code
    
    def _generate_package_json(self) -> str:
        """Generate package.json file."""
        
        package_json = {
            "name": self.config.package_name,
            "version": self.config.version,
            "description": self.config.description,
            "main": "index.js",
            "types": "src/client.d.ts" if self.config.language in [SDKLanguage.TYPESCRIPT, SDKLanguage.JAVASCRIPT] else None,
            "scripts": {
                "test": "jest",
                "build": "npm run build:js",
                "build:js": "babel src -d lib",
                "lint": "eslint src/",
                "docs": "jsdoc src/ -d docs/"
            },
            "keywords": [
                "llm",
                "ai",
                "openai",
                "anthropic",
                "api",
                "gateway",
                "sdk"
            ],
            "author": self.config.author,
            "license": "MIT",
            "dependencies": {
                "node-fetch": "^2.6.7"
            },
            "devDependencies": {
                "@babel/cli": "^7.20.0",
                "@babel/core": "^7.20.0",
                "@babel/preset-env": "^7.20.0",
                "eslint": "^8.30.0",
                "jest": "^29.3.0",
                "jsdoc": "^4.0.0"
            },
            "engines": {
                "node": ">=14.0.0"
            },
            "repository": {
                "type": "git",
                "url": f"git+https://github.com/your-org/{self.config.package_name}.git"
            },
            "bugs": {
                "url": f"https://github.com/your-org/{self.config.package_name}/issues"
            }
        }
        
        # Remove None values
        package_json = {k: v for k, v in package_json.items() if v is not None}
        
        return json.dumps(package_json, indent=2)
    
    def _generate_index(self) -> str:
        """Generate main index.js file."""
        
        code = "/**\n"
        code += f" * {self.config.package_name}\n"
        code += f" * Version: {self.config.version}\n"
        code += " */\n\n"
        
        code += "const { LLMGatewayClient } = require('./src/client');\n"
        code += "const { LLMGatewayError, AuthenticationError, RateLimitError } = require('./src/errors');\n\n"
        
        code += "module.exports = {\n"
        code += "  LLMGatewayClient,\n"
        code += "  LLMGatewayError,\n"
        code += "  AuthenticationError,\n"
        code += "  RateLimitError\n"
        code += "};\n"
        
        return code
    
    def _generate_tsconfig(self) -> str:
        """Generate TypeScript configuration."""
        
        tsconfig = {
            "compilerOptions": {
                "target": "ES2020",
                "module": "commonjs",
                "lib": ["ES2020"],
                "declaration": True,
                "outDir": "./lib",
                "rootDir": "./src",
                "strict": True,
                "esModuleInterop": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True,
                "moduleResolution": "node",
                "resolveJsonModule": True
            },
            "include": ["src/**/*"],
            "exclude": ["node_modules", "lib", "**/*.test.ts"]
        }
        
        return json.dumps(tsconfig, indent=2)
    
    def _generate_readme(self) -> str:
        """Generate README.md for JavaScript SDK."""
        
        readme = f"# {self.config.package_name}\n\n"
        readme += f"{self.config.description}\n\n"
        readme += "## Installation\n\n"
        readme += f"```bash\nnpm install {self.config.package_name}\n```\n\n"
        readme += "## Quick Start\n\n"
        readme += "```javascript\n"
        readme += f"const {{ LLMGatewayClient }} = require('{self.config.package_name}');\n\n"
        readme += "// Initialize client\n"
        readme += "const client = new LLMGatewayClient({\n"
        readme += "  apiKey: 'your_api_key_here'\n"
        readme += "});\n\n"
        readme += "// Generate chat completion\n"
        readme += "async function example() {\n"
        readme += "  try {\n"
        readme += "    const response = await client.chatCompletion({\n"
        readme += "      messages: [{ role: 'user', content: 'Hello, how are you?' }],\n"
        readme += "      model: 'gpt-3.5-turbo'\n"
        readme += "    });\n\n"
        readme += "    console.log(response.choices[0].message.content);\n"
        readme += "  } catch (error) {\n"
        readme += "    console.error('Error:', error.message);\n"
        readme += "  }\n"
        readme += "}\n\n"
        readme += "example();\n"
        readme += "```\n\n"
        readme += "## Features\n\n"
        readme += "- ✅ Node.js and browser support\n"
        readme += "- ✅ TypeScript definitions included\n"
        readme += "- ✅ Automatic retry logic with exponential backoff\n"
        readme += "- ✅ Built-in response caching\n"
        readme += "- ✅ Performance monitoring\n"
        readme += "- ✅ Enterprise authentication\n"
        readme += "- ✅ Comprehensive error handling\n\n"
        readme += "## Error Handling\n\n"
        readme += "```javascript\n"
        readme += f"const {{ LLMGatewayClient, AuthenticationError, RateLimitError }} = require('{self.config.package_name}');\n\n"
        readme += "try {\n"
        readme += "  const response = await client.chatCompletion(params);\n"
        readme += "} catch (error) {\n"
        readme += "  if (error instanceof AuthenticationError) {\n"
        readme += "    console.error('Invalid API key');\n"
        readme += "  } else if (error instanceof RateLimitError) {\n"
        readme += "    console.error('Rate limit exceeded');\n"
        readme += "  } else {\n"
        readme += "    console.error('API error:', error.message);\n"
        readme += "  }\n"
        readme += "}\n"
        readme += "```\n\n"
        readme += "## License\n\n"
        readme += "MIT License\n"
        
        return readme


class SDKGenerator:
    """
    Main SDK generator that coordinates language-specific generators.
    """
    
    def __init__(self, api_spec: Dict[str, Any]):
        """
        Initialize the SDK generator.
        
        Args:
            api_spec: OpenAPI specification
        """
        self.api_spec = api_spec
        self.generators = {
            SDKLanguage.PYTHON: PythonSDKGenerator,
            SDKLanguage.JAVASCRIPT: JavaScriptSDKGenerator,
            SDKLanguage.TYPESCRIPT: JavaScriptSDKGenerator
        }
    
    def generate_sdk(self, config: SDKConfig, output_dir: str) -> Dict[str, str]:
        """
        Generate SDK for specified language.
        
        Args:
            config: SDK configuration
            output_dir: Output directory
            
        Returns:
            Dict[str, str]: Generated files
        """
        
        generator_class = self.generators.get(config.language)
        if not generator_class:
            raise ValueError(f"Unsupported language: {config.language}")
        
        generator = generator_class(config, self.api_spec)
        return generator.generate_sdk(output_dir)
    
    def get_supported_languages(self) -> List[SDKLanguage]:
        """Get list of supported SDK languages."""
        return list(self.generators.keys())