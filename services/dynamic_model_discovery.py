"""
Dynamic Model Discovery Service for LLM Gateway
Automatically discovers and updates available models from providers
"""
import asyncio
import aiohttp
import logging
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
from dataclasses import dataclass
from providers.openai import OpenAIProvider
from providers.anthropic import AnthropicProvider
from providers.google import GoogleProvider
from utils.cache import RedisCache

logger = logging.getLogger(__name__)

@dataclass
class ModelInfo:
    """Model information structure"""
    model_id: str
    model_name: str
    provider: str
    context_length: int
    cost_per_1k_tokens: float
    max_output_tokens: int
    capabilities: List[str]
    is_deprecated: bool = False
    knowledge_cutoff: Optional[str] = None
    last_updated: datetime = None

class DynamicModelDiscovery:
    """Service for discovering and updating model information from providers"""
    
    def __init__(self, cache: RedisCache):
        self.cache = cache
        self.providers = {
            'openai': OpenAIProvider,
            'anthropic': AnthropicProvider, 
            'google': GoogleProvider
        }
        self.refresh_interval = timedelta(hours=6)  # Refresh every 6 hours
        self.cache_ttl = 21600  # 6 hours in seconds
        
    async def discover_all_models(self) -> Dict[str, List[ModelInfo]]:
        """Discover models from all providers"""
        all_models = {}
        
        tasks = []
        for provider_name in self.providers.keys():
            task = self.discover_provider_models(provider_name)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for provider_name, result in zip(self.providers.keys(), results):
            if isinstance(result, Exception):
                logger.error(f"Failed to discover models for {provider_name}: {result}")
                # Fallback to cached data
                cached_models = await self.get_cached_models(provider_name)
                if cached_models:
                    all_models[provider_name] = cached_models
            else:
                all_models[provider_name] = result
                # Cache the results
                await self.cache_models(provider_name, result)
        
        return all_models
    
    async def discover_provider_models(self, provider_name: str) -> List[ModelInfo]:
        """Discover models from a specific provider"""
        try:
            if provider_name == 'openai':
                return await self._discover_openai_models()
            elif provider_name == 'anthropic':
                return await self._discover_anthropic_models()
            elif provider_name == 'google':
                return await self._discover_google_models()
            else:
                logger.warning(f"Unknown provider: {provider_name}")
                return []
        except Exception as e:
            logger.error(f"Error discovering models for {provider_name}: {e}")
            return []
    
    async def _discover_openai_models(self) -> List[ModelInfo]:
        """Discover OpenAI models via API"""
        models = []
        
        # For OpenAI, we'll use the models endpoint to get live data
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"}
                
                async with session.get(
                    "https://api.openai.com/v1/models",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Map known model metadata
                        model_metadata = self._get_openai_model_metadata()
                        
                        for model in data.get('data', []):
                            model_id = model.get('id', '')
                            if model_id in model_metadata:
                                meta = model_metadata[model_id]
                                models.append(ModelInfo(
                                    model_id=model_id,
                                    model_name=meta.get('name', model_id),
                                    provider='openai',
                                    context_length=meta.get('context_length', 4096),
                                    cost_per_1k_tokens=meta.get('cost_per_1k_tokens', 0.001),
                                    max_output_tokens=meta.get('max_output_tokens', 4096),
                                    capabilities=meta.get('capabilities', ['text']),
                                    knowledge_cutoff=meta.get('knowledge_cutoff'),
                                    last_updated=datetime.utcnow()
                                ))
                    else:
                        logger.warning(f"OpenAI API returned status {response.status}")
        except Exception as e:
            logger.error(f"Failed to fetch OpenAI models: {e}")
            # Return static fallback
            return self._get_openai_fallback_models()
        
        return models if models else self._get_openai_fallback_models()
    
    async def _discover_anthropic_models(self) -> List[ModelInfo]:
        """Discover Anthropic models"""
        # Anthropic doesn't have a public models endpoint yet
        # Return current known models with updated metadata
        return self._get_anthropic_current_models()
    
    async def _discover_google_models(self) -> List[ModelInfo]:
        """Discover Google models"""
        # Google AI Studio API for model discovery
        try:
            async with aiohttp.ClientSession() as session:
                api_key = os.getenv('GOOGLE_API_KEY')
                url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = []
                        
                        model_metadata = self._get_google_model_metadata()
                        
                        for model in data.get('models', []):
                            model_name = model.get('name', '').split('/')[-1]
                            if model_name in model_metadata:
                                meta = model_metadata[model_name]
                                models.append(ModelInfo(
                                    model_id=model_name,
                                    model_name=meta.get('display_name', model_name),
                                    provider='google',
                                    context_length=meta.get('context_length', 32768),
                                    cost_per_1k_tokens=meta.get('cost_per_1k_tokens', 0.001),
                                    max_output_tokens=meta.get('max_output_tokens', 8192),
                                    capabilities=meta.get('capabilities', ['text']),
                                    knowledge_cutoff=meta.get('knowledge_cutoff'),
                                    last_updated=datetime.utcnow()
                                ))
                        return models
        except Exception as e:
            logger.error(f"Failed to fetch Google models: {e}")
        
        return self._get_google_current_models()
    
    def _get_openai_model_metadata(self) -> Dict[str, Any]:
        """Get OpenAI model metadata mapping"""
        return {
            'gpt-4.1': {
                'name': 'GPT-4.1',
                'context_length': 200000,
                'cost_per_1k_tokens': 0.012,
                'max_output_tokens': 8192,
                'capabilities': ['text', 'vision', 'function_calling', 'json_mode'],
                'knowledge_cutoff': '2024-12'
            },
            'gpt-4.1-mini': {
                'name': 'GPT-4.1 Mini',
                'context_length': 128000,
                'cost_per_1k_tokens': 0.0001,
                'max_output_tokens': 16384,
                'capabilities': ['text', 'vision', 'function_calling', 'json_mode'],
                'knowledge_cutoff': '2024-12'
            },
            'o3': {
                'name': 'OpenAI o3',
                'context_length': 128000,
                'cost_per_1k_tokens': 0.06,
                'max_output_tokens': 65536,
                'capabilities': ['text', 'advanced_reasoning', 'mathematics', 'coding'],
                'knowledge_cutoff': '2024-12'
            },
            'o4-mini': {
                'name': 'OpenAI o4 Mini',
                'context_length': 128000,
                'cost_per_1k_tokens': 0.003,
                'max_output_tokens': 65536,
                'capabilities': ['text', 'reasoning', 'mathematics', 'coding'],
                'knowledge_cutoff': '2024-12'
            },
            'gpt-4o': {
                'name': 'GPT-4o',
                'context_length': 128000,
                'cost_per_1k_tokens': 0.015,
                'max_output_tokens': 4096,
                'capabilities': ['text', 'vision', 'function_calling'],
                'knowledge_cutoff': '2024-04'
            }
        }
    
    def _get_openai_fallback_models(self) -> List[ModelInfo]:
        """Fallback OpenAI models when API is unavailable"""
        metadata = self._get_openai_model_metadata()
        models = []
        
        for model_id, meta in metadata.items():
            models.append(ModelInfo(
                model_id=model_id,
                model_name=meta['name'],
                provider='openai',
                context_length=meta['context_length'],
                cost_per_1k_tokens=meta['cost_per_1k_tokens'],
                max_output_tokens=meta['max_output_tokens'],
                capabilities=meta['capabilities'],
                knowledge_cutoff=meta.get('knowledge_cutoff'),
                last_updated=datetime.utcnow()
            ))
        
        return models
    
    def _get_anthropic_current_models(self) -> List[ModelInfo]:
        """Get current Anthropic models"""
        return [
            ModelInfo(
                model_id='claude-4-opus',
                model_name='Claude 4 Opus',
                provider='anthropic',
                context_length=500000,
                cost_per_1k_tokens=0.008,
                max_output_tokens=16384,
                capabilities=['text', 'vision', 'code', 'analysis', 'tool_use'],
                knowledge_cutoff='2024-12',
                last_updated=datetime.utcnow()
            ),
            ModelInfo(
                model_id='claude-4-sonnet',
                model_name='Claude 4 Sonnet',
                provider='anthropic',
                context_length=400000,
                cost_per_1k_tokens=0.0025,
                max_output_tokens=8192,
                capabilities=['text', 'vision', 'code', 'analysis', 'tool_use'],
                knowledge_cutoff='2024-12',
                last_updated=datetime.utcnow()
            ),
            ModelInfo(
                model_id='claude-4-haiku',
                model_name='Claude 4 Haiku',
                provider='anthropic',
                context_length=200000,
                cost_per_1k_tokens=0.0003,
                max_output_tokens=4096,
                capabilities=['text', 'vision', 'code', 'tool_use'],
                knowledge_cutoff='2024-12',
                last_updated=datetime.utcnow()
            )
        ]
    
    def _get_google_model_metadata(self) -> Dict[str, Any]:
        """Get Google model metadata mapping"""
        return {
            'gemini-2.0-flash-exp': {
                'display_name': 'Gemini 2.0 Flash Experimental',
                'context_length': 2000000,
                'cost_per_1k_tokens': 0.002,
                'max_output_tokens': 8192,
                'capabilities': ['text', 'vision', 'multimodal', 'function_calling'],
                'knowledge_cutoff': '2024-12'
            },
            'gemini-2.0-pro-exp': {
                'display_name': 'Gemini 2.0 Pro Experimental',
                'context_length': 2000000,
                'cost_per_1k_tokens': 0.004,
                'max_output_tokens': 16384,
                'capabilities': ['text', 'vision', 'multimodal', 'reasoning', 'function_calling'],
                'knowledge_cutoff': '2024-12'
            },
            'gemini-1.5-pro': {
                'display_name': 'Gemini 1.5 Pro',
                'context_length': 2000000,
                'cost_per_1k_tokens': 0.0035,
                'max_output_tokens': 8192,
                'capabilities': ['text', 'vision', 'function_calling'],
                'knowledge_cutoff': '2024-04'
            }
        }
    
    def _get_google_current_models(self) -> List[ModelInfo]:
        """Get current Google models"""
        metadata = self._get_google_model_metadata()
        models = []
        
        for model_id, meta in metadata.items():
            models.append(ModelInfo(
                model_id=model_id,
                model_name=meta['display_name'],
                provider='google',
                context_length=meta['context_length'],
                cost_per_1k_tokens=meta['cost_per_1k_tokens'],
                max_output_tokens=meta['max_output_tokens'],
                capabilities=meta['capabilities'],
                knowledge_cutoff=meta.get('knowledge_cutoff'),
                last_updated=datetime.utcnow()
            ))
        
        return models
    
    async def cache_models(self, provider_name: str, models: List[ModelInfo]):
        """Cache discovered models"""
        try:
            cache_key = f"models:{provider_name}"
            model_data = []
            
            for model in models:
                model_data.append({
                    'model_id': model.model_id,
                    'model_name': model.model_name,
                    'provider': model.provider,
                    'context_length': model.context_length,
                    'cost_per_1k_tokens': model.cost_per_1k_tokens,
                    'max_output_tokens': model.max_output_tokens,
                    'capabilities': model.capabilities,
                    'knowledge_cutoff': model.knowledge_cutoff,
                    'last_updated': model.last_updated.isoformat() if model.last_updated else None
                })
            
            await self.cache.set(cache_key, json.dumps(model_data), ttl=self.cache_ttl)
        except Exception as e:
            logger.error(f"Failed to cache models for {provider_name}: {e}")
    
    async def get_cached_models(self, provider_name: str) -> Optional[List[ModelInfo]]:
        """Get cached models for a provider"""
        try:
            cache_key = f"models:{provider_name}"
            cached_data = await self.cache.get(cache_key)
            
            if cached_data:
                model_data = json.loads(cached_data)
                models = []
                
                for data in model_data:
                    last_updated = None
                    if data.get('last_updated'):
                        last_updated = datetime.fromisoformat(data['last_updated'])
                    
                    models.append(ModelInfo(
                        model_id=data['model_id'],
                        model_name=data['model_name'],
                        provider=data['provider'],
                        context_length=data['context_length'],
                        cost_per_1k_tokens=data['cost_per_1k_tokens'],
                        max_output_tokens=data['max_output_tokens'],
                        capabilities=data['capabilities'],
                        knowledge_cutoff=data.get('knowledge_cutoff'),
                        last_updated=last_updated
                    ))
                
                return models
        except Exception as e:
            logger.error(f"Failed to get cached models for {provider_name}: {e}")
        
        return None
    
    async def should_refresh(self, provider_name: str) -> bool:
        """Check if models should be refreshed for a provider"""
        cached_models = await self.get_cached_models(provider_name)
        
        if not cached_models:
            return True
        
        # Check if any model is older than refresh interval
        for model in cached_models:
            if not model.last_updated:
                return True
            
            age = datetime.utcnow() - model.last_updated
            if age > self.refresh_interval:
                return True
        
        return False

# Global discovery service instance
discovery_service = None

def get_discovery_service(cache: RedisCache) -> DynamicModelDiscovery:
    """Get or create the global discovery service instance"""
    global discovery_service
    if discovery_service is None:
        discovery_service = DynamicModelDiscovery(cache)
    return discovery_service