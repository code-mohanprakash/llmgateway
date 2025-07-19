"""
OpenAI Provider for Unified Model Bridge
Supports GPT-4, GPT-3.5, and other OpenAI models with latest syntax
"""
import asyncio
import json
import time
import os
from typing import Dict, Any, List, Optional
from openai import AsyncOpenAI

from .base import BaseModelProvider, GenerationRequest, GenerationResponse, ModelMetadata, ModelCapability
try:
    from utils.logging_setup import get_logger
except ImportError:
    import logging
    def get_logger(name): return logging.getLogger(name)

logger = get_logger(__name__)


class OpenAIProvider(BaseModelProvider):
    """OpenAI provider with support for all GPT models"""
    
    def __init__(self, provider_config: Dict[str, Any]):
        super().__init__(provider_config)
        self.client: Optional[AsyncOpenAI] = None
        self.api_key = provider_config.get("api_key") or os.getenv("OPENAI_API_KEY")
        self.organization = provider_config.get("organization") or os.getenv("OPENAI_ORG_ID")
        self.base_url = provider_config.get("base_url", "https://api.openai.com/v1")
        self.default_temperature = provider_config.get("temperature", 0.1)
        self.timeout = provider_config.get("timeout", 60)
        
        # Load models from config with defaults
        self.model_configs = provider_config.get("models", self._get_default_models())
        self._setup_models_metadata()
    
    def _get_default_models(self) -> Dict[str, Any]:
        """Get default OpenAI model configurations"""
        return {
            # O-Series Reasoning Models (REAL - Available now)
            "o1": {
                "context_length": 200000,
                "cost_per_1k_tokens": 0.015,
                "max_output_tokens": 65536,
                "category": "reasoning",
                "speed": "slow",
                "reasoning": "exceptional",
                "capabilities": ["text", "advanced_reasoning", "mathematics", "coding"],
                "knowledge_cutoff": "2023-10"
            },
            "o1-mini": {
                "context_length": 128000,
                "cost_per_1k_tokens": 0.003,
                "max_output_tokens": 65536,
                "category": "reasoning",
                "speed": "medium",
                "reasoning": "excellent",
                "capabilities": ["text", "reasoning", "mathematics", "coding"],
                "knowledge_cutoff": "2023-10"
            },
            "o1-preview": {
                "context_length": 128000,
                "cost_per_1k_tokens": 0.015,
                "max_output_tokens": 32768,
                "category": "reasoning",
                "speed": "slow",
                "reasoning": "exceptional",
                "capabilities": ["text", "advanced_reasoning", "mathematics", "coding"],
                "knowledge_cutoff": "2023-10"
            },
            
            # GPT-4o Series (REAL - Current models)
            "gpt-4o": {
                "context_length": 128000,
                "cost_per_1k_tokens": 0.0025,
                "max_output_tokens": 16384,
                "category": "large",
                "speed": "fast",
                "reasoning": "excellent",
                "capabilities": ["text", "vision", "function_calling", "json_mode"],
                "knowledge_cutoff": "2024-04"
            },
            "gpt-4o-2024-11-20": {
                "context_length": 128000,
                "cost_per_1k_tokens": 0.00250,
                "max_output_tokens": 16384,
                "category": "large",
                "speed": "fast",
                "reasoning": "excellent",
                "capabilities": ["text", "vision", "function_calling"],
                "knowledge_cutoff": "2024-04"
            },
            "gpt-4o-mini": {
                "context_length": 128000,
                "cost_per_1k_tokens": 0.00015,
                "max_output_tokens": 16384,
                "category": "small",
                "speed": "fastest",
                "reasoning": "good",
                "capabilities": ["text", "vision", "function_calling"],
                "knowledge_cutoff": "2024-07"
            },
            "gpt-4o-mini-2024-07-18": {
                "context_length": 128000,
                "cost_per_1k_tokens": 0.00015,
                "max_output_tokens": 16384,
                "category": "small",
                "speed": "fastest",
                "reasoning": "good",
                "capabilities": ["text", "vision", "function_calling"],
                "knowledge_cutoff": "2024-07"
            },
            
            # GPT-4 Turbo Series
            "gpt-4-turbo": {
                "context_length": 128000,
                "cost_per_1k_tokens": 0.01,
                "max_output_tokens": 4096,
                "category": "large",
                "speed": "medium",
                "reasoning": "excellent"
            },
            "gpt-4-turbo-preview": {
                "context_length": 128000,
                "cost_per_1k_tokens": 0.01,
                "max_output_tokens": 4096,
                "category": "large",
                "speed": "medium",
                "reasoning": "excellent"
            },
            "gpt-4-1106-preview": {
                "context_length": 128000,
                "cost_per_1k_tokens": 0.01,
                "max_output_tokens": 4096,
                "category": "large",
                "speed": "medium",
                "reasoning": "excellent"
            },
            "gpt-4-0613": {
                "context_length": 8192,
                "cost_per_1k_tokens": 0.03,
                "max_output_tokens": 4096,
                "category": "large",
                "speed": "slow",
                "reasoning": "excellent"
            },
            "gpt-4-0314": {
                "context_length": 8192,
                "cost_per_1k_tokens": 0.03,
                "max_output_tokens": 4096,
                "category": "large",
                "speed": "slow",
                "reasoning": "excellent"
            },
            "gpt-4": {
                "context_length": 8192,
                "cost_per_1k_tokens": 0.03,
                "max_output_tokens": 4096,
                "category": "large",
                "speed": "slow",
                "reasoning": "excellent"
            },
            
            # GPT-3.5 Turbo Series
            "gpt-3.5-turbo": {
                "context_length": 16385,
                "cost_per_1k_tokens": 0.002,
                "max_output_tokens": 4096,
                "category": "small",
                "speed": "fast",
                "reasoning": "basic"
            },
            "gpt-3.5-turbo-16k": {
                "context_length": 16385,
                "cost_per_1k_tokens": 0.004,
                "max_output_tokens": 4096,
                "category": "small",
                "speed": "fast",
                "reasoning": "basic"
            },
            "gpt-3.5-turbo-0613": {
                "context_length": 4096,
                "cost_per_1k_tokens": 0.002,
                "max_output_tokens": 4096,
                "category": "small",
                "speed": "fast",
                "reasoning": "basic"
            },
            "gpt-3.5-turbo-0301": {
                "context_length": 4096,
                "cost_per_1k_tokens": 0.002,
                "max_output_tokens": 4096,
                "category": "small",
                "speed": "fast",
                "reasoning": "basic"
            },
            
            # Legacy Models
            "text-davinci-003": {
                "context_length": 4097,
                "cost_per_1k_tokens": 0.02,
                "max_output_tokens": 4096,
                "category": "large",
                "speed": "slow",
                "reasoning": "good"
            },
            "text-curie-001": {
                "context_length": 2049,
                "cost_per_1k_tokens": 0.002,
                "max_output_tokens": 2048,
                "category": "medium",
                "speed": "medium",
                "reasoning": "basic"
            },
            "text-babbage-001": {
                "context_length": 2049,
                "cost_per_1k_tokens": 0.0005,
                "max_output_tokens": 2048,
                "category": "small",
                "speed": "fast",
                "reasoning": "basic"
            },
            "text-ada-001": {
                "context_length": 2049,
                "cost_per_1k_tokens": 0.0004,
                "max_output_tokens": 2048,
                "category": "small",
                "speed": "fastest",
                "reasoning": "basic"
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
            
            # Add function calling for newer models
            if model_id in ["gpt-4", "gpt-4-turbo", "gpt-4-turbo-preview", "gpt-4-1106-preview", 
                           "gpt-4-0613", "gpt-4-0314", "gpt-4o", "gpt-4o-mini", 
                           "gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-0613", "gpt-3.5-turbo-0301"]:
                capabilities.append(ModelCapability.FUNCTION_CALLING)
            
            # Add vision for vision-capable models
            if model_id in ["gpt-4-turbo", "gpt-4-turbo-preview", "gpt-4-1106-preview", 
                           "gpt-4-0613", "gpt-4-0314", "gpt-4", "gpt-4o", "gpt-4o-mini"]:
                capabilities.append(ModelCapability.VISION)
            
            self._models_metadata[model_id] = ModelMetadata(
                model_id=model_id,
                provider_name=self.provider_name,
                model_name=f"OpenAI {model_id}",
                capabilities=capabilities,
                context_length=config.get("context_length", 4096),
                cost_per_1k_tokens=config.get("cost_per_1k_tokens", 0.002),
                max_output_tokens=config.get("max_output_tokens", 4096),
                supports_system_messages=True,
                supports_temperature=True
            )
    
    async def initialize(self) -> bool:
        """Initialize OpenAI client"""
        try:
            if not self.api_key:
                logger.warning("OpenAI API key not provided, provider will be disabled")
                return False
            
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                organization=self.organization,
                base_url=self.base_url,
                timeout=self.timeout
            )
            
            # Test connection with a simple request
            test_response = await self.health_check()
            if test_response["status"] == "healthy":
                logger.info("OpenAI provider initialized successfully")
                return True
            else:
                logger.error(f"OpenAI provider health check failed: {test_response.get('error')}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI provider: {str(e)}")
            return False
    
    async def generate_text(self, request: GenerationRequest, model_id: str) -> GenerationResponse:
        """Generate text using OpenAI models"""
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
            logger.error(f"OpenAI generation error: {str(e)}")
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
        """Generate structured JSON output using OpenAI models"""
        if not request.output_schema:
            return GenerationResponse(
                content="",
                model_id=model_id,
                provider_name=self.provider_name,
                error="No output schema provided for structured output"
            )
        
        # Use function calling for structured output
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
        
        if response.error:
            return response
        
        try:
            # Extract function call result
            raw_response = response.raw_response
            if (raw_response and 
                raw_response.choices[0].message.tool_calls and 
                len(raw_response.choices[0].message.tool_calls) > 0):
                
                function_args = raw_response.choices[0].message.tool_calls[0].function.arguments
                # Validate JSON
                json.loads(function_args)
                response.content = function_args
            else:
                response.error = "No function call in response"
                
        except json.JSONDecodeError as e:
            response.error = f"Invalid JSON in structured output: {str(e)}"
        except Exception as e:
            response.error = f"Error processing structured output: {str(e)}"
        
        return response
    
    def get_available_models(self) -> List[ModelMetadata]:
        """Get list of available OpenAI models"""
        return list(self._models_metadata.values())
    
    async def health_check(self) -> Dict[str, Any]:
        """Check OpenAI provider health"""
        try:
            if not self.client:
                return {
                    "status": "unhealthy",
                    "error": "Client not initialized",
                    "provider": self.provider_name
                }
            
            # Test with a simple request
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            
            return {
                "status": "healthy",
                "provider": self.provider_name,
                "models_available": len(self._models_metadata),
                "test_response": response.choices[0].message.content[:50] if response.choices[0].message.content else ""
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "provider": self.provider_name
            }
    
    def get_recommended_model(self, capability: ModelCapability, complexity: str = "medium") -> Optional[str]:
        """Get recommended OpenAI model for specific use case"""
        if complexity == "simple":
            return "gpt-4o-mini"  # Fastest and cheapest
        elif complexity == "complex":
            return "gpt-4-turbo"  # Most capable
        else:
            return "gpt-4o"  # Best balance
