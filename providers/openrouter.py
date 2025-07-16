"""
OpenRouter Provider for Unified Model Bridge
Supports DeepSeek R1, GPT-4, Claude, and other models through OpenRouter's API
Uses OpenAI-compatible syntax with OpenRouter endpoint
"""
import asyncio
import json
import time
import os
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI

from .base import BaseModelProvider, GenerationRequest, GenerationResponse, ModelMetadata, ModelCapability
from utils.logging_setup import get_logger

logger = get_logger(__name__)


class OpenRouterProvider(BaseModelProvider):
    """OpenRouter provider with support for DeepSeek R1 and other models"""
    
    def __init__(self, provider_config: Dict[str, Any]):
        super().__init__(provider_config)
        self.client: Optional[AsyncOpenAI] = None
        self.api_key = provider_config.get("api_key") or os.getenv("OPENROUTER_API_KEY")
        self.base_url = provider_config.get("base_url", "https://openrouter.ai/api/v1")
        self.default_temperature = provider_config.get("temperature", 0.1)
        self.timeout = provider_config.get("timeout", 60)
        self.site_url = provider_config.get("site_url", "https://wincraft.ai")
        self.app_name = provider_config.get("app_name", "WinCraft AI")
        
        # Load models from config or use defaults
        self.model_configs = provider_config.get("models", self._get_default_models())
        self._setup_models_metadata()
    
    def _get_default_models(self) -> Dict[str, Dict[str, Any]]:
        """Get default OpenRouter models configuration"""
        return {
            "deepseek/deepseek-r1-0528:free": {
                "context_length": 32768,
                "cost_per_1k_tokens": 0.0,  # Free model
                "max_output_tokens": 8192,
                "model_name": "DeepSeek R1 (Free)",
                "description": "Free DeepSeek R1 reasoning model"
            },
            "deepseek/deepseek-r1": {
                "context_length": 32768,
                "cost_per_1k_tokens": 0.14,
                "max_output_tokens": 8192,
                "model_name": "DeepSeek R1",
                "description": "DeepSeek R1 reasoning model"
            },
            "openai/gpt-4o": {
                "context_length": 128000,
                "cost_per_1k_tokens": 0.005,
                "max_output_tokens": 4096,
                "model_name": "GPT-4o (via OpenRouter)",
                "description": "GPT-4o through OpenRouter"
            },
            "anthropic/claude-3.5-sonnet": {
                "context_length": 200000,
                "cost_per_1k_tokens": 0.003,
                "max_output_tokens": 4096,
                "model_name": "Claude 3.5 Sonnet (via OpenRouter)",
                "description": "Claude 3.5 Sonnet through OpenRouter"
            },
            "google/gemini-pro-1.5": {
                "context_length": 2000000,
                "cost_per_1k_tokens": 0.00125,
                "max_output_tokens": 8192,
                "model_name": "Gemini Pro 1.5 (via OpenRouter)",
                "description": "Gemini Pro 1.5 through OpenRouter"
            }
        }
    
    def _setup_models_metadata(self):
        """Setup metadata for all available models"""
        for model_id, config in self.model_configs.items():
            capabilities = [
                ModelCapability.TEXT_GENERATION,
                ModelCapability.STRUCTURED_OUTPUT,
                ModelCapability.STREAMING
            ]
            
            # Add function calling for supported models
            if any(x in model_id.lower() for x in ["gpt-4", "claude", "gemini"]):
                capabilities.append(ModelCapability.FUNCTION_CALLING)
            
            # Add vision for vision-capable models
            if any(x in model_id.lower() for x in ["gpt-4o", "claude-3.5", "gemini"]):
                capabilities.append(ModelCapability.VISION)
            
            self._models_metadata[model_id] = ModelMetadata(
                model_id=model_id,
                provider_name=self.provider_name,
                model_name=config.get("model_name", model_id),
                capabilities=capabilities,
                context_length=config.get("context_length", 32768),
                cost_per_1k_tokens=config.get("cost_per_1k_tokens", 0.0),
                max_output_tokens=config.get("max_output_tokens", 8192),
                supports_system_messages=True,
                supports_temperature=True
            )
    
    async def initialize(self) -> bool:
        """Initialize OpenRouter client"""
        try:
            if not self.api_key:
                logger.warning("OpenRouter API key not provided, provider will be disabled")
                return False
            
            # Create OpenAI client configured for OpenRouter
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout,
                default_headers={
                    "HTTP-Referer": self.site_url,
                    "X-Title": self.app_name,
                }
            )
            
            # Test connection with a simple request
            test_response = await self.health_check()
            if test_response["status"] == "healthy":
                logger.info("OpenRouter provider initialized successfully")
                return True
            else:
                logger.error(f"OpenRouter provider health check failed: {test_response.get('error')}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenRouter provider: {str(e)}")
            return False
    
    async def generate_text(self, request: GenerationRequest, model_id: str) -> GenerationResponse:
        """Generate text using OpenRouter models"""
        start_time = time.time()
        
        try:
            if not self.client:
                return GenerationResponse(
                    content="",
                    model_id=model_id,
                    provider_name=self.provider_name,
                    error="Provider not initialized"
                )
            
            # Prepare messages
            messages = []
            if request.system_message:
                messages.append({"role": "system", "content": request.system_message})
            messages.append({"role": "user", "content": request.prompt})
            
            # Prepare parameters
            params = {
                "model": model_id,
                "messages": messages,
                "temperature": request.temperature or self.default_temperature,
                "stream": request.stream
            }
            
            # Add max_tokens if specified
            if request.max_tokens:
                params["max_tokens"] = request.max_tokens
            
            # Add stop sequences if provided
            if request.stop_sequences:
                params["stop"] = request.stop_sequences
            
            # Add extra parameters
            if request.extra_params:
                params.update(request.extra_params)
            
            # Make API call
            response = await self.client.chat.completions.create(**params)
            
            # Extract response data
            content = response.choices[0].message.content or ""
            usage = response.usage
            
            # Calculate cost
            cost = self.calculate_cost(
                usage.prompt_tokens,
                usage.completion_tokens,
                model_id
            )
            
            return GenerationResponse(
                content=content,
                model_id=model_id,
                provider_name=self.provider_name,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
                cost=cost,
                response_time=time.time() - start_time,
                raw_response=response
            )
            
        except Exception as e:
            logger.error(f"OpenRouter generation error: {str(e)}")
            return GenerationResponse(
                content="",
                model_id=model_id,
                provider_name=self.provider_name,
                error=str(e),
                response_time=time.time() - start_time
            )
    
    async def generate_structured_output(
        self, 
        request: GenerationRequest, 
        model_id: str
    ) -> GenerationResponse:
        """Generate structured JSON output using OpenRouter models"""
        if not request.output_schema:
            return GenerationResponse(
                content="",
                model_id=model_id,
                provider_name=self.provider_name,
                error="No output schema provided for structured output"
            )
        
        # Use function calling for structured output (if supported)
        if ModelCapability.FUNCTION_CALLING in self._models_metadata.get(model_id, ModelMetadata()).capabilities:
            enhanced_request = GenerationRequest(
                prompt=request.prompt,
                system_message=request.system_message,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stop_sequences=request.stop_sequences,
                stream=False,  # Structured output doesn't support streaming
                extra_params={
                    "tools": [{
                        "type": "function",
                        "function": {
                            "name": "structured_response",
                            "description": "Generate structured response according to schema",
                            "parameters": request.output_schema
                        }
                    }],
                    "tool_choice": {"type": "function", "function": {"name": "structured_response"}}
                }
            )
            
            response = await self.generate_text(enhanced_request, model_id)
            
            # Extract function call result
            if response.raw_response and hasattr(response.raw_response, 'choices'):
                choice = response.raw_response.choices[0]
                if hasattr(choice.message, 'tool_calls') and choice.message.tool_calls:
                    function_call = choice.message.tool_calls[0]
                    if hasattr(function_call, 'function'):
                        try:
                            structured_content = json.loads(function_call.function.arguments)
                            response.content = json.dumps(structured_content, indent=2)
                        except json.JSONDecodeError:
                            response.content = function_call.function.arguments
            
            return response
        else:
            # Fallback: Use prompt engineering for structured output
            structured_prompt = f"""
{request.prompt}

Please respond with valid JSON that matches this schema:
{json.dumps(request.output_schema, indent=2)}

Response (JSON only):
"""
            
            enhanced_request = GenerationRequest(
                prompt=structured_prompt,
                system_message=request.system_message,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stop_sequences=request.stop_sequences,
                stream=False
            )
            
            return await self.generate_text(enhanced_request, model_id)
    
    def get_available_models(self) -> List[ModelMetadata]:
        """Get list of available model metadata"""
        return list(self._models_metadata.values())
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        try:
            if not self.client:
                return {"status": "unhealthy", "error": "Client not initialized"}
            
            # Test with a simple request using the free DeepSeek model
            test_model = "deepseek/deepseek-r1-0528:free"
            response = await self.client.chat.completions.create(
                model=test_model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10,
                temperature=0
            )
            
            return {
                "status": "healthy",
                "models_available": len(self._models_metadata),
                "test_model": test_model,
                "test_response_length": len(response.choices[0].message.content or "")
            }
            
        except Exception as e:
            return {
                "status": "unhealthy", 
                "error": str(e)
            }
    
    def get_recommended_model(self, capability: ModelCapability, complexity: str = "medium") -> Optional[str]:
        """Get recommended model for a capability and complexity"""
        available_models = [
            (model_id, metadata) for model_id, metadata in self._models_metadata.items()
            if capability in metadata.capabilities
        ]
        
        if not available_models:
            return None
        
        # Prioritize based on complexity and cost
        if complexity == "high":
            # Use most capable model
            return "deepseek/deepseek-r1" if "deepseek/deepseek-r1" in self._models_metadata else available_models[0][0]
        elif complexity == "low":
            # Use free model for simple tasks
            return "deepseek/deepseek-r1-0528:free" if "deepseek/deepseek-r1-0528:free" in self._models_metadata else available_models[0][0]
        else:
            # Use free model as default
            return "deepseek/deepseek-r1-0528:free" if "deepseek/deepseek-r1-0528:free" in self._models_metadata else available_models[0][0] 