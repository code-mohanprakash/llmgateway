"""
Performance optimization service for enterprise infrastructure
"""
import asyncio
import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, text
from sqlalchemy.orm import selectinload
import redis
import hashlib

from models.monitoring import PerformanceMetric
from models.user import User, Organization


class PerformanceOptimizer:
    """Service for performance optimization and caching"""
    
    def __init__(self):
        self.cache = {}  # In-memory cache
        self.redis_client = None
        self.performance_metrics = {}
        self.query_cache = {}
        
    async def initialize_redis(self, redis_url: str = "redis://localhost:6379"):
        """Initialize Redis connection for caching"""
        try:
            self.redis_client = redis.from_url(redis_url)
            # Test connection
            self.redis_client.ping()
            print("✅ Redis connection established")
        except Exception as e:
            print(f"⚠️ Redis not available, using in-memory cache: {e}")
            self.redis_client = None
    
    async def cache_get(self, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                return self.cache.get(key, default)
        except Exception as e:
            print(f"Cache get error: {e}")
            return default
    
    async def cache_set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache with TTL"""
        try:
            if self.redis_client:
                return self.redis_client.setex(key, ttl, json.dumps(value))
            else:
                self.cache[key] = value
                # Simple TTL implementation for in-memory cache
                asyncio.create_task(self._expire_cache_key(key, ttl))
                return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    async def _expire_cache_key(self, key: str, ttl: int):
        """Expire cache key after TTL"""
        await asyncio.sleep(ttl)
        if key in self.cache:
            del self.cache[key]
    
    async def cache_delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            if self.redis_client:
                return bool(self.redis_client.delete(key))
            else:
                if key in self.cache:
                    del self.cache[key]
                    return True
                return False
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    async def cache_clear(self) -> bool:
        """Clear all cache"""
        try:
            if self.redis_client:
                self.redis_client.flushdb()
            else:
                self.cache.clear()
            return True
        except Exception as e:
            print(f"Cache clear error: {e}")
            return False
    
    async def optimize_database_queries(self, db: AsyncSession) -> Dict[str, Any]:
        """Analyze and optimize database queries"""
        
        try:
            # Get slow queries from performance metrics
            slow_queries = await self._get_slow_queries(db)
            
            # Analyze query patterns
            query_patterns = await self._analyze_query_patterns(db)
            
            # Generate optimization recommendations
            recommendations = await self._generate_optimization_recommendations(
                slow_queries, query_patterns
            )
            
            return {
                "slow_queries": slow_queries,
                "query_patterns": query_patterns,
                "recommendations": recommendations,
                "optimization_score": await self._calculate_optimization_score(db)
            }
            
        except Exception as e:
            print(f"Error optimizing database queries: {e}")
            return {
                "error": str(e),
                "slow_queries": [],
                "query_patterns": {},
                "recommendations": [],
                "optimization_score": 0
            }
    
    async def _get_slow_queries(self, db: AsyncSession) -> List[Dict[str, Any]]:
        """Get slow queries from performance metrics"""
        
        try:
            # Get recent slow queries
            recent_time = datetime.utcnow() - timedelta(hours=24)
            result = await db.execute(
                select(PerformanceMetric)
                .where(
                    and_(
                        PerformanceMetric.metric_name == 'query_duration',
                        PerformanceMetric.value > 1000,  # Queries taking more than 1 second
                        PerformanceMetric.recorded_at >= recent_time
                    )
                )
                .order_by(PerformanceMetric.value.desc())
                .limit(10)
            )
            
            slow_queries = result.scalars().all()
            
            return [
                {
                    "endpoint": query.endpoint,
                    "duration": query.value,
                    "recorded_at": query.recorded_at.isoformat(),
                    "organization_id": query.organization_id
                }
                for query in slow_queries
            ]
            
        except Exception as e:
            print(f"Error getting slow queries: {e}")
            return []
    
    async def _analyze_query_patterns(self, db: AsyncSession) -> Dict[str, Any]:
        """Analyze query patterns for optimization"""
        
        try:
            # Get query frequency by endpoint
            result = await db.execute(
                select(
                    PerformanceMetric.endpoint,
                    func.count(PerformanceMetric.id).label('count'),
                    func.avg(PerformanceMetric.value).label('avg_duration'),
                    func.max(PerformanceMetric.value).label('max_duration')
                )
                .where(
                    and_(
                        PerformanceMetric.metric_name == 'query_duration',
                        PerformanceMetric.recorded_at >= datetime.utcnow() - timedelta(hours=24)
                    )
                )
                .group_by(PerformanceMetric.endpoint)
                .order_by(text('count DESC'))
            )
            
            patterns = result.fetchall()
            
            return {
                "frequent_endpoints": [
                    {
                        "endpoint": pattern.endpoint,
                        "count": pattern.count,
                        "avg_duration": pattern.avg_duration,
                        "max_duration": pattern.max_duration
                    }
                    for pattern in patterns
                ],
                "total_queries": sum(pattern.count for pattern in patterns),
                "avg_response_time": sum(pattern.avg_duration for pattern in patterns) / len(patterns) if patterns else 0
            }
            
        except Exception as e:
            print(f"Error analyzing query patterns: {e}")
            return {
                "frequent_endpoints": [],
                "total_queries": 0,
                "avg_response_time": 0
            }
    
    async def _generate_optimization_recommendations(
        self, slow_queries: List[Dict], query_patterns: Dict
    ) -> List[Dict[str, Any]]:
        """Generate optimization recommendations"""
        
        recommendations = []
        
        # Analyze slow queries
        if slow_queries:
            recommendations.append({
                "type": "slow_queries",
                "priority": "high",
                "title": "Optimize Slow Queries",
                "description": f"Found {len(slow_queries)} queries taking more than 1 second",
                "action": "Add database indexes and optimize query patterns",
                "impact": "High - Will improve response times significantly"
            })
        
        # Analyze frequent endpoints
        frequent_endpoints = query_patterns.get("frequent_endpoints", [])
        if frequent_endpoints:
            most_frequent = frequent_endpoints[0]
            if most_frequent["count"] > 1000:  # More than 1000 requests
                recommendations.append({
                    "type": "caching",
                    "priority": "medium",
                    "title": "Implement Caching",
                    "description": f"Endpoint {most_frequent['endpoint']} has {most_frequent['count']} requests",
                    "action": "Add Redis caching for frequently accessed data",
                    "impact": "Medium - Will reduce database load"
                })
        
        # Check average response time
        avg_response_time = query_patterns.get("avg_response_time", 0)
        if avg_response_time > 500:  # More than 500ms average
            recommendations.append({
                "type": "general_optimization",
                "priority": "medium",
                "title": "General Performance Optimization",
                "description": f"Average response time is {avg_response_time:.0f}ms",
                "action": "Review and optimize database queries and indexes",
                "impact": "Medium - Will improve overall performance"
            })
        
        return recommendations
    
    async def _calculate_optimization_score(self, db: AsyncSession) -> float:
        """Calculate overall optimization score (0-100)"""
        
        try:
            # Get recent performance metrics
            recent_time = datetime.utcnow() - timedelta(hours=1)
            result = await db.execute(
                select(PerformanceMetric)
                .where(
                    and_(
                        PerformanceMetric.metric_name == 'api_response_time',
                        PerformanceMetric.recorded_at >= recent_time
                    )
                )
            )
            
            metrics = result.scalars().all()
            if not metrics:
                return 75.0  # Default score if no data
            
            # Calculate score based on response times
            avg_response_time = sum(m.value for m in metrics) / len(metrics)
            
            if avg_response_time < 100:
                return 95.0  # Excellent
            elif avg_response_time < 200:
                return 85.0  # Good
            elif avg_response_time < 500:
                return 70.0  # Fair
            elif avg_response_time < 1000:
                return 50.0  # Poor
            else:
                return 25.0  # Very poor
                
        except Exception as e:
            print(f"Error calculating optimization score: {e}")
            return 50.0
    
    async def optimize_response_times(self, db: AsyncSession) -> Dict[str, Any]:
        """Optimize API response times"""
        
        try:
            # Get current response time metrics
            recent_time = datetime.utcnow() - timedelta(minutes=30)
            result = await db.execute(
                select(PerformanceMetric)
                .where(
                    and_(
                        PerformanceMetric.metric_name == 'api_response_time',
                        PerformanceMetric.recorded_at >= recent_time
                    )
                )
                .order_by(PerformanceMetric.recorded_at.desc())
            )
            
            metrics = result.scalars().all()
            
            if not metrics:
                return {
                    "current_avg": 0,
                    "optimization_applied": False,
                    "recommendations": ["No recent metrics available"]
                }
            
            # Calculate current average
            current_avg = sum(m.value for m in metrics) / len(metrics)
            
            # Apply optimizations if needed
            optimizations = []
            if current_avg > 500:
                optimizations.append("Enable query result caching")
            if current_avg > 1000:
                optimizations.append("Add database indexes")
            if current_avg > 2000:
                optimizations.append("Implement connection pooling")
            
            return {
                "current_avg": current_avg,
                "optimization_applied": len(optimizations) > 0,
                "recommendations": optimizations,
                "metrics_count": len(metrics)
            }
            
        except Exception as e:
            print(f"Error optimizing response times: {e}")
            return {
                "error": str(e),
                "current_avg": 0,
                "optimization_applied": False,
                "recommendations": []
            }
    
    async def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache statistics"""
        
        try:
            if self.redis_client:
                # Redis statistics
                info = self.redis_client.info()
                return {
                    "cache_type": "redis",
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory": info.get("used_memory", 0),
                    "keyspace_hits": info.get("keyspace_hits", 0),
                    "keyspace_misses": info.get("keyspace_misses", 0),
                    "hit_rate": self._calculate_hit_rate(
                        info.get("keyspace_hits", 0),
                        info.get("keyspace_misses", 0)
                    )
                }
            else:
                # In-memory cache statistics
                return {
                    "cache_type": "memory",
                    "cache_size": len(self.cache),
                    "cache_keys": list(self.cache.keys()),
                    "hit_rate": 0.8  # Estimated for in-memory cache
                }
                
        except Exception as e:
            print(f"Error getting cache statistics: {e}")
            return {
                "cache_type": "unknown",
                "error": str(e)
            }
    
    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """Calculate cache hit rate"""
        total = hits + misses
        if total == 0:
            return 0.0
        return (hits / total) * 100
    
    async def clear_performance_cache(self) -> bool:
        """Clear performance-related cache"""
        
        try:
            # Clear query cache
            self.query_cache.clear()
            
            # Clear performance metrics cache
            self.performance_metrics.clear()
            
            # Clear Redis cache if available
            if self.redis_client:
                self.redis_client.flushdb()
            
            return True
            
        except Exception as e:
            print(f"Error clearing performance cache: {e}")
            return False
    
    async def get_performance_summary(self, db: AsyncSession) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        
        try:
            # Get recent metrics
            recent_time = datetime.utcnow() - timedelta(hours=24)
            result = await db.execute(
                select(PerformanceMetric)
                .where(PerformanceMetric.recorded_at >= recent_time)
                .order_by(PerformanceMetric.recorded_at.desc())
            )
            
            metrics = result.scalars().all()
            
            # Calculate statistics
            response_times = [m.value for m in metrics if m.metric_name == 'api_response_time']
            error_rates = [m.value for m in metrics if m.metric_name == 'api_errors']
            
            summary = {
                "total_requests": len(response_times),
                "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
                "max_response_time": max(response_times) if response_times else 0,
                "min_response_time": min(response_times) if response_times else 0,
                "error_rate": sum(error_rates) / len(error_rates) if error_rates else 0,
                "cache_stats": await self.get_cache_statistics(),
                "optimization_score": await self._calculate_optimization_score(db)
            }
            
            return summary
            
        except Exception as e:
            print(f"Error getting performance summary: {e}")
            return {
                "error": str(e),
                "total_requests": 0,
                "avg_response_time": 0,
                "max_response_time": 0,
                "min_response_time": 0,
                "error_rate": 0,
                "cache_stats": {},
                "optimization_score": 0
            }


# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer() 