"""
DeepSeek Provider for WinCraft AI
Implements DeepSeek R1 models via Hugging Face Inference API
"""
import asyncio
import json
import os
import time
from typing import Dict, Any, List, Optional

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

from .base import (
    BaseModelProvider, GenerationRequest, GenerationResponse, 
    ModelMetadata, ModelCapability
)
from utils.logging_setup import get_logger

logger = get_logger(__name__)


class DeepSeekProvider(BaseModelProvider):
    """DeepSeek provider implementation via Hugging Face Inference API"""
    
    def __init__(self, provider_config: Dict[str, Any]):
        super().__init__(provider_config)
        self.client = None
        self.api_key = None
        self.base_url = "https://api-inference.huggingface.co/models"
        self.initialized = False
        
        # Model configurations
        self.model_configs = {
            "deepseek-ai/DeepSeek-R1-Distill-Llama-70B": {
                "model_name": "DeepSeek-R1-Distill-Llama-70B",
                "capabilities": [
                    ModelCapability.TEXT_GENERATION,
                    ModelCapability.STRUCTURED_OUTPUT
                ],
                "context_length": 32768,
                "cost_per_1k_tokens": 0.0001,
                "max_output_tokens": 4096
            }
        }
    
    async def initialize(self) -> bool:
        """Initialize the DeepSeek provider"""
        if not HTTPX_AVAILABLE:
            logger.error("httpx package not available for DeepSeek provider")
            return False
        
        try:
            # Get API key from config or environment
            self.api_key = (
                self.provider_config.get("api_key") or 
                os.getenv("HUGGINGFACE_API_KEY")
            )
            
            if not self.api_key:
                logger.error("No Hugging Face API key provided for DeepSeek provider")
                return False
            
            # Initialize HTTP client
            self.client = httpx.AsyncClient(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=60.0
            )
            
            # Initialize model metadata
            self._initialize_model_metadata()
            
            # Test connection
            await self._test_connection()
            
            self.initialized = True
            logger.info(f"DeepSeek provider initialized with {len(self.model_configs)} models")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize DeepSeek provider: {str(e)}")
            return False
    
    def _initialize_model_metadata(self):
        """Initialize model metadata"""
        for model_id, config in self.model_configs.items():
            self._models_metadata[model_id] = ModelMetadata(
                model_id=model_id,
                provider_name=self.provider_name,
                model_name=config["model_name"],
                capabilities=config["capabilities"],
                context_length=config["context_length"],
                cost_per_1k_tokens=config["cost_per_1k_tokens"],
                max_output_tokens=config["max_output_tokens"],
                supports_system_messages=True,
                supports_temperature=True
            )
    
    async def _test_connection(self):
        """Test connection to Hugging Face API"""
        try:
            model_id = "deepseek-ai/DeepSeek-R1-Distill-Llama-70B"
            url = f"{self.base_url}/{model_id}"
            
            response = await self.client.post(
                url,
                json={
                    "inputs": "Hello, this is a test.",
                    "parameters": {
                        "max_new_tokens": 10,
                        "temperature": 0.1
                    }
                }
            )
            
            if response.status_code == 200:
                logger.info("DeepSeek connection test successful")
            else:
                logger.warning(f"DeepSeek connection test returned {response.status_code}")
                
        except Exception as e:
            logger.warning(f"DeepSeek connection test failed: {str(e)}")
    
    async def generate_text(self, request: GenerationRequest, model_id: str) -> GenerationResponse:
        """Generate text using DeepSeek model"""
        if not self.initialized:
            return GenerationResponse(
                content="", 
                model_id=model_id, 
                provider_name=self.provider_name,
                error="Provider not initialized"
            )
        
        start_time = time.time()
        
        try:
            # Convert request to DeepSeek format
            prompt = self._format_prompt(request)
            
            # Prepare API request
            url = f"{self.base_url}/{model_id}"
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": request.max_tokens or 2048,
                    "temperature": request.temperature or 0.1,
                    "top_p": 0.9,
                    "do_sample": True,
                    "return_full_text": False
                }
            }
            
            # Make API call
            response = await self.client.post(url, json=payload)
            end_time = time.time()
            
            if response.status_code != 200:
                error_msg = f"DeepSeek API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return GenerationResponse(
                    content="",
                    model_id=model_id,
                    provider_name=self.provider_name,
                    error=error_msg,
                    response_time=end_time - start_time
                )
            
            # Parse response
            result = response.json()
            content = ""
            
            if isinstance(result, list) and len(result) > 0:
                content = result[0].get("generated_text", "")
            elif isinstance(result, dict):
                content = result.get("generated_text", "")
            
            # Calculate tokens and cost
            prompt_tokens = len(prompt.split()) * 1.3  # Rough estimation
            completion_tokens = len(content.split()) * 1.3
            cost = self.calculate_cost(int(prompt_tokens), int(completion_tokens), model_id)
            
            return GenerationResponse(
                content=content,
                model_id=model_id,
                provider_name=self.provider_name,
                prompt_tokens=int(prompt_tokens),
                completion_tokens=int(completion_tokens),
                total_tokens=int(prompt_tokens + completion_tokens),
                cost=cost,
                response_time=end_time - start_time,
                raw_response=result
            )
            
        except Exception as e:
            end_time = time.time()
            error_msg = f"DeepSeek generation error: {str(e)}"
            logger.error(error_msg)
            
            return GenerationResponse(
                content="",
                model_id=model_id,
                provider_name=self.provider_name,
                error=error_msg,
                response_time=end_time - start_time
            )
    
    async def generate_structured_output(
        self, 
        request: GenerationRequest, 
        model_id: str
    ) -> GenerationResponse:
        """Generate structured JSON output"""
        if not request.output_schema:
            return GenerationResponse(
                content="",
                model_id=model_id,
                provider_name=self.provider_name,
                error="No output schema provided for structured output"
            )
        
        # Add JSON formatting instruction to the prompt
        structured_prompt = f"""
{request.prompt}

Please respond with valid JSON that follows this schema:
{json.dumps(request.output_schema, indent=2)}

Response:
"""
        
        # Create modified request
        structured_request = GenerationRequest(
            prompt=structured_prompt,
            system_message=request.system_message,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stop_sequences=request.stop_sequences,
            stream=False,
            extra_params=request.extra_params
        )
        
        return await self.generate_text(structured_request, model_id)
    
    def _format_prompt(self, request: GenerationRequest) -> str:
        """Format prompt for DeepSeek R1 model"""
        prompt_parts = []
        
        if request.system_message:
            prompt_parts.append(f"<|system|>\n{request.system_message}\n<|end|>")
        
        prompt_parts.append(f"<|user|>\n{request.prompt}\n<|end|>")
        prompt_parts.append("<|assistant|>\n")
        
        return "\n".join(prompt_parts)
    
    def get_available_models(self) -> List[ModelMetadata]:
        """Get list of available models"""
        return list(self._models_metadata.values())
    
    async def health_check(self) -> Dict[str, Any]:
        """Check provider health"""
        if not self.initialized:
            return {
                "status": "unhealthy",
                "error": "Provider not initialized",
                "models_available": 0
            }
        
        try:
            # Simple health check
            await self._test_connection()
            
            return {
                "status": "healthy",
                "models_available": len(self.model_configs),
                "provider": self.provider_name,
                "api_endpoint": self.base_url
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "models_available": len(self.model_configs)
            }
    
    async def cleanup(self):
        """Clean up resources"""
        if self.client:
            await self.client.aclose()
            logger.info("DeepSeek provider cleaned up") 