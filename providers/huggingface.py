"""
Hugging Face Provider for Inference API
Supports thousands of models through Hugging Face Inference API
"""
import asyncio
import json
import time
import os
from typing import Dict, Any, List, Optional
import httpx

from .base import BaseModelProvider, GenerationRequest, GenerationResponse, ModelMetadata, ModelCapability
from utils.logging_setup import get_logger

logger = get_logger(__name__)


class HuggingFaceProvider(BaseModelProvider):
    """Hugging Face provider for Inference API"""
    
    def __init__(self, provider_config: Dict[str, Any]):
        super().__init__(provider_config)
        self.client: Optional[httpx.AsyncClient] = None
        self.api_key = provider_config.get("api_key") or os.getenv("HUGGINGFACE_API_KEY")
        self.base_url = provider_config.get("base_url", "https://api-inference.huggingface.co")
        self.default_temperature = provider_config.get("temperature", 0.1)
        self.timeout = provider_config.get("timeout", 60)
        
        # Load models from config with defaults
        self.model_configs = provider_config.get("models", self._get_default_models())
        self._setup_models_metadata()
    
    def _get_default_models(self) -> Dict[str, Any]:
        """Get default Hugging Face model configurations"""
        return {
            "microsoft/DialoGPT-medium": {
                "context_length": 1024,
                "cost_per_1k_tokens": 0.0,
                "max_output_tokens": 512
            },
            "google/flan-t5-base": {
                "context_length": 512,
                "cost_per_1k_tokens": 0.0,
                "max_output_tokens": 256
            },
            "facebook/blenderbot-400M-distill": {
                "context_length": 128,
                "cost_per_1k_tokens": 0.0,
                "max_output_tokens": 128
            }
        }
    
    def _setup_models_metadata(self):
        """Setup metadata for all available models"""
        for model_id, config in self.model_configs.items():
            capabilities = [
                ModelCapability.TEXT_GENERATION
            ]
            
            # Add capabilities based on model type
            if "llama" in model_id.lower() or "mistral" in model_id.lower():
                capabilities.append(ModelCapability.STRUCTURED_OUTPUT)
                capabilities.append(ModelCapability.STREAMING)
            
            self._models_metadata[model_id] = ModelMetadata(
                model_id=model_id,
                provider_name=self.provider_name,
                model_name=f"HF {model_id.split('/')[-1]}",
                capabilities=capabilities,
                context_length=config.get("context_length", 2048),
                cost_per_1k_tokens=config.get("cost_per_1k_tokens", 0.0001),
                max_output_tokens=config.get("max_output_tokens", 1024),
                supports_system_messages=True,
                supports_temperature=True
            )
    
    async def initialize(self) -> bool:
        """Initialize Hugging Face client"""
        try:
            if not self.api_key:
                logger.warning("Hugging Face API key not provided, provider will be disabled")
                return False
            
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=self.timeout
            )
            
            # Simple validation - just check if client was created
            if self.client and self.model_configs:
                logger.info("Hugging Face provider initialized successfully")
                return True
            else:
                logger.error("Hugging Face provider initialization failed - no models configured")
                return False
            
        except Exception as e:
            logger.error(f"Failed to initialize Hugging Face provider: {str(e)}")
            return False
    
    async def generate_text(self, request: GenerationRequest, model_id: str) -> GenerationResponse:
        """Generate text using Hugging Face models"""
        start_time = time.time()
        
        try:
            if not self.client:
                return GenerationResponse(
                    content="",
                    model_id=model_id,
                    provider_name=self.provider_name,
                    error="Provider not initialized"
                )
            
            # Prepare prompt
            prompt = request.prompt
            if request.system_message:
                prompt = f"System: {request.system_message}\n\nUser: {prompt}\n\nAssistant:"
            
            # Prepare parameters
            params = {
                "temperature": request.temperature or self.default_temperature,
                "max_new_tokens": request.max_tokens or 512,
                "stream": request.stream
            }
            
            # Add stop sequences if provided
            if request.stop_sequences:
                params["stop_sequences"] = request.stop_sequences
            
            # Make API call using httpx directly
            try:
                payload = {
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": params.get("max_new_tokens", 50),
                        "temperature": params.get("temperature", 0.1),
                        "return_full_text": False
                    }
                }
                
                response = await self.client.post(
                    f"/{model_id}",
                    json=payload
                )
                
                if response.status_code != 200:
                    error_msg = f"HF API error {response.status_code}: {response.text}"
                    logger.error(error_msg)
                    return GenerationResponse(
                        content="",
                        model_id=model_id,
                        provider_name=self.provider_name,
                        error=error_msg
                    )
                
                result = response.json()
                
                # Extract content from response
                if isinstance(result, list) and len(result) > 0:
                    if isinstance(result[0], dict) and 'generated_text' in result[0]:
                        content = result[0]['generated_text']
                    else:
                        content = str(result[0])
                elif isinstance(result, dict) and 'generated_text' in result:
                    content = result['generated_text']
                else:
                    content = str(result)
                    
            except Exception as api_error:
                logger.error(f"HuggingFace API call failed: {str(api_error)}")
                return GenerationResponse(
                    content="",
                    model_id=model_id,
                    provider_name=self.provider_name,
                    error=f"API call failed: {str(api_error)}"
                )
            
            # Estimate token counts (HF doesn't always provide them)
            prompt_tokens = len(prompt.split()) * 1.3
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
                raw_response=content
            )
            
        except Exception as e:
            logger.error(f"Hugging Face generation error: {str(e)}")
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
        """Generate structured JSON output using Hugging Face models"""
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
        """Get list of available Hugging Face models"""
        return list(self._models_metadata.values())
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Hugging Face provider health"""
        try:
            if not self.client:
                return {
                    "status": "unhealthy",
                    "error": "Client not initialized",
                    "provider": self.provider_name
                }
            
            # Test with a simple request using a fast model
            test_model = "microsoft/DialoGPT-medium"
            if test_model not in self.model_configs:
                # Fallback to first available model
                test_model = list(self.model_configs.keys())[0] if self.model_configs else "microsoft/DialoGPT-medium"
            
            # Simple health check - just ping the API
            payload = {
                "inputs": "Hello",
                "parameters": {
                    "max_new_tokens": 5,
                    "temperature": 0.1
                }
            }
            
            response = await self.client.post(
                f"/{test_model}",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                content = "API responding"
                if isinstance(result, list) and len(result) > 0:
                    if isinstance(result[0], dict) and 'generated_text' in result[0]:
                        content = result[0]['generated_text'][:50]
            else:
                content = f"API error {response.status_code}"
            
            return {
                "status": "healthy",
                "provider": self.provider_name,
                "models_available": len(self._models_metadata),
                "test_response": content[:50],
                "specialty": "open_source_hub"
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "provider": self.provider_name
            }
    
    def get_recommended_model(self, capability: ModelCapability, complexity: str = "medium") -> Optional[str]:
        """Get recommended Hugging Face model for specific use case"""
        if complexity == "simple":
            return "microsoft/DialoGPT-medium"  # Fast
        elif complexity == "complex":
            return "meta-llama/Llama-2-70b-chat-hf"  # Most capable
        else:
            return "microsoft/DialoGPT-large"  # Good balance
