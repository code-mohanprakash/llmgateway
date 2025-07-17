"""
FastAPI dependencies for authentication and authorization
"""
import hashlib
import time
import os
from datetime import datetime
from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from database.database import get_db
from models.user import User, APIKey, Organization
from auth.jwt_handler import verify_token, decode_api_key
import redis

# Redis client for rate limiting
redis_client = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=6379, decode_responses=True)

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(credentials.credentials)
        if payload is None or payload.get("type") != "access":
            raise credentials_exception
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # Get user from database with organization relationship preloaded
        result = await db.execute(
            select(User).options(selectinload(User.organization))
            .where(User.id == user_id, User.is_active == True)
        )
        user = result.scalar_one_or_none()
        
        if user is None:
            raise credentials_exception
        
        return user
    except Exception as e:
        # Log the error for debugging
        print(f"Authentication error: {e}")
        raise credentials_exception


async def get_api_key_auth(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> APIKey:
    """Authenticate using API key"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    api_key = authorization.split(" ")[1]
    
    # Decode API key
    key_part = decode_api_key(api_key)
    if not key_part:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key format"
        )
    
    # Hash the key to find in database
    key_hash = hashlib.sha256(key_part.encode()).hexdigest()
    
    # Find API key in database
    result = await db.execute(
        select(APIKey).where(
            APIKey.key_hash == key_hash,
            APIKey.is_active == True,
            APIKey.is_deleted == False
        )
    )
    api_key_obj = result.scalar_one_or_none()
    
    if not api_key_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Check rate limits
    await check_rate_limits(api_key_obj)
    
    # Update usage
    api_key_obj.usage_count += 1
    api_key_obj.last_used_at = datetime.utcnow().isoformat()
    await db.commit()
    
    return api_key_obj


async def check_rate_limits(api_key: APIKey):
    """Check if API key has exceeded rate limits"""
    key_id = str(api_key.id)
    current_time = int(time.time())
    
    # Check per-minute limit
    minute_key = f"rate_limit:minute:{key_id}:{current_time // 60}"
    minute_count = redis_client.get(minute_key) or 0
    
    if int(minute_count) >= api_key.rate_limit_per_minute:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded: too many requests per minute"
        )
    
    # Check per-hour limit
    hour_key = f"rate_limit:hour:{key_id}:{current_time // 3600}"
    hour_count = redis_client.get(hour_key) or 0
    
    if int(hour_count) >= api_key.rate_limit_per_hour:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded: too many requests per hour"
        )
    
    # Check per-day limit
    day_key = f"rate_limit:day:{key_id}:{current_time // 86400}"
    day_count = redis_client.get(day_key) or 0
    
    if int(day_count) >= api_key.rate_limit_per_day:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded: too many requests per day"
        )
    
    # Increment counters
    pipe = redis_client.pipeline()
    pipe.incr(minute_key)
    pipe.expire(minute_key, 60)
    pipe.incr(hour_key)
    pipe.expire(hour_key, 3600)
    pipe.incr(day_key)
    pipe.expire(day_key, 86400)
    pipe.execute()


async def get_current_organization(
    api_key: APIKey = Depends(get_api_key_auth),
    db: AsyncSession = Depends(get_db)
) -> Organization:
    """Get current organization from API key"""
    result = await db.execute(
        select(Organization).where(
            Organization.id == api_key.organization_id,
            Organization.is_deleted == False
        )
    )
    organization = result.scalar_one_or_none()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    return organization


def require_role(required_role: str):
    """Dependency factory for role-based access control"""
    async def role_checker(current_user: User = Depends(get_current_user)):
        user_roles_hierarchy = {
            "viewer": 1,
            "member": 2,
            "admin": 3,
            "owner": 4
        }
        
        user_role_level = user_roles_hierarchy.get(current_user.role.value, 0)
        required_role_level = user_roles_hierarchy.get(required_role, 999)
        
        if user_role_level < required_role_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        return current_user
    
    return role_checker