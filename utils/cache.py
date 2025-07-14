"""
Redis caching utilities for LLM responses
"""
import os
import json
import hashlib
import redis
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# Cache TTL settings
DEFAULT_CACHE_TTL = int(os.getenv("CACHE_TTL_SECONDS", "3600"))  # 1 hour
LONG_CACHE_TTL = int(os.getenv("LONG_CACHE_TTL_SECONDS", "86400"))  # 24 hours

class RedisCache:
    """Redis cache manager for LLM responses"""
    
    def __init__(self):
        self.redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            password=REDIS_PASSWORD,
            decode_responses=True
        )
    
    def _generate_cache_key(self, prompt: str, model: str, **kwargs) -> str:
        """Generate a cache key for the request"""
        # Create a hash of the request parameters
        cache_data = {
            "prompt": prompt,
            "model": model,
            **kwargs
        }
        
        # Sort keys for consistent hashing
        cache_string = json.dumps(cache_data, sort_keys=True)
        cache_hash = hashlib.sha256(cache_string.encode()).hexdigest()
        
        return f"llm_cache:{cache_hash}"
    
    async def get(self, prompt: str, model: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Get cached response"""
        try:
            cache_key = self._generate_cache_key(prompt, model, **kwargs)
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            
            return None
            
        except Exception as e:
            # Log error but don't fail the request
            print(f"Cache get error: {e}")
            return None
    
    async def set(
        self, 
        prompt: str, 
        model: str, 
        response_data: Dict[str, Any], 
        ttl: int = DEFAULT_CACHE_TTL,
        **kwargs
    ) -> bool:
        """Cache response"""
        try:
            cache_key = self._generate_cache_key(prompt, model, **kwargs)
            
            # Add metadata to cached response
            cache_data = {
                **response_data,
                "cached_at": str(datetime.utcnow()),
                "cache_key": cache_key
            }
            
            self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(cache_data)
            )
            
            return True
            
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    async def delete(self, prompt: str, model: str, **kwargs) -> bool:
        """Delete cached response"""
        try:
            cache_key = self._generate_cache_key(prompt, model, **kwargs)
            self.redis_client.delete(cache_key)
            return True
            
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    async def clear_user_cache(self, organization_id: str) -> int:
        """Clear all cache for an organization"""
        try:
            pattern = f"llm_cache:*:org:{organization_id}:*"
            keys = self.redis_client.keys(pattern)
            
            if keys:
                return self.redis_client.delete(*keys)
            
            return 0
            
        except Exception as e:
            print(f"Cache clear error: {e}")
            return 0
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            info = self.redis_client.info('memory')
            keyspace = self.redis_client.info('keyspace')
            
            # Count LLM cache keys
            cache_keys = self.redis_client.keys("llm_cache:*")
            
            return {
                "total_keys": len(cache_keys),
                "memory_used": info.get('used_memory_human', '0'),
                "hit_rate": self._calculate_hit_rate(),
                "keyspace_info": keyspace
            }
            
        except Exception as e:
            print(f"Cache stats error: {e}")
            return {}
    
    def _calculate_hit_rate(self) -> float:
        """Calculate cache hit rate from Redis stats"""
        try:
            info = self.redis_client.info('stats')
            hits = info.get('keyspace_hits', 0)
            misses = info.get('keyspace_misses', 0)
            
            if hits + misses == 0:
                return 0.0
            
            return hits / (hits + misses) * 100
            
        except Exception:
            return 0.0
    
    def is_healthy(self) -> bool:
        """Check if Redis is healthy"""
        try:
            self.redis_client.ping()
            return True
        except Exception:
            return False


# Global cache instance
cache = RedisCache()


async def get_cached_response(prompt: str, model: str, **kwargs) -> Optional[Dict[str, Any]]:
    """Get cached LLM response"""
    return await cache.get(prompt, model, **kwargs)


async def cache_response(
    prompt: str, 
    model: str, 
    response_data: Dict[str, Any], 
    ttl: int = DEFAULT_CACHE_TTL,
    **kwargs
) -> bool:
    """Cache LLM response"""
    return await cache.set(prompt, model, response_data, ttl, **kwargs)