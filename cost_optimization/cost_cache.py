"""
Cost Cache - Phase 2.3: Cost-aware Caching
Intelligent caching system that considers cost savings in cache decisions.
"""

import asyncio
import hashlib
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging
from collections import OrderedDict

logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """Cache strategies based on cost optimization."""
    COST_AWARE = "cost_aware"  # Cache based on cost savings
    FREQUENCY_BASED = "frequency_based"  # Cache based on access frequency
    HYBRID = "hybrid"  # Combine cost and frequency
    QUALITY_AWARE = "quality_aware"  # Consider response quality


@dataclass
class CacheEntry:
    """Cached response with cost metadata."""
    key: str
    prompt_hash: str
    response_content: str
    model_id: str
    provider: str
    original_cost: float
    tokens_used: int
    quality_score: float
    created_at: datetime
    last_accessed: datetime
    access_count: int
    cumulative_savings: float
    expiry_time: Optional[datetime]
    metadata: Dict[str, Any]


@dataclass
class CacheMetrics:
    """Metrics for cache performance."""
    total_requests: int
    cache_hits: int
    cache_misses: int
    hit_rate: float
    total_cost_savings: float
    avg_cost_per_hit: float
    avg_cost_per_miss: float
    storage_cost: float
    net_savings: float
    quality_improvement: float


@dataclass
class CostSavingsCalculation:
    """Detailed cost savings calculation."""
    original_cost: float
    cache_storage_cost: float
    retrieval_cost: float
    net_savings: float
    savings_percentage: float
    break_even_accesses: int
    current_accesses: int
    profitability_score: float


class CostCache:
    """
    Cost-aware caching system with intelligent eviction.
    
    Chain of thought:
    1. Cache decisions based on cost savings potential
    2. Prioritize expensive responses for caching
    3. Implement cost-aware eviction policies
    4. Track cumulative savings and ROI
    5. Balance storage costs vs. computation costs
    """
    
    def __init__(self, max_size: int = 10000, storage_cost_per_mb: float = 0.001):
        """Initialize cost-aware cache."""
        self.logger = logging.getLogger(__name__)
        self.max_size = max_size
        self.storage_cost_per_mb = storage_cost_per_mb
        
        # Cache storage
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        
        # Cost tracking
        self.metrics = CacheMetrics(
            total_requests=0,
            cache_hits=0,
            cache_misses=0,
            hit_rate=0.0,
            total_cost_savings=0.0,
            avg_cost_per_hit=0.0,
            avg_cost_per_miss=0.0,
            storage_cost=0.0,
            net_savings=0.0,
            quality_improvement=0.0
        )
        
        # Cache strategy
        self.strategy = CacheStrategy.COST_AWARE
        
        # Cost thresholds
        self.min_cost_threshold = 0.001  # Minimum cost to consider caching
        self.max_storage_ratio = 0.1  # Max storage cost as ratio of original cost
        
        # Quality thresholds
        self.min_quality_score = 0.7  # Minimum quality to cache
        
        # Eviction parameters
        self.eviction_batch_size = 100  # Number of items to evict at once
        
        self.logger.info(f"CostCache initialized with max_size={max_size}")
    
    async def get(self, prompt: str, model_id: str, provider: str, **kwargs) -> Optional[CacheEntry]:
        """
        Get cached response if available and cost-effective.
        
        Args:
            prompt: Input prompt
            model_id: Model identifier
            provider: Provider name
            **kwargs: Additional parameters affecting cache key
            
        Returns:
            CacheEntry if found and cost-effective, None otherwise
        """
        try:
            # Generate cache key
            cache_key = self._generate_cache_key(prompt, model_id, provider, **kwargs)
            
            self.metrics.total_requests += 1
            
            # Check if entry exists
            if cache_key not in self.cache:
                self.metrics.cache_misses += 1
                return None
            
            entry = self.cache[cache_key]
            
            # Check expiry
            if entry.expiry_time and datetime.now() > entry.expiry_time:
                del self.cache[cache_key]
                self.metrics.cache_misses += 1
                return None
            
            # Update access metrics
            entry.last_accessed = datetime.now()
            entry.access_count += 1
            
            # Move to end (most recently used)
            self.cache.move_to_end(cache_key)
            
            # Calculate cost savings for this hit
            savings = self._calculate_hit_savings(entry)
            entry.cumulative_savings += savings
            
            # Update metrics
            self.metrics.cache_hits += 1
            self.metrics.total_cost_savings += savings
            self.metrics.hit_rate = self.metrics.cache_hits / self.metrics.total_requests
            
            self.logger.debug(f"Cache hit for {model_id}: saved ${savings:.6f}")
            return entry
            
        except Exception as e:
            self.logger.error(f"Error retrieving from cache: {str(e)}")
            return None
    
    async def put(
        self,
        prompt: str,
        response: str,
        model_id: str,
        provider: str,
        cost: float,
        tokens: int,
        quality_score: float = 1.0,
        ttl_seconds: Optional[int] = None,
        **kwargs
    ) -> bool:
        """
        Store response in cache if cost-effective.
        
        Args:
            prompt: Input prompt
            response: Model response
            model_id: Model identifier
            provider: Provider name
            cost: Cost of generating the response
            tokens: Number of tokens used
            quality_score: Quality score (0.0 to 1.0)
            ttl_seconds: Time to live in seconds
            **kwargs: Additional parameters
            
        Returns:
            True if cached, False otherwise
        """
        try:
            # Check if worth caching
            if not self._should_cache(cost, quality_score, tokens):
                return False
            
            # Generate cache key
            cache_key = self._generate_cache_key(prompt, model_id, provider, **kwargs)
            prompt_hash = self._hash_prompt(prompt)
            
            # Calculate expiry
            expiry_time = None
            if ttl_seconds:
                expiry_time = datetime.now() + timedelta(seconds=ttl_seconds)
            
            # Create cache entry
            entry = CacheEntry(
                key=cache_key,
                prompt_hash=prompt_hash,
                response_content=response,
                model_id=model_id,
                provider=provider,
                original_cost=cost,
                tokens_used=tokens,
                quality_score=quality_score,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=0,
                cumulative_savings=0.0,
                expiry_time=expiry_time,
                metadata=kwargs
            )
            
            # Check if cache is full
            if len(self.cache) >= self.max_size:
                await self._evict_entries()
            
            # Store entry
            self.cache[cache_key] = entry
            
            # Update storage cost
            self._update_storage_cost()
            
            self.logger.debug(f"Cached response for {model_id}: cost=${cost:.6f}, tokens={tokens}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error storing in cache: {str(e)}")
            return False
    
    def _should_cache(self, cost: float, quality_score: float, tokens: int) -> bool:
        """
        Determine if response should be cached based on cost and quality.
        
        Chain of thought:
        1. Only cache if cost exceeds minimum threshold
        2. Consider quality score (don't cache low-quality responses)
        3. Estimate storage cost vs. potential savings
        4. Account for expected access frequency
        """
        # Check minimum cost threshold
        if cost < self.min_cost_threshold:
            return False
        
        # Check quality threshold
        if quality_score < self.min_quality_score:
            return False
        
        # Estimate storage cost
        response_size_mb = tokens * 4 / 1024 / 1024  # Rough estimate: 4 bytes per token
        storage_cost = response_size_mb * self.storage_cost_per_mb
        
        # Check storage cost ratio
        if storage_cost / cost > self.max_storage_ratio:
            return False
        
        # Additional strategy-specific checks
        if self.strategy == CacheStrategy.COST_AWARE:
            # Cost-aware: prioritize expensive responses
            return cost > self.min_cost_threshold * 2
        
        elif self.strategy == CacheStrategy.QUALITY_AWARE:
            # Quality-aware: prioritize high-quality responses
            return quality_score > 0.8
        
        elif self.strategy == CacheStrategy.HYBRID:
            # Hybrid: balance cost and quality
            score = (cost / self.min_cost_threshold) * quality_score
            return score > 1.5
        
        return True
    
    async def _evict_entries(self):
        """Evict cache entries using cost-aware policy."""
        if len(self.cache) < self.eviction_batch_size:
            return
        
        # Get entries sorted by profitability score
        entries_with_scores = []
        for key, entry in self.cache.items():
            score = self._calculate_profitability_score(entry)
            entries_with_scores.append((key, entry, score))
        
        # Sort by score (lowest first for eviction)
        entries_with_scores.sort(key=lambda x: x[2])
        
        # Evict lowest scoring entries
        evicted_count = 0
        for key, entry, score in entries_with_scores:
            if evicted_count >= self.eviction_batch_size:
                break
            
            # Don't evict recently accessed or highly profitable entries
            if entry.last_accessed > datetime.now() - timedelta(hours=1):
                continue
            
            if score > 2.0:  # High profitability threshold
                continue
            
            del self.cache[key]
            evicted_count += 1
        
        self.logger.info(f"Evicted {evicted_count} cache entries")
        self._update_storage_cost()
    
    def _calculate_profitability_score(self, entry: CacheEntry) -> float:
        """
        Calculate profitability score for cache entry.
        
        Higher score = more profitable to keep
        Lower score = candidate for eviction
        """
        # Base score from cumulative savings
        if entry.original_cost > 0:
            savings_ratio = entry.cumulative_savings / entry.original_cost
        else:
            savings_ratio = 0.0
        
        # Access frequency factor
        age_hours = (datetime.now() - entry.created_at).total_seconds() / 3600
        access_frequency = entry.access_count / max(age_hours, 1)
        
        # Recency factor
        hours_since_access = (datetime.now() - entry.last_accessed).total_seconds() / 3600
        recency_factor = max(0.1, 1.0 / (1.0 + hours_since_access))
        
        # Quality factor
        quality_factor = entry.quality_score
        
        # Storage cost factor
        storage_cost = self._estimate_entry_storage_cost(entry)
        if storage_cost > 0:
            storage_efficiency = entry.original_cost / storage_cost
        else:
            storage_efficiency = 1.0
        
        # Combine factors
        score = (
            savings_ratio * 2.0 +
            access_frequency * 1.5 +
            recency_factor * 1.0 +
            quality_factor * 0.5 +
            min(storage_efficiency, 10.0) * 0.3
        )
        
        return score
    
    def _calculate_hit_savings(self, entry: CacheEntry) -> float:
        """Calculate cost savings from cache hit."""
        # Savings = original cost - retrieval cost
        retrieval_cost = self._estimate_retrieval_cost(entry)
        return max(0.0, entry.original_cost - retrieval_cost)
    
    def _estimate_retrieval_cost(self, entry: CacheEntry) -> float:
        """Estimate cost of retrieving from cache."""
        # Negligible cost for cache retrieval
        return 0.0001
    
    def _estimate_entry_storage_cost(self, entry: CacheEntry) -> float:
        """Estimate storage cost for cache entry."""
        # Estimate based on response size
        response_size_mb = len(entry.response_content.encode('utf-8')) / 1024 / 1024
        return response_size_mb * self.storage_cost_per_mb
    
    def _update_storage_cost(self):
        """Update total storage cost."""
        total_storage_cost = sum(
            self._estimate_entry_storage_cost(entry)
            for entry in self.cache.values()
        )
        self.metrics.storage_cost = total_storage_cost
        self.metrics.net_savings = self.metrics.total_cost_savings - total_storage_cost
    
    def _generate_cache_key(self, prompt: str, model_id: str, provider: str, **kwargs) -> str:
        """Generate cache key from prompt and parameters."""
        # Create deterministic key
        key_data = {
            "prompt": prompt,
            "model_id": model_id,
            "provider": provider,
            **kwargs
        }
        
        # Sort keys for consistency
        sorted_data = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(sorted_data.encode()).hexdigest()
    
    def _hash_prompt(self, prompt: str) -> str:
        """Generate hash of prompt for deduplication."""
        return hashlib.md5(prompt.encode()).hexdigest()
    
    def calculate_cost_savings(self, entry: CacheEntry) -> CostSavingsCalculation:
        """Calculate detailed cost savings for cache entry."""
        storage_cost = self._estimate_entry_storage_cost(entry)
        retrieval_cost = self._estimate_retrieval_cost(entry)
        
        net_savings = entry.cumulative_savings - storage_cost
        
        if entry.original_cost > 0:
            savings_percentage = (net_savings / entry.original_cost) * 100
        else:
            savings_percentage = 0.0
        
        # Calculate break-even point
        cost_per_access = entry.original_cost - retrieval_cost
        if cost_per_access > 0:
            break_even_accesses = int(storage_cost / cost_per_access) + 1
        else:
            break_even_accesses = 1
        
        # Profitability score
        if break_even_accesses > 0:
            profitability_score = entry.access_count / break_even_accesses
        else:
            profitability_score = 0.0
        
        return CostSavingsCalculation(
            original_cost=entry.original_cost,
            cache_storage_cost=storage_cost,
            retrieval_cost=retrieval_cost,
            net_savings=net_savings,
            savings_percentage=savings_percentage,
            break_even_accesses=break_even_accesses,
            current_accesses=entry.access_count,
            profitability_score=profitability_score
        )
    
    def get_cache_stats(self) -> CacheMetrics:
        """Get current cache statistics."""
        # Update calculated metrics
        if self.metrics.total_requests > 0:
            self.metrics.hit_rate = self.metrics.cache_hits / self.metrics.total_requests
        
        if self.metrics.cache_hits > 0:
            self.metrics.avg_cost_per_hit = self.metrics.total_cost_savings / self.metrics.cache_hits
        
        if self.metrics.cache_misses > 0:
            # Estimate average cost per miss (would need actual data)
            self.metrics.avg_cost_per_miss = 0.01  # Placeholder
        
        # Update net savings
        self.metrics.net_savings = self.metrics.total_cost_savings - self.metrics.storage_cost
        
        return self.metrics
    
    def get_top_performers(self, limit: int = 10) -> List[Tuple[str, CacheEntry, CostSavingsCalculation]]:
        """Get top performing cache entries by cost savings."""
        performers = []
        
        for key, entry in self.cache.items():
            savings_calc = self.calculate_cost_savings(entry)
            performers.append((key, entry, savings_calc))
        
        # Sort by net savings (descending)
        performers.sort(key=lambda x: x[2].net_savings, reverse=True)
        
        return performers[:limit]
    
    def clear_expired(self):
        """Clear expired cache entries."""
        now = datetime.now()
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry.expiry_time and now > entry.expiry_time
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            self.logger.info(f"Cleared {len(expired_keys)} expired cache entries")
            self._update_storage_cost()
    
    def clear_low_quality(self, quality_threshold: float = 0.5):
        """Clear cache entries below quality threshold."""
        low_quality_keys = [
            key for key, entry in self.cache.items()
            if entry.quality_score < quality_threshold
        ]
        
        for key in low_quality_keys:
            del self.cache[key]
        
        if low_quality_keys:
            self.logger.info(f"Cleared {len(low_quality_keys)} low-quality cache entries")
            self._update_storage_cost()
    
    def export_cache_data(self) -> Dict[str, Any]:
        """Export cache data for analysis."""
        return {
            "cache_size": len(self.cache),
            "metrics": asdict(self.metrics),
            "entries": [
                {
                    "key": entry.key,
                    "model_id": entry.model_id,
                    "provider": entry.provider,
                    "original_cost": entry.original_cost,
                    "access_count": entry.access_count,
                    "cumulative_savings": entry.cumulative_savings,
                    "quality_score": entry.quality_score,
                    "created_at": entry.created_at.isoformat(),
                    "last_accessed": entry.last_accessed.isoformat()
                }
                for entry in self.cache.values()
            ]
        }