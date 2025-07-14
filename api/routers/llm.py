"""
Enhanced LLM API routes with SaaS features
"""
import json
import time
import uuid
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from models.user import APIKey, Organization, UsageRecord
from auth.dependencies import get_api_key_auth, get_current_organization
from llm_gateway import EnhancedLLMGateway
from utils.cache import get_cached_response, cache_response

router = APIRouter()

# Initialize the LLM Gateway
gateway = EnhancedLLMGateway()


class GenerationRequest(BaseModel):
    prompt: str
    model: str = "balanced"
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    task_type: Optional[str] = None
    complexity: Optional[str] = "medium"
    schema: Optional[Dict[str, Any]] = None  # For structured output


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


@router.on_event("startup")
async def startup_event():
    """Initialize gateway on startup"""
    await gateway.initialize()


@router.post("/generate", response_model=GenerationResponse)
async def generate_text(
    request: GenerationRequest,
    api_key: APIKey = Depends(get_api_key_auth),
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
    http_request: Request = None
):
    """Generate text using the LLM gateway"""
    
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    try:
        # Check organization limits
        await check_usage_limits(organization, db)
        
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
        
        # Generate text using the gateway
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


@router.post("/generate-structured", response_model=GenerationResponse)
async def generate_structured_output(
    request: GenerationRequest,
    api_key: APIKey = Depends(get_api_key_auth),
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db),
    http_request: Request = None
):
    """Generate structured output using the LLM gateway"""
    
    if not request.schema:
        raise HTTPException(status_code=400, detail="Schema is required for structured output")
    
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    try:
        # Check organization limits
        await check_usage_limits(organization, db)
        
        # Generate structured output using the gateway
        response = await gateway.generate_structured_output(
            prompt=request.prompt,
            schema=request.schema,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            task_type=request.task_type,
            complexity=request.complexity
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


@router.get("/models")
async def list_available_models(
    api_key: APIKey = Depends(get_api_key_auth)
):
    """List all available models"""
    models = await gateway.get_available_models()
    return {"models": models}


@router.get("/health")
async def gateway_health(
    api_key: APIKey = Depends(get_api_key_auth)
):
    """Get gateway health status"""
    health = await gateway.health_check()
    return health


async def check_usage_limits(organization: Organization, db: AsyncSession):
    """Check if organization has exceeded usage limits"""
    from sqlalchemy import func, extract
    from datetime import datetime
    
    current_month = datetime.utcnow().month
    current_year = datetime.utcnow().year
    
    # Get current month usage
    result = await db.execute(
        select(
            func.count(UsageRecord.id).label("request_count"),
            func.sum(UsageRecord.total_tokens).label("token_count")
        ).where(
            UsageRecord.organization_id == organization.id,
            extract('month', UsageRecord.created_at) == current_month,
            extract('year', UsageRecord.created_at) == current_year,
            UsageRecord.success == True
        )
    )
    
    usage = result.first()
    request_count = usage.request_count or 0
    token_count = usage.token_count or 0
    
    # Check limits
    if request_count >= organization.monthly_request_limit:
        raise HTTPException(
            status_code=429,
            detail=f"Monthly request limit ({organization.monthly_request_limit}) exceeded"
        )
    
    if token_count >= organization.monthly_token_limit:
        raise HTTPException(
            status_code=429,
            detail=f"Monthly token limit ({organization.monthly_token_limit}) exceeded"
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
    
    # Calculate markup (20% margin)
    markup = cost * 0.2
    
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
        markup_usd=markup,
        response_time_ms=response_time_ms,
        success=success,
        error_message=error_message,
        task_type=task_type,
        complexity=complexity,
        user_agent=http_request.headers.get("User-Agent") if http_request else None,
        ip_address=http_request.client.host if http_request else None
    )
    
    db.add(usage_record)
    await db.commit()