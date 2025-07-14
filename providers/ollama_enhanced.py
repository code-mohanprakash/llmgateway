"""
Enhanced Ollama Provider for Local Models
Supports Llama, Mistral, Qwen, DeepSeek, CodeLlama, and many more local models
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


class OllamaEnhancedProvider(BaseModelProvider):
    """Enhanced Ollama provider for comprehensive local model support"""
    
    def __init__(self, provider_config: Dict[str, Any]):
        super().__init__(provider_config)
        self.client: Optional[httpx.AsyncClient] = None
        self.base_url = provider_config.get("base_url", "http://localhost:11434")
        self.auto_pull = provider_config.get("auto_pull", True)
        self.default_temperature = provider_config.get("temperature", 0.1)
        self.timeout = provider_config.get("timeout", 120)  # Longer timeout for local models
        
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
            
            # Add structured output for most models
            capabilities.append(ModelCapability.STRUCTURED_OUTPUT)
            
            # Add special capabilities based on model type
            if "code" in model_id.lower():
                capabilities.append(ModelCapability.FUNCTION_CALLING)
            
            # Determine specialty
            specialty = None
            if "code" in model_id.lower():
                specialty = "coding"
            elif "deepseek" in model_id.lower():
                specialty = "reasoning"
            elif "qwen" in model_id.lower():
                specialty = "multilingual"
            
            self._models_metadata[model_id] = ModelMetadata(
                model_id=model_id,
                provider_name=self.provider_name,
                model_name=f"Ollama {model_id}",
                capabilities=capabilities,
                context_length=config.get("context_length", 8192),
                cost_per_1k_tokens=0.0,  # Local models are free
                max_output_tokens=config.get("max_output_tokens", 4096),
                supports_system_messages=True,
                supports_temperature=True
            )
    
    async def initialize(self) -> bool:
        """Initialize Ollama client"""
        try:
            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout
            )
            
            # Test connection
            test_response = await self.health_check()
            if test_response["status"] == "healthy":
                logger.info("Enhanced Ollama provider initialized successfully")
                
                # Auto-pull missing models if enabled
                if self.auto_pull:
                    await self._auto_pull_models()
                
                return True
            else:
                logger.error(f"Enhanced Ollama provider health check failed: {test_response.get('error')}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to initialize Enhanced Ollama provider: {str(e)}")
            return False
    
    async def _auto_pull_models(self):
        """Automatically pull missing models"""
        try:
            # Get list of available models
            response = await self.client.get("/api/tags")
            if response.status_code == 200:
                available_models = {model["name"] for model in response.json().get("models", [])}
                
                # Pull missing models
                for model_id in self.model_configs.keys():
                    if model_id not in available_models:
                        logger.info(f"Auto-pulling missing model: {model_id}")
                        await self._pull_model(model_id)
            
        except Exception as e:
            logger.warning(f"Failed to auto-pull models: {str(e)}")
    
    async def _pull_model(self, model_id: str):
        """Pull a specific model"""
        try:
            response = await self.client.post("/api/pull", json={"name": model_id})
            if response.status_code == 200:
                logger.info(f"Successfully pulled model: {model_id}")
            else:
                logger.warning(f"Failed to pull model {model_id}: {response.text}")
        except Exception as e:
            logger.warning(f"Error pulling model {model_id}: {str(e)}")
    
    async def generate_text(self, request: GenerationRequest, model_id: str) -> GenerationResponse:
        """Generate text using Ollama models"""
        start_time = time.time()
        
        try:
            if not self.client:
                return GenerationResponse(
                    content="",
                    model_id=model_id,
                    provider_name=self.provider_name,
                    error="Provider not initialized"
                )
            
            # Prepare prompt with system message
            prompt = request.prompt
            if request.system_message:
                prompt = f"System: {request.system_message}\n\nUser: {prompt}\n\nAssistant:"
            
            # Prepare parameters
            params = {
                "model": model_id,
                "prompt": prompt,
                "stream": request.stream,
                "options": {
                    "temperature": request.temperature or self.default_temperature,
                }
            }
            
            # Add max_tokens if specified
            if request.max_tokens:
                params["options"]["num_predict"] = request.max_tokens
            
            # Add stop sequences if provided
            if request.stop_sequences:
                params["options"]["stop"] = request.stop_sequences
            
            # Add extra parameters
            if request.extra_params:
                params["options"].update(request.extra_params)
            
            # Make API call
            if request.stream:
                # Handle streaming
                content = ""
                async with self.client.stream("POST", "/api/generate", json=params) as response:
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                chunk = json.loads(line)
                                if "response" in chunk:
                                    content += chunk["response"]
                                if chunk.get("done", False):
                                    break
                            except json.JSONDecodeError:
                                continue
            else:
                # Handle non-streaming
                response = await self.client.post("/api/generate", json=params)
                response.raise_for_status()
                
                response_data = response.json()
                content = response_data.get("response", "")
            
            # Estimate token counts (Ollama doesn't provide them)
            prompt_tokens = len(prompt.split()) * 1.3
            completion_tokens = len(content.split()) * 1.3
            total_tokens = prompt_tokens + completion_tokens
            
            return GenerationResponse(
                content=content,
                model_id=model_id,
                provider_name=self.provider_name,
                prompt_tokens=int(prompt_tokens),
                completion_tokens=int(completion_tokens),
                total_tokens=int(total_tokens),
                cost=0.0,  # Local models are free
                response_time=time.time() - start_time,
                raw_response=content
            )
            
        except Exception as e:
            logger.error(f"Enhanced Ollama generation error: {str(e)}")
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
        """Generate structured JSON output using Ollama models"""
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
        """Get list of available Ollama models"""
        return list(self._models_metadata.values())
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Ollama provider health"""
        try:
            if not self.client:
                return {
                    "status": "unhealthy",
                    "error": "Client not initialized",
                    "provider": self.provider_name
                }
            
            # Test Ollama server connection
            response = await self.client.get("/api/tags")
            if response.status_code == 200:
                models_data = response.json()
                available_models = len(models_data.get("models", []))
                
                return {
                    "status": "healthy",
                    "provider": self.provider_name,
                    "models_available": available_models,
                    "configured_models": len(self._models_metadata),
                    "specialty": "local_inference",
                    "cost": "free"
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": f"Ollama server returned status {response.status_code}",
                    "provider": self.provider_name
                }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "provider": self.provider_name
            }
    
    def get_recommended_model(self, capability: ModelCapability, complexity: str = "medium") -> Optional[str]:
        """Get recommended Ollama model for specific use case"""
        if complexity == "simple":
            return "llama3:8b"  # Fast and efficient
        elif complexity == "complex":
            return "llama3:70b"  # Most capable
        else:
            return "llama3:13b"  # Good balance
    
    async def list_available_models(self) -> List[str]:
        """List all models available on the Ollama server"""
        try:
            if not self.client:
                return []
            
            response = await self.client.get("/api/tags")
            if response.status_code == 200:
                models_data = response.json()
                return [model["name"] for model in models_data.get("models", [])]
            else:
                return []
                
        except Exception as e:
            logger.error(f"Failed to list Ollama models: {str(e)}")
            return []
