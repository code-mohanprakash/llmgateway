"""
Anthropic Claude Provider for Unified LLM Gateway
Handles Claude-3 models (Haiku, Sonnet, Opus)
"""
import os
import time
import json
from typing import Dict, Any, List, Optional
import aiohttp

from .base import (
    BaseModelProvider, 
    GenerationRequest, 
    GenerationResponse, 
    ModelMetadata, 
    ModelCapability
)
from utils.logging_setup import get_logger

logger = get_logger(__name__)


class AnthropicProvider(BaseModelProvider):
    """Anthropic Claude provider implementation"""
    
    def __init__(self, provider_config: Dict[str, Any]):
        self.provider_name = "anthropic"
        self.provider_config = provider_config
        self.api_key = provider_config.get("api_key") or os.getenv("ANTHROPIC_API_KEY")
        self.base_url = "https://api.anthropic.com/v1/messages"
        self._initialized = False
        self._models_metadata = {}
    
    async def initialize(self) -> bool:
        """Initialize Anthropic provider"""
        try:
            if not self.api_key:
                logger.error("Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable.")
                return False
            
            # Define available Claude models
            self._models_metadata = {
                "claude-3-haiku": ModelMetadata(
                    model_id="claude-3-haiku",
                    model_name="claude-3-haiku-20240307",
                    provider_name=self.provider_name,
                    capabilities=[
                        ModelCapability.TEXT_GENERATION,
                        ModelCapability.STRUCTURED_OUTPUT
                    ],
                    context_length=200000,
                    cost_per_1k_tokens=0.00025,  # Very cheap
                    max_output_tokens=4096,
                    supports_system_messages=True,
                    supports_temperature=True
                ),
                "claude-3-sonnet": ModelMetadata(
                    model_id="claude-3-sonnet",
                    model_name="claude-3-sonnet-20240229",
                    provider_name=self.provider_name,
                    capabilities=[
                        ModelCapability.TEXT_GENERATION,
                        ModelCapability.STRUCTURED_OUTPUT,
                        ModelCapability.CODE_GENERATION
                    ],
                    context_length=200000,
                    cost_per_1k_tokens=0.003,  # Balanced
                    max_output_tokens=4096,
                    supports_system_messages=True,
                    supports_temperature=True
                ),
                "claude-3-opus": ModelMetadata(
                    model_id="claude-3-opus",
                    model_name="claude-3-opus-20240229",
                    provider_name=self.provider_name,
                    capabilities=[
                        ModelCapability.TEXT_GENERATION,
                        ModelCapability.STRUCTURED_OUTPUT,
                        ModelCapability.CODE_GENERATION,
                        ModelCapability.FUNCTION_CALLING
                    ],
                    context_length=200000,
                    cost_per_1k_tokens=0.015,  # Most powerful
                    max_output_tokens=4096,
                    supports_system_messages=True,
                    supports_temperature=True
                )
            }
            
            self._initialized = True
            logger.info(f"Anthropic provider initialized with {len(self._models_metadata)} models")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic provider: {str(e)}")
            return False
    
    async def generate_text(self, request: GenerationRequest, model_id: str) -> GenerationResponse:
        """Generate text using Claude"""
        start_time = time.time()
        
        try:
            if not self._initialized:
                await self.initialize()
            
            if model_id not in self._models_metadata:
                return GenerationResponse(
                    content="",
                    model_id=model_id,
                    provider_name=self.provider_name,
                    error=f"Model {model_id} not available"
                )
            
            # Prepare messages for Claude API
            messages = [{"role": "user", "content": request.prompt}]
            
            payload = {
                "model": self._models_metadata[model_id].model_name,
                "max_tokens": request.max_tokens or 4096,
                "messages": messages,
                "temperature": request.temperature or 0.1
            }
            
            if request.system_message:
                payload["system"] = request.system_message
            
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            # Make request to Claude API
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data.get("content", [{}])[0].get("text", "")
                        
                        response_time = time.time() - start_time
                        
                        # Estimate tokens
                        prompt_tokens = self._estimate_tokens(request.prompt + (request.system_message or ""))
                        completion_tokens = self._estimate_tokens(content)
                        
                        # Calculate cost
                        cost = self.calculate_cost(prompt_tokens, completion_tokens, model_id)
                        
                        return GenerationResponse(
                            content=content,
                            model_id=model_id,
                            provider_name=self.provider_name,
                            prompt_tokens=prompt_tokens,
                            completion_tokens=completion_tokens,
                            total_tokens=prompt_tokens + completion_tokens,
                            cost=cost,
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
                            error=f"Claude API error: {error_text}"
                        )
                        
        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"Claude text generation failed: {str(e)}")
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
        """Generate structured JSON output using Claude"""
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
            
            Please respond with valid JSON that matches this exact schema:
            {schema_str}
            
            Return only the JSON response, no additional text.
            """
            
            # Create new request with structured prompt
            structured_request = GenerationRequest(
                prompt=structured_prompt,
                system_message=request.system_message,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
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
            logger.error(f"Claude structured output failed: {str(e)}")
            return GenerationResponse(
                content="",
                model_id=model_id,
                provider_name=self.provider_name,
                error=str(e)
            )
    
    def get_available_models(self) -> List[ModelMetadata]:
        """Get list of available Claude models"""
        return list(self._models_metadata.values())
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Anthropic provider health"""
        try:
            # Simple test request
            test_request = GenerationRequest(
                prompt="Say 'OK' if you can hear me.",
                temperature=0.1,
                max_tokens=10
            )
            
            response = await self.generate_text(test_request, "claude-3-haiku")
            
            return {
                "provider": self.provider_name,
                "status": "healthy" if response.is_success() else "unhealthy",
                "available_models": len(self._models_metadata),
                "initialized": self._initialized,
                "test_response": response.content if response.is_success() else response.error,
                "response_time": response.response_time
            }
            
        except Exception as e:
            return {
                "provider": self.provider_name,
                "status": "unhealthy",
                "error": str(e),
                "initialized": self._initialized
            }
    
    def get_recommended_model(self, capability: ModelCapability, complexity: str = "medium") -> Optional[str]:
        """Get recommended Claude model based on capability and complexity"""
        if complexity == "simple":
            return "claude-3-haiku"   # Fastest and cheapest
        elif complexity == "complex":
            return "claude-3-opus"    # Most capable
        else:
            return "claude-3-sonnet"  # Balanced option
    
    def _estimate_tokens(self, text: str) -> int:
        """Rough estimation of token count (4 chars per token average)"""
        return max(1, len(text) // 4)