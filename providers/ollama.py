"""
Ollama Provider for Unified LLM Gateway
Handles local Ollama models like Llama, CodeLlama, Mistral, etc.
"""
import aiohttp
import asyncio
import json
import time
from typing import Dict, Any, List, Optional

from .base import (
    BaseModelProvider, 
    GenerationRequest, 
    GenerationResponse, 
    ModelMetadata, 
    ModelCapability
)
from utils.logging_setup import get_logger

logger = get_logger(__name__)


class OllamaProvider(BaseModelProvider):
    """Ollama local models provider implementation"""
    
    def __init__(self, provider_config: Dict[str, Any]):
        self.provider_name = "ollama"
        self.provider_config = provider_config
        self.base_url = provider_config.get("base_url", "http://localhost:11434")
        self.timeout = provider_config.get("timeout", 60)
        self._initialized = False
        self._available_models = []
    
    async def initialize(self) -> bool:
        """Initialize Ollama provider and check available models"""
        try:
            # Check if Ollama is running and get available models
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        models = data.get("models", [])
                        
                        self._available_models = []
                        for model in models:
                            model_id = model.get("name", "")
                            if model_id:
                                # Determine capabilities based on model name
                                capabilities = [ModelCapability.TEXT_GENERATION]
                                if "code" in model_id.lower():
                                    capabilities.append(ModelCapability.CODE_GENERATION)
                                
                                metadata = ModelMetadata(
                                    model_id=model_id,
                                    model_name=model_id,
                                    provider_name=self.provider_name,
                                    capabilities=capabilities,
                                    context_length=self._get_context_length(model_id),
                                    cost_per_1k_tokens=0.0,  # Local models are free
                                    max_output_tokens=2048,
                                    supports_system_messages=True,
                                    supports_temperature=True
                                )
                                self._available_models.append(metadata)
                        
                        self._initialized = True
                        logger.info(f"Ollama provider initialized with {len(self._available_models)} models")
                        return True
                    else:
                        logger.error(f"Failed to connect to Ollama server: HTTP {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Failed to initialize Ollama provider: {str(e)}")
            return False
    
    def _get_context_length(self, model_id: str) -> int:
        """Estimate context length based on model name"""
        if "32k" in model_id.lower():
            return 32768
        elif "16k" in model_id.lower():
            return 16384
        elif "8k" in model_id.lower():
            return 8192
        else:
            return 4096  # Default context length
    
    async def generate_text(self, request: GenerationRequest, model_id: str) -> GenerationResponse:
        """Generate text using Ollama model"""
        start_time = time.time()
        
        try:
            if not self._initialized:
                await self.initialize()
            
            # Check if model is available
            if not any(m.model_id == model_id for m in self._available_models):
                return GenerationResponse(
                    content="",
                    model_id=model_id,
                    provider_name=self.provider_name,
                    error=f"Model {model_id} not available"
                )
            
            # Prepare messages
            messages = []
            if request.system_message:
                messages.append({"role": "system", "content": request.system_message})
            messages.append({"role": "user", "content": request.prompt})
            
            # Prepare request payload
            payload = {
                "model": model_id,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": request.temperature or 0.1,
                    "num_predict": request.max_tokens or 2048
                }
            }
            
            # Make request to Ollama
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data.get("message", {}).get("content", "")
                        
                        response_time = time.time() - start_time
                        
                        # Estimate tokens (Ollama doesn't provide exact counts)
                        prompt_tokens = self._estimate_tokens(request.prompt + (request.system_message or ""))
                        completion_tokens = self._estimate_tokens(content)
                        
                        return GenerationResponse(
                            content=content,
                            model_id=model_id,
                            provider_name=self.provider_name,
                            prompt_tokens=prompt_tokens,
                            completion_tokens=completion_tokens,
                            total_tokens=prompt_tokens + completion_tokens,
                            cost=0.0,  # Local models are free
                            response_time=response_time,
                            raw_response=data
                        )
                    else:
                        error_text = await response.text()
                        return GenerationResponse(
                            content="",
                            model_id=model_id,
                            provider_name=self.provider_name,
                            response_time=time.time() - start_time,
                            error=f"Ollama request failed: {error_text}"
                        )
                        
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Ollama text generation failed: {str(e)}")
            return GenerationResponse(
                content="",
                model_id=model_id,
                provider_name=self.provider_name,
                response_time=response_time,
                error=str(e)
            )
    
    async def generate_structured_output(
        self, 
        request: GenerationRequest, 
        model_id: str
    ) -> GenerationResponse:
        """Generate structured JSON output using Ollama"""
        try:
            if not request.output_schema:
                return GenerationResponse(
                    content="",
                    model_id=model_id,
                    provider_name=self.provider_name,
                    error="output_schema is required for structured output"
                )
            
            # Create structured prompt
            schema_str = json.dumps(request.output_schema, indent=2)
            structured_prompt = f"""
            {request.prompt}
            
            IMPORTANT: Respond with valid JSON that matches this exact schema:
            {schema_str}
            
            Return only the JSON response, no additional text or formatting.
            """
            
            # Create new request with structured prompt
            structured_request = GenerationRequest(
                prompt=structured_prompt,
                system_message=request.system_message,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stop_sequences=request.stop_sequences,
                extra_params=request.extra_params
            )
            
            # Generate response
            response = await self.generate_text(structured_request, model_id)
            
            if response.error:
                return response
            
            # Parse JSON response
            try:
                parsed_content = json.loads(response.content)
                response.content = json.dumps(parsed_content)
                return response
            except json.JSONDecodeError as e:
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
                if json_match:
                    try:
                        parsed_content = json.loads(json_match.group())
                        response.content = json.dumps(parsed_content)
                        return response
                    except json.JSONDecodeError:
                        pass
                
                response.error = f"Invalid JSON response: {str(e)}"
                return response
            
        except Exception as e:
            logger.error(f"Ollama structured output failed: {str(e)}")
            return GenerationResponse(
                content="",
                model_id=model_id,
                provider_name=self.provider_name,
                error=str(e)
            )
    
    def get_available_models(self) -> List[ModelMetadata]:
        """Get list of available Ollama models"""
        return self._available_models
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Ollama provider health"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        models = data.get("models", [])
                        
                        return {
                            "provider": self.provider_name,
                            "status": "healthy",
                            "available_models": len(models),
                            "initialized": self._initialized,
                            "server_url": self.base_url,
                            "models": [m.get("name") for m in models[:3]]  # First 3 models
                        }
                    else:
                        return {
                            "provider": self.provider_name,
                            "status": "unhealthy",
                            "error": f"HTTP {response.status}",
                            "server_url": self.base_url
                        }
                        
        except Exception as e:
            return {
                "provider": self.provider_name,
                "status": "unhealthy",
                "error": str(e),
                "server_url": self.base_url
            }
    
    def get_recommended_model(self, capability: ModelCapability, complexity: str = "medium") -> Optional[str]:
        """Get recommended Ollama model based on capability and complexity"""
        available_model_names = [m.model_id for m in self._available_models]
        
        if capability == ModelCapability.CODE_GENERATION:
            # Prefer code models
            for model in ["codellama:13b", "codellama:7b", "codellama"]:
                if model in available_model_names:
                    return model
        
        # General text generation based on complexity
        if complexity == "simple":
            for model in ["llama3:8b", "llama2:7b", "mistral:7b"]:
                if model in available_model_names:
                    return model
        elif complexity == "complex":
            for model in ["llama3:70b", "llama2:70b", "llama3:13b"]:
                if model in available_model_names:
                    return model
        
        # Return first available model as fallback
        if available_model_names:
            return available_model_names[0]
        
        return None
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough estimation of token count (4 chars per token average)"""
        return max(1, len(text) // 4)
    
    async def pull_model(self, model_name: str) -> Dict[str, Any]:
        """Pull a model from Ollama registry"""
        try:
            payload = {"name": model_name}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/pull",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=300)  # 5 minutes for model download
                ) as response:
                    if response.status == 200:
                        # Refresh available models
                        await self.initialize()
                        return {
                            "success": True,
                            "message": f"Model {model_name} pulled successfully"
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"Failed to pull model: {error_text}"
                        }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }