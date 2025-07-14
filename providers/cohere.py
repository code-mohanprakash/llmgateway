"""
Cohere Provider for Command Models
Supports Command, Command-Light, Command-R, and Command-R-Plus models
"""
import asyncio
import json
import time
import os
from typing import Dict, Any, List, Optional
import cohere

from .base import BaseModelProvider, GenerationRequest, GenerationResponse, ModelMetadata, ModelCapability
from utils.logging_setup import get_logger

logger = get_logger(__name__)


class CohereProvider(BaseModelProvider):
    """Cohere provider for Command models"""
    
    def __init__(self, provider_config: Dict[str, Any]):
        super().__init__(provider_config)
        self.client: Optional[cohere.AsyncClient] = None
        self.api_key = provider_config.get("api_key") or os.getenv("COHERE_API_KEY")
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
            
            # Add structured output for R models
            if "command-r" in model_id.lower():
                capabilities.append(ModelCapability.STRUCTURED_OUTPUT)
                capabilities.append(ModelCapability.FUNCTION_CALLING)
            
            self._models_metadata[model_id] = ModelMetadata(
                model_id=model_id,
                provider_name=self.provider_name,
                model_name=f"Cohere {model_id}",
                capabilities=capabilities,
                context_length=config.get("context_length", 4096),
                cost_per_1k_tokens=config.get("cost_per_1k_tokens", 0.0015),
                max_output_tokens=config.get("max_output_tokens", 4096),
                supports_system_messages=True,
                supports_temperature=True
            )
    
    async def initialize(self) -> bool:
        """Initialize Cohere client"""
        try:
            if not self.api_key:
                logger.warning("Cohere API key not provided, provider will be disabled")
                return False
            
            self.client = cohere.AsyncClient(
                api_key=self.api_key,
                timeout=self.timeout
            )
            
            # Test connection
            test_response = await self.health_check()
            if test_response["status"] == "healthy":
                logger.info("Cohere provider initialized successfully")
                return True
            else:
                logger.error(f"Cohere provider health check failed: {test_response.get('error')}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to initialize Cohere provider: {str(e)}")
            return False
    
    async def generate_text(self, request: GenerationRequest, model_id: str) -> GenerationResponse:
        """Generate text using Cohere models"""
        start_time = time.time()
        
        try:
            if not self.client:
                return GenerationResponse(
                    content="",
                    model_id=model_id,
                    provider_name=self.provider_name,
                    error="Provider not initialized"
                )
            
            # Prepare prompt (Cohere uses different format)
            prompt = request.prompt
            if request.system_message:
                prompt = f"{request.system_message}\n\n{prompt}"
            
            # Prepare parameters
            params = {
                "model": model_id,
                "message": prompt,
                "temperature": request.temperature or self.default_temperature,
                "stream": request.stream
            }
            
            # Add max_tokens if specified
            if request.max_tokens:
                params["max_tokens"] = request.max_tokens
            
            # Add stop sequences if provided
            if request.stop_sequences:
                params["stop_sequences"] = request.stop_sequences
            
            # Make API call
            response = await self.client.chat(**params)
            
            # Extract response data
            content = response.text or ""
            
            # Cohere doesn't always provide token counts, estimate them
            prompt_tokens = len(prompt.split()) * 1.3  # Rough estimation
            completion_tokens = len(content.split()) * 1.3
            total_tokens = prompt_tokens + completion_tokens
            
            # Calculate cost
            cost = self.calculate_cost(
                int(prompt_tokens),
                int(completion_tokens),
                model_id
            )
            
            return GenerationResponse(
                content=content,
                model_id=model_id,
                provider_name=self.provider_name,
                prompt_tokens=int(prompt_tokens),
                completion_tokens=int(completion_tokens),
                total_tokens=int(total_tokens),
                cost=cost,
                response_time=time.time() - start_time,
                raw_response=response
            )
            
        except Exception as e:
            logger.error(f"Cohere generation error: {str(e)}")
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
        """Generate structured JSON output using Cohere models"""
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

Please respond with valid JSON that matches this schema:
{json.dumps(request.output_schema, indent=2)}

Important: Respond ONLY with valid JSON, no additional text or explanations.
"""
        
        enhanced_request = GenerationRequest(
            prompt=schema_prompt,
            system_message="You are a precise JSON generator. Always respond with valid JSON that matches the given schema exactly.",
            temperature=request.temperature or 0.1,
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
        """Get list of available Cohere models"""
        return list(self._models_metadata.values())
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Cohere provider health"""
        try:
            if not self.client:
                return {
                    "status": "unhealthy",
                    "error": "Client not initialized",
                    "provider": self.provider_name
                }
            
            # Test with a simple request using the light model
            test_model = "command-light"
            if test_model not in self.model_configs:
                # Fallback to first available model
                test_model = list(self.model_configs.keys())[0] if self.model_configs else "command-light"
            
            response = await self.client.chat(
                model=test_model,
                message="Hello",
                max_tokens=5
            )
            
            return {
                "status": "healthy",
                "provider": self.provider_name,
                "models_available": len(self._models_metadata),
                "test_response": response.text[:50] if response.text else "",
                "specialty": "enterprise_nlp"
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "provider": self.provider_name
            }
    
    def get_recommended_model(self, capability: ModelCapability, complexity: str = "medium") -> Optional[str]:
        """Get recommended Cohere model for specific use case"""
        if complexity == "simple":
            return "command-light"  # Fastest and cheapest
        elif complexity == "complex":
            return "command-r-plus"  # Most capable
        else:
            return "command-r"  # Good balance
