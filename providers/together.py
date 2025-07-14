"""
Together AI Provider for Open Source Models
Supports Llama, Mistral, Code Llama, and other open source models
"""
import asyncio
import json
import time
import os
from typing import Dict, Any, List, Optional
from together import AsyncTogether

from .base import BaseModelProvider, GenerationRequest, GenerationResponse, ModelMetadata, ModelCapability
from utils.logging_setup import get_logger

logger = get_logger(__name__)


class TogetherProvider(BaseModelProvider):
    """Together AI provider for open source models"""
    
    def __init__(self, provider_config: Dict[str, Any]):
        super().__init__(provider_config)
        self.client: Optional[AsyncTogether] = None
        self.api_key = provider_config.get("api_key") or os.getenv("TOGETHER_API_KEY")
        self.base_url = provider_config.get("base_url", "https://api.together.xyz/v1")
        self.default_temperature = provider_config.get("temperature", 0.1)
        self.timeout = provider_config.get("timeout", 60)
        
        # Load models from config
        self.model_configs = provider_config.get("models", {})
        self._setup_models_metadata()
    
    def _setup_models_metadata(self):
        """Setup metadata for all available models"""
        for model_id, config in self.model_configs.items():
            capabilities = [
                ModelCapability.TEXT_GENERATION,
                ModelCapability.STREAMING
            ]
            
            # Add structured output for newer models
            if any(x in model_id.lower() for x in ["llama-3", "mixtral", "mistral"]):
                capabilities.append(ModelCapability.STRUCTURED_OUTPUT)
            
            self._models_metadata[model_id] = ModelMetadata(
                model_id=model_id,
                provider_name=self.provider_name,
                model_name=f"Together {model_id}",
                capabilities=capabilities,
                context_length=config.get("context_length", 8192),
                cost_per_1k_tokens=config.get("cost_per_1k_tokens", 0.0002),
                max_output_tokens=config.get("max_output_tokens", 4096),
                supports_system_messages=True,
                supports_temperature=True
            )
    
    async def initialize(self) -> bool:
        """Initialize Together client"""
        try:
            if not self.api_key:
                logger.warning("Together API key not provided, provider will be disabled")
                return False
            
            self.client = AsyncTogether(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout
            )
            
            # Test connection
            test_response = await self.health_check()
            if test_response["status"] == "healthy":
                logger.info("Together provider initialized successfully")
                return True
            else:
                logger.error(f"Together provider health check failed: {test_response.get('error')}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to initialize Together provider: {str(e)}")
            return False
    
    async def generate_text(self, request: GenerationRequest, model_id: str) -> GenerationResponse:
        """Generate text using Together models"""
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
            logger.error(f"Together generation error: {str(e)}")
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
        """Generate structured JSON output using Together models"""
        if not request.output_schema:
            return GenerationResponse(
                content="",
                model_id=model_id,
                provider_name=self.provider_name,
                error="No output schema provided for structured output"
            )
        
        # Add JSON schema instruction to prompt
        schema_prompt = f"""
{request.prompt}

Please respond with valid JSON that matches this exact schema:
{json.dumps(request.output_schema, indent=2)}

Important: Respond ONLY with valid JSON, no additional text or explanations.
"""
        
        enhanced_request = GenerationRequest(
            prompt=schema_prompt,
            system_message="You are a precise JSON generator. Always respond with valid JSON that matches the given schema exactly.",
            temperature=request.temperature or 0.1,  # Lower temperature for structured output
            max_tokens=request.max_tokens,
            stop_sequences=request.stop_sequences,
            stream=False
        )
        
        response = await self.generate_text(enhanced_request, model_id)
        
        if response.error:
            return response
        
        try:
            # Try to extract JSON from response
            content = response.content.strip()
            
            # Remove markdown code blocks if present
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            content = content.strip()
            
            # Validate JSON
            json.loads(content)
            response.content = content
            
        except json.JSONDecodeError as e:
            response.error = f"Invalid JSON in structured output: {str(e)}"
        except Exception as e:
            response.error = f"Error processing structured output: {str(e)}"
        
        return response
    
    def get_available_models(self) -> List[ModelMetadata]:
        """Get list of available Together models"""
        return list(self._models_metadata.values())
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Together provider health"""
        try:
            if not self.client:
                return {
                    "status": "unhealthy",
                    "error": "Client not initialized",
                    "provider": self.provider_name
                }
            
            # Test with a simple request using a fast model
            test_model = "llama-3-8b-chat"
            if test_model not in self.model_configs:
                # Fallback to first available model
                test_model = list(self.model_configs.keys())[0] if self.model_configs else "llama-3-8b-chat"
            
            response = await self.client.chat.completions.create(
                model=test_model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            
            return {
                "status": "healthy",
                "provider": self.provider_name,
                "models_available": len(self._models_metadata),
                "test_response": response.choices[0].message.content[:50] if response.choices[0].message.content else "",
                "specialty": "open_source"
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "provider": self.provider_name
            }
    
    def get_recommended_model(self, capability: ModelCapability, complexity: str = "medium") -> Optional[str]:
        """Get recommended Together model for specific use case"""
        if complexity == "simple":
            return "llama-3-8b-chat"  # Fast and efficient
        elif complexity == "complex":
            return "llama-3-70b-chat"  # Most capable
        else:
            return "mixtral-8x22b-instruct"  # Good balance
