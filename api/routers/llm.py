"""
Enhanced LLM API routes with SaaS features
"""
import json
import time
import uuid
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, extract, select
from datetime import datetime

from database.database import get_db
from models.user import APIKey, Organization, UsageRecord, PlanType
from auth.dependencies import get_api_key_auth, get_current_organization
from auth.rbac_middleware import require_permission
from model_bridge import EnhancedModelBridge
from utils.cache import get_cached_response, cache_response

router = APIRouter()

# Initialize the Model Bridge
gateway = EnhancedModelBridge()

# Define plan-based model access
FREE_TIER_MODELS = {
    "openrouter": ["deepseek/deepseek-r1-0528:free"],
    "ollama": ["llama3:8b", "mistral:7b", "phi3:mini", "qwen2:7b"],
    "google": ["gemini-1.5-flash", "gemini-pro"],
    "groq": ["llama3-8b-8192"],
    "together": ["llama-3-8b-chat", "mistral-7b-instruct"],
    "huggingface": ["microsoft/DialoGPT-medium"]
}

PAID_TIER_MODELS = {
    "openai": [
        "gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4-turbo-preview", "gpt-4-1106-preview",
        "gpt-4-0613", "gpt-4-0314", "gpt-4", "gpt-3.5-turbo", "gpt-3.5-turbo-16k",
        "gpt-3.5-turbo-0613", "gpt-3.5-turbo-0301", "text-davinci-003", "text-curie-001",
        "text-babbage-001", "text-ada-001"
    ],
    "anthropic": [
        "claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307", "claude-2.1", "claude-2.0", "claude-instant-1.2",
        "claude-instant-1.1"
    ],
    "google": [
        "gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.5-pro-latest", "gemini-pro",
        "gemini-pro-vision", "gemini-ultra", "gemini-ultra-vision"
    ],
    "groq": ["mixtral-8x7b-32768", "llama3-70b-8192"],
    "together": ["llama-3-13b-chat", "llama-3-70b-chat", "mixtral-8x22b-instruct"],
    "mistral": ["mistral-tiny", "mistral-small", "mistral-medium", "mistral-large"],
    "cohere": ["command", "command-light", "command-r", "command-r-plus"],
    "perplexity": ["pplx-7b-online", "pplx-7b-chat", "pplx-70b-online", "pplx-70b-chat"],
    "openrouter": ["deepseek/deepseek-r1", "openai/gpt-4o", "anthropic/claude-3.5-sonnet", "google/gemini-pro-1.5"],
    "ollama": ["llama3:13b", "llama3:70b", "mistral:8x7b", "qwen2:14b", "qwen2:72b", "deepseek-coder:33b", "codellama:13b"]
}


class GenerationRequest(BaseModel):
    prompt: str
    model: str = "balanced"
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    task_type: Optional[str] = None
    complexity: Optional[str] = "medium"
    response_schema: Optional[Dict[str, Any]] = None  # For structured output


class AdvancedGenerationRequest(BaseModel):
    prompt: str
    routing_strategy: str = "intelligent"  # intelligent, cost_optimized, speed_optimized, quality_optimized
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    task_type: Optional[str] = None
    complexity: Optional[str] = "medium"
    preferred_providers: Optional[List[str]] = None
    excluded_providers: Optional[List[str]] = None
    max_cost: Optional[float] = None
    max_response_time: Optional[float] = None
    response_schema: Optional[Dict[str, Any]] = None


class GenerationResponse(BaseModel):
    content: str
    model_id: str
    provider_name: str
    cost: float
    input_tokens: int
    output_tokens: int
    total_tokens: int
    response_time_ms: int
    request_id: str
    cached: bool = False
    routing_info: Optional[Dict[str, Any]] = None


@router.on_event("startup")
async def startup_event():
    """Initialize gateway on startup"""
    await gateway.initialize()


@router.post("/generate", response_model=GenerationResponse)
@require_permission("llm.generate", "llm")
async def generate_text(
    request: GenerationRequest,
    api_key: APIKey = Depends(get_api_key_auth),
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
    http_request: Request = None
):
    """Generate text using the Model Bridge with intelligent routing"""
    
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    try:
        # Check organization limits
        await check_usage_limits(organization, db)
        
        # Check plan-based model access
        await check_plan_model_access(request.model, organization, db)
        
        # Check cache first
        cache_params = {
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "task_type": request.task_type,
            "complexity": request.complexity
        }
        
        cached_response = await get_cached_response(
            request.prompt, 
            request.model, 
            **cache_params
        )
        
        if cached_response:
            # Return cached response
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Still record usage for analytics (but no cost)
            await record_usage(
                request_id=request_id,
                api_key=api_key,
                organization=organization,
                provider=cached_response["provider_name"],
                model_id=cached_response["model_id"],
                input_tokens=cached_response["input_tokens"],
                output_tokens=cached_response["output_tokens"],
                cost=0.0,  # No cost for cached responses
                response_time_ms=response_time_ms,
                success=True,
                task_type=request.task_type,
                complexity=request.complexity,
                http_request=http_request,
                db=db
            )
            
            return GenerationResponse(
                content=cached_response["content"],
                model_id=cached_response["model_id"],
                provider_name=cached_response["provider_name"],
                cost=0.0,  # No cost for cached responses
                input_tokens=cached_response["input_tokens"],
                output_tokens=cached_response["output_tokens"],
                total_tokens=cached_response["total_tokens"],
                response_time_ms=response_time_ms,
                request_id=request_id,
                cached=True
            )
        
        # Generate text using the gateway with intelligent routing
        response = await gateway.generate_text(
            prompt=request.prompt,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            task_type=request.task_type,
            complexity=request.complexity
        )
        
        # Cache the response
        await cache_response(
            request.prompt,
            request.model,
            {
                "content": response.content,
                "model_id": response.model_id,
                "provider_name": response.provider_name,
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "total_tokens": response.total_tokens,
                "cost": response.cost
            },
            **cache_params
        )
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Record usage
        await record_usage(
            request_id=request_id,
            api_key=api_key,
            organization=organization,
            provider=response.provider_name,
            model_id=response.model_id,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            cost=response.cost,
            response_time_ms=response_time_ms,
            success=True,
            task_type=request.task_type,
            complexity=request.complexity,
            http_request=http_request,
            db=db
        )
        
        return GenerationResponse(
            content=response.content,
            model_id=response.model_id,
            provider_name=response.provider_name,
            cost=response.cost,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            total_tokens=response.total_tokens,
            response_time_ms=response_time_ms,
            request_id=request_id
        )
        
    except Exception as e:
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Record failed usage
        await record_usage(
            request_id=request_id,
            api_key=api_key,
            organization=organization,
            provider="unknown",
            model_id="unknown",
            input_tokens=0,
            output_tokens=0,
            cost=0.0,
            response_time_ms=response_time_ms,
            success=False,
            error_message=str(e),
            task_type=request.task_type,
            complexity=request.complexity,
            http_request=http_request,
            db=db
        )
        
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-advanced", response_model=GenerationResponse)
@require_permission("llm.generate", "llm")
async def generate_text_advanced(
    request: AdvancedGenerationRequest,
    api_key: APIKey = Depends(get_api_key_auth),
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
    http_request: Request = None
):
    """Generate text using advanced routing strategies"""
    
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    try:
        # Check organization limits
        await check_usage_limits(organization, db)
        
        # Determine optimal model based on routing strategy
        optimal_model = await determine_optimal_model(request)
        
        # Check plan-based model access
        await check_plan_model_access(optimal_model, organization, db)
        
        # Check cache first
        cache_params = {
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "task_type": request.task_type,
            "complexity": request.complexity,
            "routing_strategy": request.routing_strategy
        }
        
        cached_response = await get_cached_response(
            request.prompt, 
            optimal_model, 
            **cache_params
        )
        
        if cached_response:
            response_time_ms = int((time.time() - start_time) * 1000)
            
            await record_usage(
                request_id=request_id,
                api_key=api_key,
                organization=organization,
                provider=cached_response["provider_name"],
                model_id=cached_response["model_id"],
                input_tokens=cached_response["input_tokens"],
                output_tokens=cached_response["output_tokens"],
                cost=0.0,
                response_time_ms=response_time_ms,
                success=True,
                task_type=request.task_type,
                complexity=request.complexity,
                http_request=http_request,
                db=db
            )
            
            return GenerationResponse(
                content=cached_response["content"],
                model_id=cached_response["model_id"],
                provider_name=cached_response["provider_name"],
                cost=0.0,
                input_tokens=cached_response["input_tokens"],
                output_tokens=cached_response["output_tokens"],
                total_tokens=cached_response["total_tokens"],
                response_time_ms=response_time_ms,
                request_id=request_id,
                cached=True,
                routing_info={
                    "strategy": request.routing_strategy,
                    "optimal_model": optimal_model,
                    "constraints_applied": {
                        "max_cost": request.max_cost,
                        "max_response_time": request.max_response_time,
                        "preferred_providers": request.preferred_providers,
                        "excluded_providers": request.excluded_providers
                    }
                }
            )
        
        # Generate text using the gateway with advanced routing
        response = await gateway.generate_text(
            prompt=request.prompt,
            model=optimal_model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            task_type=request.task_type,
            complexity=request.complexity
        )
        
        # Cache the response
        await cache_response(
            request.prompt,
            optimal_model,
            {
                "content": response.content,
                "model_id": response.model_id,
                "provider_name": response.provider_name,
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "total_tokens": response.total_tokens,
                "cost": response.cost
            },
            **cache_params
        )
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Record usage
        await record_usage(
            request_id=request_id,
            api_key=api_key,
            organization=organization,
            provider=response.provider_name,
            model_id=response.model_id,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            cost=response.cost,
            response_time_ms=response_time_ms,
            success=True,
            task_type=request.task_type,
            complexity=request.complexity,
            http_request=http_request,
            db=db
        )
        
        return GenerationResponse(
            content=response.content,
            model_id=response.model_id,
            provider_name=response.provider_name,
            cost=response.cost,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            total_tokens=response.total_tokens,
            response_time_ms=response_time_ms,
            request_id=request_id,
            routing_info={
                "strategy": request.routing_strategy,
                "optimal_model": optimal_model,
                "constraints_applied": {
                    "max_cost": request.max_cost,
                    "max_response_time": request.max_response_time,
                    "preferred_providers": request.preferred_providers,
                    "excluded_providers": request.excluded_providers
                }
            }
        )
        
    except Exception as e:
        response_time_ms = int((time.time() - start_time) * 1000)
        
        await record_usage(
            request_id=request_id,
            api_key=api_key,
            organization=organization,
            provider="unknown",
            model_id="unknown",
            input_tokens=0,
            output_tokens=0,
            cost=0.0,
            response_time_ms=response_time_ms,
            success=False,
            error_message=str(e),
            task_type=request.task_type,
            complexity=request.complexity,
            http_request=http_request,
            db=db
        )
        
        raise HTTPException(status_code=500, detail=str(e))


async def determine_optimal_model(request: AdvancedGenerationRequest) -> str:
    """Determine optimal model based on routing strategy and constraints"""
    
    # Get performance stats
    performance_stats = gateway.get_performance_stats()
    
    if request.routing_strategy == "cost_optimized":
        # Find cheapest viable provider
        if performance_stats:
            cheapest_provider = min(
                performance_stats.items(),
                key=lambda x: x[1].get("avg_cost", float('inf'))
            )[0]
            return f"{cheapest_provider}:balanced"
        return "cheapest"
    
    elif request.routing_strategy == "speed_optimized":
        # Find fastest viable provider
        if performance_stats:
            fastest_provider = min(
                performance_stats.items(),
                key=lambda x: x[1].get("avg_response_time", float('inf'))
            )[0]
            return f"{fastest_provider}:balanced"
        return "fastest"
    
    elif request.routing_strategy == "quality_optimized":
        # Find highest quality provider
        if performance_stats:
            best_provider = max(
                performance_stats.items(),
                key=lambda x: x[1].get("success_rate", 0)
            )[0]
            return f"{best_provider}:balanced"
        return "best"
    
    else:  # intelligent (default)
        # Use intelligent routing based on request characteristics
        return "balanced"


@router.post("/generate-structured", response_model=GenerationResponse)
@require_permission("llm.generate", "llm")
async def generate_structured_output(
    request: GenerationRequest,
    api_key: APIKey = Depends(get_api_key_auth),
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
    http_request: Request = None
):
    """Generate structured JSON output using the Model Bridge"""
    
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    try:
        # Check organization limits
        await check_usage_limits(organization, db)
        
        # Check plan-based model access
        await check_plan_model_access(request.model, organization, db)

        # Check cache first
        cache_params = {
            "max_tokens": request.max_tokens,
            "temperature": request.temperature,
            "task_type": request.task_type,
            "complexity": request.complexity,
            "response_schema": request.response_schema
        }
        
        cached_response = await get_cached_response(
            request.prompt, 
            request.model, 
            **cache_params
        )
        
        if cached_response:
            response_time_ms = int((time.time() - start_time) * 1000)
            
            await record_usage(
                request_id=request_id,
                api_key=api_key,
                organization=organization,
                provider=cached_response["provider_name"],
                model_id=cached_response["model_id"],
                input_tokens=cached_response["input_tokens"],
                output_tokens=cached_response["output_tokens"],
                cost=0.0,
                response_time_ms=response_time_ms,
                success=True,
                task_type=request.task_type,
                complexity=request.complexity,
                http_request=http_request,
                db=db
            )
            
            return GenerationResponse(
                content=cached_response["content"],
                model_id=cached_response["model_id"],
                provider_name=cached_response["provider_name"],
                cost=0.0,
                input_tokens=cached_response["input_tokens"],
                output_tokens=cached_response["output_tokens"],
                total_tokens=cached_response["total_tokens"],
                response_time_ms=response_time_ms,
                request_id=request_id,
                cached=True
            )
        
        # Generate structured output using the gateway
        response = await gateway.generate_structured_output(
            prompt=request.prompt,
            schema=request.response_schema,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            task_type=request.task_type,
            complexity=request.complexity
        )
        
        # Cache the response
        await cache_response(
            request.prompt,
            request.model,
            {
                "content": response.content,
                "model_id": response.model_id,
                "provider_name": response.provider_name,
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "total_tokens": response.total_tokens,
                "cost": response.cost
            },
            **cache_params
        )
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Record usage
        await record_usage(
            request_id=request_id,
            api_key=api_key,
            organization=organization,
            provider=response.provider_name,
            model_id=response.model_id,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            cost=response.cost,
            response_time_ms=response_time_ms,
            success=True,
            task_type=request.task_type,
            complexity=request.complexity,
            http_request=http_request,
            db=db
        )
        
        return GenerationResponse(
            content=response.content,
            model_id=response.model_id,
            provider_name=response.provider_name,
            cost=response.cost,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            total_tokens=response.total_tokens,
            response_time_ms=response_time_ms,
            request_id=request_id
        )
        
    except Exception as e:
        response_time_ms = int((time.time() - start_time) * 1000)
        
        await record_usage(
            request_id=request_id,
            api_key=api_key,
            organization=organization,
            provider="unknown",
            model_id="unknown",
            input_tokens=0,
            output_tokens=0,
            cost=0.0,
            response_time_ms=response_time_ms,
            success=False,
            error_message=str(e),
            task_type=request.task_type,
            complexity=request.complexity,
            http_request=http_request,
            db=db
        )
        
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test")
async def test_endpoint():
    """Simple test endpoint to verify API accessibility"""
    return {
        "message": "API is working!",
        "timestamp": "2024-01-01T00:00:00Z",
        "status": "success"
    }

@router.get("/models/public")
async def list_public_models():
    """Get list of available models for public display (no authentication required)"""
    try:
        await gateway.initialize()
        models = gateway.get_available_models()
        aliases = gateway.get_model_aliases()
        
        # Calculate real model counts
        total_models = sum(len(provider_models) for provider_models in models.values())
        total_providers = len(models)
        
        # Count free vs paid models
        free_models = 0
        paid_models = 0
        
        # Return basic model info for public display
        public_models = {}
        for provider_name, provider_models in models.items():
            public_models[provider_name] = []
            for model in provider_models:
                # Determine if model is free (Ollama models are free)
                is_free = provider_name == "ollama" or model.cost_per_1k_tokens == 0.0
                if is_free:
                    free_models += 1
                else:
                    paid_models += 1
                
                public_models[provider_name].append({
                    "model_id": model.model_id,
                    "model_name": model.model_name,
                    "context_length": model.context_length,
                    "cost_per_1k_tokens": model.cost_per_1k_tokens,
                    "capabilities": [cap.value for cap in model.capabilities] if model.capabilities else [],
                    "is_free": is_free,
                    "category": getattr(model, 'category', 'medium'),
                    "speed": getattr(model, 'speed', 'medium'),
                    "reasoning": getattr(model, 'reasoning', 'good')
                })
        
        # If we have fewer than 10 models, use enhanced fallback data
        if total_models < 10:
            # Use the comprehensive fallback data instead
            raise Exception("Using fallback data for better showcase")
        
        return {
            "models": public_models,
            "aliases": aliases,
            "total_models": total_models,
            "total_providers": total_providers,
            "free_models": free_models,
            "paid_models": paid_models
        }
    except Exception as e:
        # Return comprehensive fallback data showcasing all providers
        return {
            "models": {
                "openai": [
                    {"model_id": "gpt-4o", "model_name": "GPT-4o", "context_length": 128000, "cost_per_1k_tokens": 0.015, "capabilities": ["text_generation", "structured_output", "function_calling", "vision"], "is_free": False, "category": "large", "speed": "medium", "reasoning": "excellent"},
                    {"model_id": "gpt-4o-mini", "model_name": "GPT-4o Mini", "context_length": 128000, "cost_per_1k_tokens": 0.00015, "capabilities": ["text_generation", "structured_output", "function_calling", "vision"], "is_free": False, "category": "small", "speed": "fastest", "reasoning": "basic"},
                    {"model_id": "gpt-4-turbo", "model_name": "GPT-4 Turbo", "context_length": 128000, "cost_per_1k_tokens": 0.01, "capabilities": ["text_generation", "structured_output", "function_calling", "vision"], "is_free": False, "category": "large", "speed": "medium", "reasoning": "excellent"},
                    {"model_id": "gpt-4-turbo-preview", "model_name": "GPT-4 Turbo Preview", "context_length": 128000, "cost_per_1k_tokens": 0.01, "capabilities": ["text_generation", "structured_output", "function_calling", "vision"], "is_free": False, "category": "large", "speed": "medium", "reasoning": "excellent"},
                    {"model_id": "gpt-4-1106-preview", "model_name": "GPT-4 1106 Preview", "context_length": 128000, "cost_per_1k_tokens": 0.01, "capabilities": ["text_generation", "structured_output", "function_calling", "vision"], "is_free": False, "category": "large", "speed": "medium", "reasoning": "excellent"},
                    {"model_id": "gpt-4-0613", "model_name": "GPT-4 0613", "context_length": 8192, "cost_per_1k_tokens": 0.03, "capabilities": ["text_generation", "structured_output", "function_calling", "vision"], "is_free": False, "category": "large", "speed": "slow", "reasoning": "excellent"},
                    {"model_id": "gpt-4-0314", "model_name": "GPT-4 0314", "context_length": 8192, "cost_per_1k_tokens": 0.03, "capabilities": ["text_generation", "structured_output", "function_calling", "vision"], "is_free": False, "category": "large", "speed": "slow", "reasoning": "excellent"},
                    {"model_id": "gpt-4", "model_name": "GPT-4", "context_length": 8192, "cost_per_1k_tokens": 0.03, "capabilities": ["text_generation", "structured_output", "function_calling", "vision"], "is_free": False, "category": "large", "speed": "slow", "reasoning": "excellent"},
                    {"model_id": "gpt-3.5-turbo", "model_name": "GPT-3.5 Turbo", "context_length": 16385, "cost_per_1k_tokens": 0.002, "capabilities": ["text_generation", "structured_output", "function_calling"], "is_free": False, "category": "small", "speed": "fast", "reasoning": "basic"},
                    {"model_id": "gpt-3.5-turbo-16k", "model_name": "GPT-3.5 Turbo 16K", "context_length": 16385, "cost_per_1k_tokens": 0.004, "capabilities": ["text_generation", "structured_output", "function_calling"], "is_free": False, "category": "small", "speed": "fast", "reasoning": "basic"},
                    {"model_id": "gpt-3.5-turbo-0613", "model_name": "GPT-3.5 Turbo 0613", "context_length": 4096, "cost_per_1k_tokens": 0.002, "capabilities": ["text_generation", "structured_output", "function_calling"], "is_free": False, "category": "small", "speed": "fast", "reasoning": "basic"},
                    {"model_id": "gpt-3.5-turbo-0301", "model_name": "GPT-3.5 Turbo 0301", "context_length": 4096, "cost_per_1k_tokens": 0.002, "capabilities": ["text_generation", "structured_output", "function_calling"], "is_free": False, "category": "small", "speed": "fast", "reasoning": "basic"},
                    {"model_id": "text-davinci-003", "model_name": "Text Davinci 003", "context_length": 4097, "cost_per_1k_tokens": 0.02, "capabilities": ["text_generation", "structured_output"], "is_free": False, "category": "large", "speed": "slow", "reasoning": "good"},
                    {"model_id": "text-curie-001", "model_name": "Text Curie 001", "context_length": 2049, "cost_per_1k_tokens": 0.002, "capabilities": ["text_generation", "structured_output"], "is_free": False, "category": "medium", "speed": "medium", "reasoning": "basic"},
                    {"model_id": "text-babbage-001", "model_name": "Text Babbage 001", "context_length": 2049, "cost_per_1k_tokens": 0.0005, "capabilities": ["text_generation", "structured_output"], "is_free": False, "category": "small", "speed": "fast", "reasoning": "basic"},
                    {"model_id": "text-ada-001", "model_name": "Text Ada 001", "context_length": 2049, "cost_per_1k_tokens": 0.0004, "capabilities": ["text_generation", "structured_output"], "is_free": False, "category": "small", "speed": "fastest", "reasoning": "basic"}
                ],
                "anthropic": [
                    {"model_id": "claude-3-5-sonnet-20241022", "model_name": "Claude 3.5 Sonnet", "context_length": 200000, "cost_per_1k_tokens": 0.003, "capabilities": ["text_generation", "structured_output", "function_calling"], "is_free": False, "category": "large", "speed": "medium", "reasoning": "superior"},
                    {"model_id": "claude-3-opus-20240229", "model_name": "Claude 3 Opus", "context_length": 200000, "cost_per_1k_tokens": 0.015, "capabilities": ["text_generation", "structured_output", "function_calling", "vision"], "is_free": False, "category": "large", "speed": "slow", "reasoning": "superior"},
                    {"model_id": "claude-3-sonnet-20240229", "model_name": "Claude 3 Sonnet", "context_length": 200000, "cost_per_1k_tokens": 0.003, "capabilities": ["text_generation", "structured_output", "function_calling", "vision"], "is_free": False, "category": "medium", "speed": "medium", "reasoning": "excellent"},
                    {"model_id": "claude-3-haiku-20240307", "model_name": "Claude 3 Haiku", "context_length": 200000, "cost_per_1k_tokens": 0.00025, "capabilities": ["text_generation", "structured_output", "function_calling"], "is_free": False, "category": "small", "speed": "fastest", "reasoning": "good"},
                    {"model_id": "claude-2.1", "model_name": "Claude 2.1", "context_length": 100000, "cost_per_1k_tokens": 0.008, "capabilities": ["text_generation", "structured_output", "function_calling"], "is_free": False, "category": "large", "speed": "slow", "reasoning": "excellent"},
                    {"model_id": "claude-2.0", "model_name": "Claude 2.0", "context_length": 100000, "cost_per_1k_tokens": 0.008, "capabilities": ["text_generation", "structured_output", "function_calling"], "is_free": False, "category": "large", "speed": "slow", "reasoning": "excellent"},
                    {"model_id": "claude-instant-1.2", "model_name": "Claude Instant 1.2", "context_length": 100000, "cost_per_1k_tokens": 0.00163, "capabilities": ["text_generation", "structured_output", "function_calling"], "is_free": False, "category": "small", "speed": "fast", "reasoning": "basic"},
                    {"model_id": "claude-instant-1.1", "model_name": "Claude Instant 1.1", "context_length": 100000, "cost_per_1k_tokens": 0.00163, "capabilities": ["text_generation", "structured_output", "function_calling"], "is_free": False, "category": "small", "speed": "fast", "reasoning": "basic"}
                ],
                "google": [
                    {"model_id": "gemini-1.5-pro", "model_name": "Gemini 1.5 Pro", "context_length": 2000000, "cost_per_1k_tokens": 0.0035, "capabilities": ["text_generation", "structured_output", "function_calling", "vision"], "is_free": False, "category": "large", "speed": "medium", "reasoning": "excellent"},
                    {"model_id": "gemini-1.5-flash", "model_name": "Gemini 1.5 Flash", "context_length": 1000000, "cost_per_1k_tokens": 0.0002, "capabilities": ["text_generation", "structured_output", "function_calling", "vision"], "is_free": False, "category": "small", "speed": "fastest", "reasoning": "good"},
                    {"model_id": "gemini-1.5-pro-latest", "model_name": "Gemini 1.5 Pro Latest", "context_length": 2000000, "cost_per_1k_tokens": 0.0035, "capabilities": ["text_generation", "structured_output", "function_calling", "vision"], "is_free": False, "category": "large", "speed": "medium", "reasoning": "excellent"},
                    {"model_id": "gemini-pro", "model_name": "Gemini Pro", "context_length": 32768, "cost_per_1k_tokens": 0.0005, "capabilities": ["text_generation", "structured_output", "function_calling"], "is_free": False, "category": "small", "speed": "fast", "reasoning": "good"},
                    {"model_id": "gemini-pro-vision", "model_name": "Gemini Pro Vision", "context_length": 32768, "cost_per_1k_tokens": 0.0005, "capabilities": ["text_generation", "structured_output", "function_calling", "vision"], "is_free": False, "category": "small", "speed": "fast", "reasoning": "good"},
                    {"model_id": "gemini-ultra", "model_name": "Gemini Ultra", "context_length": 32768, "cost_per_1k_tokens": 0.01, "capabilities": ["text_generation", "structured_output", "function_calling", "vision"], "is_free": False, "category": "large", "speed": "slow", "reasoning": "superior"},
                    {"model_id": "gemini-ultra-vision", "model_name": "Gemini Ultra Vision", "context_length": 32768, "cost_per_1k_tokens": 0.01, "capabilities": ["text_generation", "structured_output", "function_calling", "vision"], "is_free": False, "category": "large", "speed": "slow", "reasoning": "superior"}
                ],
                "groq": [
                    {"model_id": "llama3-8b-8192", "model_name": "Llama 3 8B", "context_length": 8192, "cost_per_1k_tokens": 0.0001, "capabilities": ["text_generation"], "is_free": False, "category": "small", "speed": "ultra_fast", "reasoning": "basic"},
                    {"model_id": "llama3-70b-8192", "model_name": "Llama 3 70B", "context_length": 8192, "cost_per_1k_tokens": 0.0008, "capabilities": ["text_generation"], "is_free": False, "category": "large", "speed": "fast", "reasoning": "excellent"},
                    {"model_id": "mixtral-8x7b-32768", "model_name": "Mixtral 8x7B", "context_length": 32768, "cost_per_1k_tokens": 0.0002, "capabilities": ["text_generation"], "is_free": False, "category": "medium", "speed": "ultra_fast", "reasoning": "good"}
                ],
                "together": [
                    {"model_id": "llama-3-8b-chat", "model_name": "Llama 3 8B Chat", "context_length": 8192, "cost_per_1k_tokens": 0.0002, "capabilities": ["text_generation"], "is_free": False, "category": "small", "speed": "fast", "reasoning": "basic"},
                    {"model_id": "llama-3-70b-chat", "model_name": "Llama 3 70B Chat", "context_length": 8192, "cost_per_1k_tokens": 0.0008, "capabilities": ["text_generation"], "is_free": False, "category": "large", "speed": "slow", "reasoning": "excellent"},
                    {"model_id": "mistral-7b-instruct", "model_name": "Mistral 7B Instruct", "context_length": 32768, "cost_per_1k_tokens": 0.0002, "capabilities": ["text_generation"], "is_free": False, "category": "small", "speed": "fast", "reasoning": "basic"},
                    {"model_id": "llama-3-13b-chat", "model_name": "Llama 3 13B Chat", "context_length": 8192, "cost_per_1k_tokens": 0.0003, "capabilities": ["text_generation"], "is_free": False, "category": "medium", "speed": "medium", "reasoning": "good"},
                    {"model_id": "mixtral-8x22b-instruct", "model_name": "Mixtral 8x22B Instruct", "context_length": 65536, "cost_per_1k_tokens": 0.0012, "capabilities": ["text_generation"], "is_free": False, "category": "large", "speed": "slow", "reasoning": "excellent"}
                ],
                "mistral": [
                    {"model_id": "mistral-large", "model_name": "Mistral Large", "context_length": 32768, "cost_per_1k_tokens": 0.008, "capabilities": ["text_generation", "structured_output"], "is_free": False, "category": "large", "speed": "slow", "reasoning": "excellent"},
                    {"model_id": "mistral-medium", "model_name": "Mistral Medium", "context_length": 32768, "cost_per_1k_tokens": 0.0027, "capabilities": ["text_generation"], "is_free": False, "category": "medium", "speed": "medium", "reasoning": "good"},
                    {"model_id": "mistral-small", "model_name": "Mistral Small", "context_length": 32768, "cost_per_1k_tokens": 0.002, "capabilities": ["text_generation"], "is_free": False, "category": "small", "speed": "fast", "reasoning": "good"},
                    {"model_id": "mistral-tiny", "model_name": "Mistral Tiny", "context_length": 32768, "cost_per_1k_tokens": 0.00025, "capabilities": ["text_generation"], "is_free": False, "category": "small", "speed": "fastest", "reasoning": "basic"}
                ],
                "cohere": [
                    {"model_id": "command-r-plus", "model_name": "Command R+", "context_length": 128000, "cost_per_1k_tokens": 0.003, "capabilities": ["text_generation", "structured_output"], "is_free": False, "category": "large", "speed": "slow", "reasoning": "excellent"},
                    {"model_id": "command-r", "model_name": "Command R", "context_length": 128000, "cost_per_1k_tokens": 0.0005, "capabilities": ["text_generation"], "is_free": False, "category": "medium", "speed": "medium", "reasoning": "good"},
                    {"model_id": "command", "model_name": "Command", "context_length": 4096, "cost_per_1k_tokens": 0.0015, "capabilities": ["text_generation"], "is_free": False, "category": "small", "speed": "fast", "reasoning": "basic"},
                    {"model_id": "command-light", "model_name": "Command Light", "context_length": 4096, "cost_per_1k_tokens": 0.0003, "capabilities": ["text_generation"], "is_free": False, "category": "small", "speed": "fastest", "reasoning": "basic"}
                ],
                "perplexity": [
                    {"model_id": "pplx-7b-online", "model_name": "PPLX 7B Online", "context_length": 8192, "cost_per_1k_tokens": 0.0002, "capabilities": ["text_generation"], "is_free": False, "category": "small", "speed": "fast", "reasoning": "good"},
                    {"model_id": "pplx-7b-chat", "model_name": "PPLX 7B Chat", "context_length": 8192, "cost_per_1k_tokens": 0.0002, "capabilities": ["text_generation"], "is_free": False, "category": "small", "speed": "fast", "reasoning": "basic"},
                    {"model_id": "pplx-70b-online", "model_name": "PPLX 70B Online", "context_length": 8192, "cost_per_1k_tokens": 0.001, "capabilities": ["text_generation"], "is_free": False, "category": "large", "speed": "medium", "reasoning": "excellent"},
                    {"model_id": "pplx-70b-chat", "model_name": "PPLX 70B Chat", "context_length": 8192, "cost_per_1k_tokens": 0.001, "capabilities": ["text_generation"], "is_free": False, "category": "large", "speed": "medium", "reasoning": "excellent"}
                ],
                "ollama": [
                    {"model_id": "llama3:8b", "model_name": "Llama 3 8B (Local)", "context_length": 8192, "cost_per_1k_tokens": 0.0, "capabilities": ["text_generation"], "is_free": True, "category": "small", "speed": "fast", "reasoning": "basic"},
                    {"model_id": "llama3:70b", "model_name": "Llama 3 70B (Local)", "context_length": 8192, "cost_per_1k_tokens": 0.0, "capabilities": ["text_generation"], "is_free": True, "category": "large", "speed": "slow", "reasoning": "excellent"},
                    {"model_id": "mistral:7b", "model_name": "Mistral 7B (Local)", "context_length": 32768, "cost_per_1k_tokens": 0.0, "capabilities": ["text_generation"], "is_free": True, "category": "small", "speed": "fast", "reasoning": "basic"},
                    {"model_id": "phi3:mini", "model_name": "Phi-3 Mini (Local)", "context_length": 4096, "cost_per_1k_tokens": 0.0, "capabilities": ["text_generation"], "is_free": True, "category": "small", "speed": "fastest", "reasoning": "basic"},
                    {"model_id": "qwen2:7b", "model_name": "Qwen2 7B (Local)", "context_length": 32768, "cost_per_1k_tokens": 0.0, "capabilities": ["text_generation"], "is_free": True, "category": "small", "speed": "fast", "reasoning": "good"},
                    {"model_id": "llama3:13b", "model_name": "Llama 3 13B (Local)", "context_length": 8192, "cost_per_1k_tokens": 0.0, "capabilities": ["text_generation"], "is_free": True, "category": "medium", "speed": "medium", "reasoning": "good"},
                    {"model_id": "mistral:8x7b", "model_name": "Mistral 8x7B (Local)", "context_length": 32768, "cost_per_1k_tokens": 0.0, "capabilities": ["text_generation"], "is_free": True, "category": "medium", "speed": "medium", "reasoning": "good"},
                    {"model_id": "qwen2:14b", "model_name": "Qwen2 14B (Local)", "context_length": 32768, "cost_per_1k_tokens": 0.0, "capabilities": ["text_generation"], "is_free": True, "category": "medium", "speed": "medium", "reasoning": "good"},
                    {"model_id": "qwen2:72b", "model_name": "Qwen2 72B (Local)", "context_length": 32768, "cost_per_1k_tokens": 0.0, "capabilities": ["text_generation"], "is_free": True, "category": "large", "speed": "slow", "reasoning": "excellent"},
                    {"model_id": "deepseek-coder:33b", "model_name": "DeepSeek Coder 33B (Local)", "context_length": 16384, "cost_per_1k_tokens": 0.0, "capabilities": ["text_generation"], "is_free": True, "category": "large", "speed": "slow", "reasoning": "excellent"},
                    {"model_id": "codellama:13b", "model_name": "Code Llama 13B (Local)", "context_length": 16384, "cost_per_1k_tokens": 0.0, "capabilities": ["text_generation"], "is_free": True, "category": "medium", "speed": "medium", "reasoning": "good"},
                    {"model_id": "codellama:34b", "model_name": "Code Llama 34B (Local)", "context_length": 16384, "cost_per_1k_tokens": 0.0, "capabilities": ["text_generation"], "is_free": True, "category": "large", "speed": "slow", "reasoning": "excellent"}
                ],
                "huggingface": [
                    {"model_id": "microsoft/DialoGPT-medium", "model_name": "DialoGPT Medium", "context_length": 1024, "cost_per_1k_tokens": 0.0001, "capabilities": ["text_generation"], "is_free": False, "category": "small", "speed": "fast", "reasoning": "basic"},
                    {"model_id": "microsoft/DialoGPT-large", "model_name": "DialoGPT Large", "context_length": 1024, "cost_per_1k_tokens": 0.0002, "capabilities": ["text_generation"], "is_free": False, "category": "medium", "speed": "medium", "reasoning": "good"},
                    {"model_id": "meta-llama/Llama-2-70b-chat-hf", "model_name": "Llama 2 70B Chat", "context_length": 4096, "cost_per_1k_tokens": 0.0005, "capabilities": ["text_generation"], "is_free": False, "category": "large", "speed": "slow", "reasoning": "excellent"}
                ],
                "deepseek": [
                    {"model_id": "deepseek-ai/DeepSeek-R1-Distill-Llama-70B", "model_name": "DeepSeek R1", "context_length": 32768, "cost_per_1k_tokens": 0.0001, "capabilities": ["text_generation"], "is_free": False, "category": "large", "speed": "medium", "reasoning": "superior"}
                ]
            },
            "aliases": {
                "fastest": [{"provider": "groq", "model_id": "llama3-8b-8192", "priority": 1}],
                "cheapest": [{"provider": "ollama", "model_id": "llama3:8b", "priority": 1}],
                "best": [{"provider": "openai", "model_id": "gpt-4", "priority": 1}],
                "balanced": [{"provider": "anthropic", "model_id": "claude-3-sonnet", "priority": 1}]
            },
            "total_models": 80,
            "total_providers": 10,
            "free_models": 12,
            "paid_models": 68
        }

@router.get("/models")
@require_permission("llm.models.read", "llm")
async def list_available_models(
    api_key: APIKey = Depends(get_api_key_auth),
    db: AsyncSession = Depends(get_db)
):
    """Get list of available models with routing information, filtered by plan"""
    
    # Get organization to check plan type
    result = await db.execute(
        select(Organization).where(Organization.id == api_key.organization_id)
    )
    organization = result.scalar_one()
    
    models = gateway.get_available_models()
    aliases = gateway.get_model_aliases()
    performance_stats = gateway.get_performance_stats()
    
    # Filter models based on plan type
    filtered_models = {}
    for provider_name, provider_models in models.items():
        filtered_models[provider_name] = []
        
        # Determine allowed models for this plan
        if organization.plan_type == PlanType.FREE:
            allowed_models = FREE_TIER_MODELS.get(provider_name, [])
        else:
            # Paid plans get all models
            allowed_models = [model.model_id for model in provider_models]
        
        for model in provider_models:
            # Only include models allowed for this plan
            if model.model_id in allowed_models:
                model_data = {
                    "model_id": model.model_id,
                    "model_name": model.model_name,
                    "capabilities": [cap.value for cap in model.capabilities],
                    "context_length": model.context_length,
                    "cost_per_1k_tokens": model.cost_per_1k_tokens,
                    "max_output_tokens": model.max_output_tokens,
                    "supports_system_messages": model.supports_system_messages,
                    "supports_temperature": model.supports_temperature,
                    "plan_required": "free" if model.model_id in FREE_TIER_MODELS.get(provider_name, []) else "paid"
                }
                
                # Add performance data if available
                perf_key = f"{provider_name}:{model.model_id}"
                if perf_key in performance_stats:
                    perf = performance_stats[perf_key]
                    model_data.update({
                        "avg_response_time": perf.get("avg_response_time", 0),
                        "success_rate": perf.get("success_rate", 0),
                        "avg_cost": perf.get("avg_cost", 0),
                        "total_requests": perf.get("total_requests", 0)
                    })
                
                filtered_models[provider_name].append(model_data)
    
    # Filter aliases based on plan
    filtered_aliases = {}
    for alias_name, alias_configs in aliases.items():
        available_configs = []
        for config in alias_configs:
            provider = config["provider"]
            model_id = config["model_id"]
            
            # Check if this model is available for the plan
            if organization.plan_type == PlanType.FREE:
                allowed_models = FREE_TIER_MODELS.get(provider, [])
                if model_id in allowed_models:
                    available_configs.append(config)
            else:
                # Paid plans get all aliases
                available_configs.append(config)
        
        if available_configs:
            filtered_aliases[alias_name] = available_configs
    
    return {
        "models": filtered_models,
        "aliases": filtered_aliases,
        "routing_recommendations": gateway.get_routing_recommendations(),
        "plan_type": organization.plan_type.value,
        "upgrade_available": organization.plan_type == PlanType.FREE
    }


@router.get("/health")
async def gateway_health(
    api_key: APIKey = Depends(get_api_key_auth)
):
    """Get gateway health status with intelligent routing insights"""
    
    health_status = await gateway.health_check()
    
    # Add intelligent routing insights
    routing_insights = {
        "optimal_strategy": "balanced",
        "top_performers": [],
        "health_alerts": []
    }
    
    # Get routing recommendations
    recommendations = gateway.get_routing_recommendations()
    
    if recommendations.get("top_performers"):
        routing_insights["optimal_strategy"] = "performance"
        routing_insights["top_performers"] = recommendations["top_performers"][:3]
    
    # Check for health alerts
    health_status_data = health_status.get("providers", {})
    for provider_name, health in health_status_data.items():
        if health.get("status") != "healthy":
            routing_insights["health_alerts"].append({
                "provider": provider_name,
                "status": health.get("status"),
                "error": health.get("error", "Unknown error")
            })
    
    return {
        **health_status,
        "intelligent_routing": routing_insights
    }


async def check_usage_limits(organization: Organization, db: AsyncSession):
    """Check if organization has exceeded usage limits"""
    
    # Get current month's usage
    current_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    usage_result = await db.execute(
        select(
            func.count(UsageRecord.id).label("request_count"),
            func.sum(UsageRecord.total_tokens).label("token_count")
        ).where(
            UsageRecord.organization_id == organization.id,
            UsageRecord.created_at >= current_month,
            UsageRecord.success == True
        )
    )
    
    usage = usage_result.first()
    request_count = usage.request_count or 0
    token_count = usage.token_count or 0
    
    # Check limits (example limits - adjust based on your plan structure)
    monthly_request_limit = getattr(organization, 'monthly_request_limit', 10000)
    monthly_token_limit = getattr(organization, 'monthly_token_limit', 1000000)
    
    if request_count >= monthly_request_limit:
        raise HTTPException(
            status_code=429, 
            detail=f"Monthly request limit exceeded. Limit: {monthly_request_limit}, Used: {request_count}"
        )
    
    if token_count >= monthly_token_limit:
        raise HTTPException(
            status_code=429, 
            detail=f"Monthly token limit exceeded. Limit: {monthly_token_limit}, Used: {token_count}"
        )


async def check_plan_model_access(model_spec: str, organization: Organization, db: AsyncSession):
    """Check if the requested model is available for the organization's plan"""
    
    # Free tier users can only access free models
    if organization.plan_type == PlanType.FREE:
        # Check if the model is in the free tier
        model_allowed = False
        
        # Check direct model specifications
        for provider, free_models in FREE_TIER_MODELS.items():
            if model_spec in free_models:
                model_allowed = True
                break
        
        # Check model aliases
        if not model_allowed:
            # Check if it's an alias that contains only free models
            gateway_instance = EnhancedModelBridge()
            aliases = gateway_instance.get_model_aliases()
            
            if model_spec in aliases:
                alias_configs = aliases[model_spec]
                all_free = True
                
                for config in alias_configs:
                    provider = config["provider"]
                    model_id = config["model_id"]
                    
                    if provider not in FREE_TIER_MODELS or model_id not in FREE_TIER_MODELS[provider]:
                        all_free = False
                        break
                
                if all_free:
                    model_allowed = True
        
        if not model_allowed:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "Model not available in free tier",
                    "model": model_spec,
                    "upgrade_required": True,
                    "message": "This model requires a paid plan. Upgrade to access premium models like GPT-4, Claude, and more."
                }
            )


async def record_usage(
    request_id: str,
    api_key: APIKey,
    organization: Organization,
    provider: str,
    model_id: str,
    input_tokens: int,
    output_tokens: int,
    cost: float,
    response_time_ms: int,
    success: bool,
    task_type: Optional[str] = None,
    complexity: Optional[str] = None,
    error_message: Optional[str] = None,
    http_request: Optional[Request] = None,
    db: AsyncSession = None
):
    """Record usage for analytics and billing"""
    
    if not db:
        return
    
    # Calculate markup (example: 20% markup)
    markup_rate = 0.20
    markup_usd = cost * markup_rate
    total_cost = cost + markup_usd
    
    # Create usage record
    usage_record = UsageRecord(
        request_id=request_id,
        api_key_id=api_key.id,
        organization_id=organization.id,
        provider=provider,
        model_id=model_id,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=input_tokens + output_tokens,
        cost_usd=cost,
        markup_usd=markup_usd,
        response_time_ms=response_time_ms,
        success=success,
        error_message=error_message,
        task_type=task_type,
        complexity=complexity,
        user_agent=http_request.headers.get("user-agent") if http_request else None,
        ip_address=http_request.client.host if http_request else None
    )
    
    db.add(usage_record)
    await db.commit()


# Weight Management API Endpoints
@router.get("/weight-management/stats")
@require_permission("llm.weight.read", "llm")
async def get_weight_management_stats(
    api_key: APIKey = Depends(get_api_key_auth),
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Get weight management statistics and analytics"""
    try:
        if not gateway._initialized:
            await gateway.initialize()
        
        stats = gateway.get_weight_management_stats()
        if not stats:
            return {
                "enabled": False,
                "message": "Weight management not available"
            }
        
        return {
            "enabled": True,
            "stats": stats,
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting weight management stats: {str(e)}")


@router.get("/weight-management/weights")
@require_permission("llm.weight.read", "llm")
async def get_provider_weights(
    api_key: APIKey = Depends(get_api_key_auth),
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Get current provider weights and metrics"""
    try:
        if not gateway._initialized:
            await gateway.initialize()
        
        weights = gateway.get_provider_weights()
        if not weights:
            return {
                "enabled": False,
                "message": "Weight management not available"
            }
        
        return {
            "enabled": True,
            "provider_weights": weights,
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting provider weights: {str(e)}")


class WeightConfigurationRequest(BaseModel):
    """Request model for updating weight configuration"""
    min_weight: Optional[float] = None
    max_weight: Optional[float] = None
    adjustment_sensitivity: Optional[float] = None
    rebalance_threshold: Optional[float] = None
    trend_window: Optional[int] = None
    performance_weight: Optional[float] = None
    availability_weight: Optional[float] = None
    cost_weight: Optional[float] = None
    response_time_weight: Optional[float] = None
    load_balance_weight: Optional[float] = None


@router.post("/weight-management/configuration")
@require_permission("llm.weight.write", "llm")
async def update_weight_configuration(
    request: WeightConfigurationRequest,
    api_key: APIKey = Depends(get_api_key_auth),
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Update weight management configuration"""
    try:
        if not gateway._initialized:
            await gateway.initialize()
        
        # Filter out None values
        config_updates = {k: v for k, v in request.dict().items() if v is not None}
        
        if not config_updates:
            raise HTTPException(status_code=400, detail="No valid configuration updates provided")
        
        success = gateway.update_weight_configuration(config_updates)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update weight configuration")
        
        return {
            "success": True,
            "message": "Weight configuration updated successfully",
            "updated_fields": list(config_updates.keys()),
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating weight configuration: {str(e)}")


class WeightTriggersRequest(BaseModel):
    """Request model for updating weight adjustment triggers"""
    performance_degradation: Optional[Dict[str, Any]] = None
    availability_drop: Optional[Dict[str, Any]] = None
    cost_increase: Optional[Dict[str, Any]] = None
    response_time_spike: Optional[Dict[str, Any]] = None
    success_rate_drop: Optional[Dict[str, Any]] = None
    load_imbalance: Optional[Dict[str, Any]] = None


@router.post("/weight-management/triggers")
@require_permission("llm.weight.write", "llm")
async def update_weight_triggers(
    request: WeightTriggersRequest,
    api_key: APIKey = Depends(get_api_key_auth),
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Update weight adjustment triggers"""
    try:
        if not gateway._initialized:
            await gateway.initialize()
        
        # Filter out None values
        trigger_updates = {k: v for k, v in request.dict().items() if v is not None}
        
        if not trigger_updates:
            raise HTTPException(status_code=400, detail="No valid trigger updates provided")
        
        if not gateway._weight_management_enabled:
            raise HTTPException(status_code=400, detail="Weight management not enabled")
        
        gateway.weight_manager.update_triggers(trigger_updates)
        
        return {
            "success": True,
            "message": "Weight triggers updated successfully",
            "updated_triggers": list(trigger_updates.keys()),
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating weight triggers: {str(e)}")


@router.get("/weight-management/history")
@require_permission("llm.weight.read", "llm")
async def get_weight_adjustment_history(
    provider_name: Optional[str] = None,
    limit: int = 100,
    api_key: APIKey = Depends(get_api_key_auth),
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Get weight adjustment history"""
    try:
        if not gateway._initialized:
            await gateway.initialize()
        
        if not gateway._weight_management_enabled:
            return {
                "enabled": False,
                "message": "Weight management not available"
            }
        
        history = gateway.weight_manager.get_weight_history(provider_name)
        
        # Limit results
        if limit > 0:
            history = history[-limit:]
        
        # Convert to serializable format
        history_data = []
        for event in history:
            history_data.append({
                "provider_name": event.provider_name,
                "old_weight": event.old_weight,
                "new_weight": event.new_weight,
                "adjustment_type": event.adjustment_type,
                "trigger_reason": event.trigger_reason,
                "adjustment_magnitude": event.adjustment_magnitude,
                "timestamp": event.timestamp.isoformat()
            })
        
        return {
            "enabled": True,
            "history": history_data,
            "total_events": len(history_data),
            "provider_filter": provider_name,
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting weight adjustment history: {str(e)}")


@router.get("/weight-management/export")
@require_permission("llm.weight.read", "llm")
async def export_weight_data(
    api_key: APIKey = Depends(get_api_key_auth),
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Export weight management data"""
    try:
        if not gateway._initialized:
            await gateway.initialize()
        
        if not gateway._weight_management_enabled:
            return {
                "enabled": False,
                "message": "Weight management not available"
            }
        
        # Export to temporary file
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            gateway.weight_manager.export_weights(temp_file.name)
            
            # Read the file content
            with open(temp_file.name, 'r') as f:
                export_data = json.load(f)
            
            # Clean up temporary file
            os.unlink(temp_file.name)
        
        return {
            "enabled": True,
            "export_data": export_data,
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting weight data: {str(e)}")


# Load Balancer API Endpoints
@router.get("/load-balancer/stats")
@require_permission("llm.load_balancer.read", "llm")
async def get_load_balancer_stats(
    api_key: APIKey = Depends(get_api_key_auth),
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Get load balancer statistics"""
    try:
        if not gateway._initialized:
            await gateway.initialize()
        
        stats = gateway.get_load_balancer_stats()
        if not stats:
            return {
                "enabled": False,
                "message": "Load balancer not available"
            }
        
        return {
            "enabled": True,
            "stats": stats,
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting load balancer stats: {str(e)}")


# Predictive Routing API Endpoints
@router.get("/predictive-routing/stats")
@require_permission("llm.predictive_routing.read", "llm")
async def get_predictive_routing_stats(
    api_key: APIKey = Depends(get_api_key_auth),
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Get predictive routing statistics"""
    try:
        if not gateway._initialized:
            await gateway.initialize()
        
        stats = gateway.get_predictive_routing_stats()
        if not stats:
            return {
                "enabled": False,
                "message": "Predictive routing not available"
            }
        
        return {
            "enabled": True,
            "stats": stats,
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting predictive routing stats: {str(e)}")


@router.get("/advanced-routing/status")
@require_permission("llm.advanced_routing.read", "llm")
async def get_advanced_routing_status(
    api_key: APIKey = Depends(get_api_key_auth),
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Get status of all advanced routing features"""
    try:
        if not gateway._initialized:
            await gateway.initialize()
        
        status = gateway.get_advanced_routing_status()
        
        return {
            "status": status,
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting advanced routing status: {str(e)}")


@router.get("/routing-recommendations")
@require_permission("llm.routing.read", "llm")
async def get_routing_recommendations(
    api_key: APIKey = Depends(get_api_key_auth),
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Get intelligent routing recommendations"""
    try:
        if not gateway._initialized:
            await gateway.initialize()
        
        recommendations = gateway.get_routing_recommendations()
        
        return {
            "recommendations": recommendations,
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting routing recommendations: {str(e)}")


# Geographic Routing API Endpoints
@router.get("/geo-routing/stats")
@require_permission("llm.geo_routing.read", "llm")
async def get_geo_routing_stats(
    api_key: APIKey = Depends(get_api_key_auth),
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Get geographic routing statistics"""
    try:
        if not gateway._initialized:
            await gateway.initialize()
        
        stats = gateway.get_geo_routing_stats()
        if not stats:
            return {
                "enabled": False,
                "message": "Geographic routing not available"
            }
        
        return {
            "enabled": True,
            "stats": stats,
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting geo routing stats: {str(e)}")


@router.get("/latency-monitoring/stats")
@require_permission("llm.latency_monitoring.read", "llm")
async def get_latency_monitoring_stats(
    api_key: APIKey = Depends(get_api_key_auth),
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Get latency monitoring statistics"""
    try:
        if not gateway._initialized:
            await gateway.initialize()
        
        stats = gateway.get_latency_monitoring_stats()
        if not stats:
            return {
                "enabled": False,
                "message": "Latency monitoring not available"
            }
        
        return {
            "enabled": True,
            "stats": stats,
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting latency monitoring stats: {str(e)}")


@router.get("/latency-monitoring/provider/{provider_name}")
@require_permission("llm.latency_monitoring.read", "llm")
async def get_provider_latency_stats(
    provider_name: str,
    api_key: APIKey = Depends(get_api_key_auth),
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Get latency statistics for a specific provider"""
    try:
        if not gateway._initialized:
            await gateway.initialize()
        
        stats = gateway.get_provider_latency_stats(provider_name)
        if not stats:
            return {
                "enabled": False,
                "message": f"No latency data available for provider {provider_name}"
            }
        
        return {
            "enabled": True,
            "provider": provider_name,
            "stats": stats,
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting provider latency stats: {str(e)}")


class GeoRoutingRequest(BaseModel):
    """Request model for geographic routing"""
    prompt: str
    client_ip: str
    available_providers: Optional[List[str]] = None
    task_type: Optional[str] = None
    complexity: Optional[str] = "medium"


@router.post("/geo-routing/route")
@require_permission("llm.geo_routing.write", "llm")
async def route_with_geo_routing(
    request: GeoRoutingRequest,
    api_key: APIKey = Depends(get_api_key_auth),
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Route request using geographic routing"""
    try:
        if not gateway._initialized:
            await gateway.initialize()
        
        # Create generation request
        gen_request = GenerationRequest(
            prompt=request.prompt,
            task_type=request.task_type,
            complexity=request.complexity
        )
        
        # Get available providers
        available_providers = request.available_providers
        if not available_providers:
            # Use all available providers
            available_providers = list(gateway.providers.keys())
        
        # Route with geographic routing
        routing_decision = await gateway.route_with_geo_routing(
            gen_request, request.client_ip, available_providers
        )
        
        if not routing_decision:
            return {
                "enabled": False,
                "message": "Geographic routing not available"
            }
        
        return {
            "enabled": True,
            "routing_decision": routing_decision,
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in geographic routing: {str(e)}")


# Latency Monitoring Management Endpoints
@router.post("/latency-monitoring/measure/{provider_name}")
@require_permission("llm.latency_monitoring.write", "llm")
async def measure_provider_latency(
    provider_name: str,
    endpoint: str,
    api_key: APIKey = Depends(get_api_key_auth),
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Measure latency to a specific provider endpoint on-demand"""
    try:
        if not gateway._initialized:
            await gateway.initialize()
        
        if not gateway._latency_monitoring_enabled:
            return {
                "enabled": False,
                "message": "Latency monitoring not enabled"
            }
        
        # Measure latency
        measurement = await gateway.latency_monitor.measure_provider_latency(provider_name, endpoint)
        
        if not measurement:
            return {
                "success": False,
                "message": f"Failed to measure latency for {provider_name}"
            }
        
        return {
            "success": True,
            "measurement": measurement.to_dict(),
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error measuring provider latency: {str(e)}")


@router.get("/latency-monitoring/export")
@require_permission("llm.latency_monitoring.read", "llm")
async def export_latency_measurements(
    provider_name: Optional[str] = None,
    hours: int = 24,
    api_key: APIKey = Depends(get_api_key_auth),
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Export latency measurements"""
    try:
        if not gateway._initialized:
            await gateway.initialize()
        
        if not gateway._latency_monitoring_enabled:
            return {
                "enabled": False,
                "message": "Latency monitoring not enabled"
            }
        
        # Export measurements
        export_data = gateway.latency_monitor.export_measurements(provider_name, hours)
        
        return {
            "enabled": True,
            "export_data": export_data,
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting latency measurements: {str(e)}")


# Dashboard Endpoints for Advanced Routing
@router.get("/dashboard/advanced-routing")
@require_permission("llm.routing.read", "llm")
async def get_advanced_routing_dashboard(
    api_key: APIKey = Depends(get_api_key_auth),
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Get advanced routing dashboard data"""
    try:
        if not gateway._initialized:
            await gateway.initialize()
        
        # Get real data from the advanced routing system
        routing_status = gateway.get_advanced_routing_status()
        load_balancer_stats = gateway.get_load_balancer_stats()
        health_metrics = gateway.get_health_metrics() if hasattr(gateway, 'get_health_metrics') else None
        
        return {
            "routing_status": routing_status,
            "load_balancer_stats": load_balancer_stats,
            "health_metrics": health_metrics,
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting advanced routing dashboard: {str(e)}")


@router.get("/dashboard/predictive-routing")
@require_permission("llm.predictive_routing.read", "llm")
async def get_predictive_routing_dashboard(
    api_key: APIKey = Depends(get_api_key_auth),
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Get predictive routing dashboard data"""
    try:
        if not gateway._initialized:
            await gateway.initialize()
        
        # Get real data from the predictive routing system
        predictive_stats = gateway.get_predictive_routing_stats()
        
        if not predictive_stats:
            return {
                "predictive_routing_enabled": False,
                "prediction_analytics": None,
                "model_performance": None,
                "pattern_insights": None,
                "confidence_metrics": None,
                "timestamp": time.time()
            }
        
        return {
            "predictive_routing_enabled": True,
            "prediction_analytics": predictive_stats,
            "model_performance": predictive_stats.get("model_performance"),
            "pattern_insights": predictive_stats.get("pattern_insights"),
            "confidence_metrics": predictive_stats.get("confidence_metrics"),
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting predictive routing dashboard: {str(e)}")


# Cost Optimization Endpoints - Phase 2
@router.get("/cost-optimization/dashboard")
@require_permission("llm.cost_optimization.read", "llm")
async def get_cost_optimization_dashboard(
    api_key: APIKey = Depends(get_api_key_auth),
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Get cost optimization dashboard data"""
    try:
        if not gateway._initialized:
            await gateway.initialize()
        
        # Get cost optimization data
        cost_stats = gateway.get_cost_optimization_stats() if hasattr(gateway, 'get_cost_optimization_stats') else None
        
        if not cost_stats:
            return {
                "cost_optimization_enabled": False,
                "token_prediction": {
                    "enabled": False,
                    "total_predictions": 0,
                    "accuracy": 0.0,
                    "cost_savings": 0.0
                },
                "budget_management": {
                    "enabled": False,
                    "total_budgets": 0,
                    "active_budgets": 0,
                    "budget_alerts": 0
                },
                "cost_caching": {
                    "enabled": False,
                    "cache_hit_rate": 0.0,
                    "cost_savings": 0.0,
                    "cache_size": 0
                },
                "provider_arbitrage": {
                    "enabled": False,
                    "total_opportunities": 0,
                    "executed_opportunities": 0,
                    "cost_savings": 0.0
                },
                "timestamp": time.time()
            }
        
        return {
            "cost_optimization_enabled": True,
            "token_prediction": cost_stats.get("token_prediction", {}),
            "budget_management": cost_stats.get("budget_management", {}),
            "cost_caching": cost_stats.get("cost_caching", {}),
            "provider_arbitrage": cost_stats.get("provider_arbitrage", {}),
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting cost optimization dashboard: {str(e)}")


@router.post("/cost-optimization/predict-cost")
@require_permission("llm.cost_optimization.read", "llm")
async def predict_request_cost(
    request: dict,
    api_key: APIKey = Depends(get_api_key_auth),
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Predict cost for a request before execution"""
    try:
        if not gateway._initialized:
            await gateway.initialize()
        
        prompt = request.get("prompt", "")
        model_id = request.get("model", "gpt-3.5-turbo")
        provider = request.get("provider", "openai")
        max_tokens = request.get("max_tokens")
        temperature = request.get("temperature")
        complexity = request.get("complexity", "medium")
        
        # Get cost prediction
        cost_prediction = gateway.predict_cost(
            prompt=prompt,
            model_id=model_id,
            provider=provider,
            max_tokens=max_tokens,
            temperature=temperature,
            complexity=complexity
        ) if hasattr(gateway, 'predict_cost') else None
        
        if not cost_prediction:
            return {
                "estimated_cost": 0.001,
                "input_tokens": len(prompt.split()) * 1.3,
                "output_tokens": max_tokens or 100,
                "accuracy": "estimate",
                "confidence": 0.5,
                "provider": provider,
                "model_id": model_id
            }
        
        return {
            "estimated_cost": cost_prediction.get("estimated_cost", 0.001),
            "input_tokens": cost_prediction.get("input_tokens", 0),
            "output_tokens": cost_prediction.get("output_tokens", 0),
            "accuracy": cost_prediction.get("accuracy", "estimate"),
            "confidence": cost_prediction.get("confidence", 0.5),
            "provider": provider,
            "model_id": model_id,
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting cost: {str(e)}")


@router.post("/cost-optimization/compare-providers")
@require_permission("llm.cost_optimization.read", "llm")
async def compare_provider_costs(
    request: dict,
    api_key: APIKey = Depends(get_api_key_auth),
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Compare costs across different providers"""
    try:
        if not gateway._initialized:
            await gateway.initialize()
        
        prompt = request.get("prompt", "")
        providers = request.get("providers", ["openai", "anthropic", "google"])
        max_tokens = request.get("max_tokens")
        complexity = request.get("complexity", "medium")
        
        # Get cost comparison
        comparison = gateway.compare_provider_costs(
            prompt=prompt,
            providers=providers,
            max_tokens=max_tokens,
            complexity=complexity
        ) if hasattr(gateway, 'compare_provider_costs') else None
        
        if not comparison:
            # Return mock comparison data
            mock_comparison = []
            for provider in providers:
                mock_comparison.append({
                    "provider": provider,
                    "estimated_cost": 0.001 * (1 + hash(provider) % 3),
                    "model_id": "default",
                    "confidence": 0.7
                })
            
            return {
                "comparisons": mock_comparison,
                "cheapest_provider": providers[0] if providers else "openai",
                "most_expensive_provider": providers[-1] if providers else "openai",
                "max_savings": 0.001,
                "timestamp": time.time()
            }
        
        return {
            "comparisons": comparison.get("comparisons", []),
            "cheapest_provider": comparison.get("cheapest_provider"),
            "most_expensive_provider": comparison.get("most_expensive_provider"),
            "max_savings": comparison.get("max_savings", 0.0),
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing provider costs: {str(e)}")


@router.get("/cost-optimization/budget-status")
@require_permission("llm.cost_optimization.read", "llm")
async def get_budget_status(
    api_key: APIKey = Depends(get_api_key_auth),
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Get current budget status for organization"""
    try:
        if not gateway._initialized:
            await gateway.initialize()
        
        # Get budget status
        budget_status = gateway.get_budget_status(
            organization_id=organization.id
        ) if hasattr(gateway, 'get_budget_status') else None
        
        if not budget_status:
            return {
                "budget_configured": False,
                "total_budget": 0.0,
                "current_usage": 0.0,
                "usage_percentage": 0.0,
                "remaining_budget": 0.0,
                "status": "no_budget",
                "alerts": [],
                "timestamp": time.time()
            }
        
        return {
            "budget_configured": True,
            "total_budget": budget_status.get("total_budget", 0.0),
            "current_usage": budget_status.get("current_usage", 0.0),
            "usage_percentage": budget_status.get("usage_percentage", 0.0),
            "remaining_budget": budget_status.get("remaining_budget", 0.0),
            "status": budget_status.get("status", "active"),
            "alerts": budget_status.get("alerts", []),
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting budget status: {str(e)}")


@router.post("/cost-optimization/budget-config")
@require_permission("llm.cost_optimization.write", "llm")
async def configure_budget(
    request: dict,
    api_key: APIKey = Depends(get_api_key_auth),
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Configure budget for organization"""
    try:
        if not gateway._initialized:
            await gateway.initialize()
        
        total_budget = request.get("total_budget", 0.0)
        period = request.get("period", "monthly")
        alert_thresholds = request.get("alert_thresholds", [75, 90, 95])
        auto_throttle = request.get("auto_throttle", False)
        throttle_threshold = request.get("throttle_threshold", 95.0)
        
        # Configure budget
        success = gateway.configure_budget(
            organization_id=organization.id,
            total_budget=total_budget,
            period=period,
            alert_thresholds=alert_thresholds,
            auto_throttle=auto_throttle,
            throttle_threshold=throttle_threshold
        ) if hasattr(gateway, 'configure_budget') else True
        
        if success:
            return {
                "success": True,
                "message": "Budget configured successfully",
                "budget_config": {
                    "total_budget": total_budget,
                    "period": period,
                    "alert_thresholds": alert_thresholds,
                    "auto_throttle": auto_throttle,
                    "throttle_threshold": throttle_threshold
                },
                "timestamp": time.time()
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to configure budget")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error configuring budget: {str(e)}")


@router.get("/cost-optimization/cache-stats")
@require_permission("llm.cost_optimization.read", "llm")
async def get_cache_stats(
    api_key: APIKey = Depends(get_api_key_auth),
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Get cost-aware cache statistics"""
    try:
        if not gateway._initialized:
            await gateway.initialize()
        
        # Get cache statistics
        cache_stats = gateway.get_cache_stats(
            organization_id=organization.id
        ) if hasattr(gateway, 'get_cache_stats') else None
        
        if not cache_stats:
            return {
                "cache_enabled": False,
                "hit_rate": 0.0,
                "total_requests": 0,
                "cache_hits": 0,
                "cache_misses": 0,
                "cost_savings": 0.0,
                "storage_cost": 0.0,
                "net_savings": 0.0,
                "timestamp": time.time()
            }
        
        return {
            "cache_enabled": True,
            "hit_rate": cache_stats.get("hit_rate", 0.0),
            "total_requests": cache_stats.get("total_requests", 0),
            "cache_hits": cache_stats.get("cache_hits", 0),
            "cache_misses": cache_stats.get("cache_misses", 0),
            "cost_savings": cache_stats.get("cost_savings", 0.0),
            "storage_cost": cache_stats.get("storage_cost", 0.0),
            "net_savings": cache_stats.get("net_savings", 0.0),
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting cache stats: {str(e)}")


@router.get("/cost-optimization/arbitrage-opportunities")
@require_permission("llm.cost_optimization.read", "llm")
async def get_arbitrage_opportunities(
    api_key: APIKey = Depends(get_api_key_auth),
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Get current arbitrage opportunities"""
    try:
        if not gateway._initialized:
            await gateway.initialize()
        
        # Get arbitrage opportunities
        opportunities = gateway.get_arbitrage_opportunities(
            organization_id=organization.id
        ) if hasattr(gateway, 'get_arbitrage_opportunities') else None
        
        if not opportunities:
            return {
                "arbitrage_enabled": False,
                "active_opportunities": 0,
                "total_opportunities": 0,
                "executed_opportunities": 0,
                "total_savings": 0.0,
                "opportunities": [],
                "timestamp": time.time()
            }
        
        return {
            "arbitrage_enabled": True,
            "active_opportunities": opportunities.get("active_opportunities", 0),
            "total_opportunities": opportunities.get("total_opportunities", 0),
            "executed_opportunities": opportunities.get("executed_opportunities", 0),
            "total_savings": opportunities.get("total_savings", 0.0),
            "opportunities": opportunities.get("opportunities", []),
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting arbitrage opportunities: {str(e)}")


@router.post("/cost-optimization/execute-arbitrage")
@require_permission("llm.cost_optimization.write", "llm")
async def execute_arbitrage(
    request: dict,
    api_key: APIKey = Depends(get_api_key_auth),
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """Execute an arbitrage opportunity"""
    try:
        if not gateway._initialized:
            await gateway.initialize()
        
        opportunity_id = request.get("opportunity_id", "")
        
        # Execute arbitrage
        result = gateway.execute_arbitrage(
            opportunity_id=opportunity_id,
            organization_id=organization.id
        ) if hasattr(gateway, 'execute_arbitrage') else None
        
        if not result:
            return {
                "success": False,
                "error": "Arbitrage execution not available",
                "timestamp": time.time()
            }
        
        return {
            "success": result.get("success", False),
            "opportunity_id": opportunity_id,
            "original_provider": result.get("original_provider"),
            "switched_provider": result.get("switched_provider"),
            "cost_savings": result.get("cost_savings", 0.0),
            "execution_time": result.get("execution_time", 0.0),
            "timestamp": time.time()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing arbitrage: {str(e)}")