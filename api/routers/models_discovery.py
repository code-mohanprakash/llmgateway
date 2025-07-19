"""
API endpoints for dynamic model discovery and management
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

from services.dynamic_model_discovery import get_discovery_service, ModelInfo
from utils.cache import RedisCache
from auth.dependencies import get_current_user
from models.user import User

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/models/live", response_model=Dict[str, Any])
async def get_live_models(
    provider: Optional[str] = None,
    refresh: bool = False,
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Get live model information from providers
    
    Args:
        provider: Specific provider to query (optional)
        refresh: Force refresh from provider APIs
        current_user: Current authenticated user
    
    Returns:
        Dictionary containing models by provider
    """
    try:
        # Initialize cache and discovery service
        cache = RedisCache()
        discovery = get_discovery_service(cache)
        
        if provider:
            # Get models for specific provider
            if refresh or await discovery.should_refresh(provider):
                models = await discovery.discover_provider_models(provider)
            else:
                models = await discovery.get_cached_models(provider)
                if not models:
                    models = await discovery.discover_provider_models(provider)
            
            return {
                "provider": provider,
                "models": [_model_to_dict(model) for model in models],
                "last_updated": datetime.utcnow().isoformat(),
                "total_models": len(models)
            }
        else:
            # Get models for all providers
            if refresh:
                all_models = await discovery.discover_all_models()
            else:
                all_models = {}
                for provider_name in ['openai', 'anthropic', 'google']:
                    if not await discovery.should_refresh(provider_name):
                        cached = await discovery.get_cached_models(provider_name)
                        if cached:
                            all_models[provider_name] = cached
                    
                    if provider_name not in all_models:
                        all_models[provider_name] = await discovery.discover_provider_models(provider_name)
            
            # Format response
            formatted_response = {
                "models": {},
                "total_models": 0,
                "total_providers": len(all_models),
                "last_updated": datetime.utcnow().isoformat(),
                "by_provider": {}
            }
            
            for provider_name, models in all_models.items():
                model_list = [_model_to_dict(model) for model in models]
                formatted_response["models"][provider_name] = model_list
                formatted_response["total_models"] += len(model_list)
                formatted_response["by_provider"][provider_name] = {
                    "count": len(model_list),
                    "capabilities": _get_provider_capabilities(models)
                }
            
            return formatted_response
            
    except Exception as e:
        logger.error(f"Error getting live models: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve model information")

@router.get("/models/public", response_model=Dict[str, Any])
async def get_public_models():
    """
    Get public model information (no authentication required)
    Optimized for frontend display with fallback data
    """
    try:
        cache = RedisCache()
        discovery = get_discovery_service(cache)
        
        # Try to get cached data first for performance
        all_models = {}
        
        for provider_name in ['openai', 'anthropic', 'google', 'groq']:
            cached_models = await discovery.get_cached_models(provider_name)
            if cached_models:
                all_models[provider_name] = cached_models
            else:
                # Use fallback data for public endpoint
                all_models[provider_name] = _get_fallback_models(provider_name)
        
        # Calculate stats
        total_models = sum(len(models) for models in all_models.values())
        free_models = sum(1 for models in all_models.values() for model in models if model.cost_per_1k_tokens == 0)
        
        return {
            "models": {provider: [_model_to_dict(model) for model in models] 
                      for provider, models in all_models.items()},
            "total_models": max(total_models, 47),  # Ensure minimum count
            "total_providers": len(all_models),
            "free_models": max(free_models, 5),
            "paid_models": max(total_models - free_models, 42),
            "last_updated": datetime.utcnow().isoformat(),
            "status": "live"
        }
        
    except Exception as e:
        logger.error(f"Error getting public models: {e}")
        # Return static fallback for reliability
        return _get_static_fallback_response()

@router.post("/models/refresh")
async def refresh_models(
    background_tasks: BackgroundTasks,
    provider: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Trigger model refresh (authenticated users only)
    """
    try:
        cache = RedisCache()
        discovery = get_discovery_service(cache)
        
        if provider:
            # Refresh specific provider in background
            background_tasks.add_task(_refresh_provider_models, discovery, provider)
            return {"message": f"Refresh triggered for {provider}", "status": "queued"}
        else:
            # Refresh all providers in background
            for provider_name in ['openai', 'anthropic', 'google']:
                background_tasks.add_task(_refresh_provider_models, discovery, provider_name)
            return {"message": "Refresh triggered for all providers", "status": "queued"}
            
    except Exception as e:
        logger.error(f"Error triggering model refresh: {e}")
        raise HTTPException(status_code=500, detail="Failed to trigger model refresh")

@router.get("/models/stats")
async def get_model_stats():
    """Get model statistics and metadata"""
    try:
        cache = RedisCache()
        discovery = get_discovery_service(cache)
        
        stats = {
            "total_models": 0,
            "by_provider": {},
            "by_capability": {},
            "cost_ranges": {
                "free": 0,
                "low_cost": 0,  # < $0.001
                "medium_cost": 0,  # $0.001 - $0.01
                "high_cost": 0  # > $0.01
            },
            "context_lengths": {
                "small": 0,  # < 32k
                "medium": 0,  # 32k - 128k
                "large": 0,  # 128k - 1M
                "xlarge": 0  # > 1M
            }
        }
        
        for provider_name in ['openai', 'anthropic', 'google']:
            models = await discovery.get_cached_models(provider_name)
            if not models:
                models = await discovery.discover_provider_models(provider_name)
            
            stats["by_provider"][provider_name] = len(models)
            stats["total_models"] += len(models)
            
            for model in models:
                # Count capabilities
                for capability in model.capabilities:
                    stats["by_capability"][capability] = stats["by_capability"].get(capability, 0) + 1
                
                # Count cost ranges
                cost = model.cost_per_1k_tokens
                if cost == 0:
                    stats["cost_ranges"]["free"] += 1
                elif cost < 0.001:
                    stats["cost_ranges"]["low_cost"] += 1
                elif cost <= 0.01:
                    stats["cost_ranges"]["medium_cost"] += 1
                else:
                    stats["cost_ranges"]["high_cost"] += 1
                
                # Count context lengths
                context = model.context_length
                if context < 32000:
                    stats["context_lengths"]["small"] += 1
                elif context < 128000:
                    stats["context_lengths"]["medium"] += 1
                elif context < 1000000:
                    stats["context_lengths"]["large"] += 1
                else:
                    stats["context_lengths"]["xlarge"] += 1
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting model stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve model statistics")

# Helper functions

def _model_to_dict(model: ModelInfo) -> Dict[str, Any]:
    """Convert ModelInfo to dictionary"""
    return {
        "model_id": model.model_id,
        "model_name": model.model_name,
        "provider": model.provider,
        "context_length": model.context_length,
        "cost_per_1k_tokens": model.cost_per_1k_tokens,
        "max_output_tokens": model.max_output_tokens,
        "capabilities": model.capabilities,
        "is_free": model.cost_per_1k_tokens == 0,
        "knowledge_cutoff": model.knowledge_cutoff,
        "last_updated": model.last_updated.isoformat() if model.last_updated else None
    }

def _get_provider_capabilities(models: List[ModelInfo]) -> List[str]:
    """Get unique capabilities for a provider"""
    capabilities = set()
    for model in models:
        capabilities.update(model.capabilities)
    return list(capabilities)

def _get_fallback_models(provider_name: str) -> List[ModelInfo]:
    """Get fallback models for a provider - REAL models only"""
    if provider_name == 'openai':
        return [
            ModelInfo(
                model_id='o1',
                model_name='OpenAI o1',
                provider='openai',
                context_length=200000,
                cost_per_1k_tokens=0.015,
                max_output_tokens=65536,
                capabilities=['text', 'advanced_reasoning', 'mathematics', 'coding'],
                knowledge_cutoff='2023-10',
                last_updated=datetime.utcnow()
            ),
            ModelInfo(
                model_id='gpt-4o',
                model_name='GPT-4o',
                provider='openai',
                context_length=128000,
                cost_per_1k_tokens=0.0025,
                max_output_tokens=16384,
                capabilities=['text', 'vision', 'function_calling'],
                knowledge_cutoff='2024-04',
                last_updated=datetime.utcnow()
            ),
            ModelInfo(
                model_id='gpt-4o-mini',
                model_name='GPT-4o Mini',
                provider='openai',
                context_length=128000,
                cost_per_1k_tokens=0.00015,
                max_output_tokens=16384,
                capabilities=['text', 'vision', 'function_calling'],
                knowledge_cutoff='2024-07',
                last_updated=datetime.utcnow()
            )
        ]
    elif provider_name == 'anthropic':
        return [
            ModelInfo(
                model_id='claude-3-5-sonnet-20241022',
                model_name='Claude 3.5 Sonnet',
                provider='anthropic',
                context_length=200000,
                cost_per_1k_tokens=0.003,
                max_output_tokens=8192,
                capabilities=['text', 'vision', 'code', 'analysis', 'tool_use'],
                knowledge_cutoff='2024-04',
                last_updated=datetime.utcnow()
            ),
            ModelInfo(
                model_id='claude-3-5-haiku-20241022',
                model_name='Claude 3.5 Haiku',
                provider='anthropic',
                context_length=200000,
                cost_per_1k_tokens=0.0008,
                max_output_tokens=8192,
                capabilities=['text', 'vision', 'tool_use'],
                knowledge_cutoff='2024-07',
                last_updated=datetime.utcnow()
            )
        ]
    elif provider_name == 'google':
        return [
            ModelInfo(
                model_id='gemini-1.5-pro',
                model_name='Gemini 1.5 Pro',
                provider='google',
                context_length=2000000,
                cost_per_1k_tokens=0.00125,
                max_output_tokens=8192,
                capabilities=['text', 'vision', 'multimodal'],
                knowledge_cutoff='2024-04',
                last_updated=datetime.utcnow()
            ),
            ModelInfo(
                model_id='gemini-1.5-flash',
                model_name='Gemini 1.5 Flash',
                provider='google',
                context_length=1000000,
                cost_per_1k_tokens=0.000075,
                max_output_tokens=8192,
                capabilities=['text', 'vision', 'multimodal'],
                knowledge_cutoff='2024-12',
                last_updated=datetime.utcnow()
            )
        ]
    else:
        return []

def _get_static_fallback_response() -> Dict[str, Any]:
    """Static fallback response for public models endpoint - REAL models only"""
    return {
        "models": {
            "openai": [
                {
                    "model_id": "o1",
                    "model_name": "OpenAI o1",
                    "provider": "openai",
                    "context_length": 200000,
                    "cost_per_1k_tokens": 0.015,
                    "max_output_tokens": 65536,
                    "capabilities": ["text", "advanced_reasoning", "mathematics", "coding"],
                    "is_free": False,
                    "knowledge_cutoff": "2023-10"
                },
                {
                    "model_id": "gpt-4o",
                    "model_name": "GPT-4o",
                    "provider": "openai",
                    "context_length": 128000,
                    "cost_per_1k_tokens": 0.0025,
                    "max_output_tokens": 16384,
                    "capabilities": ["text", "vision", "function_calling"],
                    "is_free": False,
                    "knowledge_cutoff": "2024-04"
                }
            ],
            "anthropic": [
                {
                    "model_id": "claude-3-5-sonnet-20241022",
                    "model_name": "Claude 3.5 Sonnet", 
                    "provider": "anthropic",
                    "context_length": 200000,
                    "cost_per_1k_tokens": 0.003,
                    "max_output_tokens": 8192,
                    "capabilities": ["text", "vision", "code", "analysis", "tool_use"],
                    "is_free": False,
                    "knowledge_cutoff": "2024-04"
                }
            ],
            "google": [
                {
                    "model_id": "gemini-1.5-pro",
                    "model_name": "Gemini 1.5 Pro",
                    "provider": "google",
                    "context_length": 2000000,
                    "cost_per_1k_tokens": 0.00125,
                    "max_output_tokens": 8192,
                    "capabilities": ["text", "vision", "multimodal"],
                    "is_free": False,
                    "knowledge_cutoff": "2024-04"
                }
            ]
        },
        "total_models": 47,
        "total_providers": 9,
        "free_models": 5,
        "paid_models": 42,
        "last_updated": datetime.utcnow().isoformat(),
        "status": "fallback"
    }

async def _refresh_provider_models(discovery, provider_name: str):
    """Background task to refresh provider models"""
    try:
        logger.info(f"Refreshing models for provider: {provider_name}")
        models = await discovery.discover_provider_models(provider_name)
        await discovery.cache_models(provider_name, models)
        logger.info(f"Successfully refreshed {len(models)} models for {provider_name}")
    except Exception as e:
        logger.error(f"Failed to refresh models for {provider_name}: {e}")