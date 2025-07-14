"""
Prometheus metrics for monitoring LLM Gateway
"""
import time
from prometheus_client import Counter, Histogram, Gauge, Summary
from typing import Dict, Any

# Request metrics
REQUEST_COUNT = Counter(
    'llm_gateway_requests_total',
    'Total number of LLM requests',
    ['organization_id', 'provider', 'model', 'status']
)

REQUEST_DURATION = Histogram(
    'llm_gateway_request_duration_seconds',
    'Request duration in seconds',
    ['organization_id', 'provider', 'model']
)

TOKEN_COUNT = Counter(
    'llm_gateway_tokens_total',
    'Total tokens processed',
    ['organization_id', 'provider', 'model', 'type']  # type: input/output
)

COST_TOTAL = Counter(
    'llm_gateway_cost_usd_total',
    'Total cost in USD',
    ['organization_id', 'provider', 'model']
)

# Cache metrics
CACHE_HITS = Counter(
    'llm_gateway_cache_hits_total',
    'Total cache hits',
    ['organization_id']
)

CACHE_MISSES = Counter(
    'llm_gateway_cache_misses_total',
    'Total cache misses',
    ['organization_id']
)

# Rate limiting metrics
RATE_LIMIT_EXCEEDED = Counter(
    'llm_gateway_rate_limit_exceeded_total',
    'Total rate limit exceeded events',
    ['organization_id', 'limit_type']  # limit_type: minute/hour/day
)

# Provider health metrics
PROVIDER_HEALTH = Gauge(
    'llm_gateway_provider_health',
    'Provider health status (1=healthy, 0=unhealthy)',
    ['provider']
)

PROVIDER_RESPONSE_TIME = Summary(
    'llm_gateway_provider_response_seconds',
    'Provider response time',
    ['provider', 'model']
)

# Organization metrics
ACTIVE_ORGANIZATIONS = Gauge(
    'llm_gateway_active_organizations',
    'Number of active organizations'
)

ACTIVE_API_KEYS = Gauge(
    'llm_gateway_active_api_keys',
    'Number of active API keys'
)

# Billing metrics
MONTHLY_USAGE = Gauge(
    'llm_gateway_monthly_usage',
    'Monthly usage metrics',
    ['organization_id', 'metric']  # metric: requests/tokens/cost
)


class MetricsCollector:
    """Metrics collection helper"""
    
    @staticmethod
    def record_request(
        organization_id: str,
        provider: str,
        model: str,
        status: str,
        duration_seconds: float,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
        cached: bool = False
    ):
        """Record a complete request with all metrics"""
        
        # Request count
        REQUEST_COUNT.labels(
            organization_id=organization_id,
            provider=provider,
            model=model,
            status=status
        ).inc()
        
        # Duration
        REQUEST_DURATION.labels(
            organization_id=organization_id,
            provider=provider,
            model=model
        ).observe(duration_seconds)
        
        # Tokens
        TOKEN_COUNT.labels(
            organization_id=organization_id,
            provider=provider,
            model=model,
            type="input"
        ).inc(input_tokens)
        
        TOKEN_COUNT.labels(
            organization_id=organization_id,
            provider=provider,
            model=model,
            type="output"
        ).inc(output_tokens)
        
        # Cost (only for non-cached responses)
        if not cached:
            COST_TOTAL.labels(
                organization_id=organization_id,
                provider=provider,
                model=model
            ).inc(cost_usd)
        
        # Cache metrics
        if cached:
            CACHE_HITS.labels(organization_id=organization_id).inc()
        else:
            CACHE_MISSES.labels(organization_id=organization_id).inc()
    
    @staticmethod
    def record_rate_limit_exceeded(organization_id: str, limit_type: str):
        """Record rate limit exceeded event"""
        RATE_LIMIT_EXCEEDED.labels(
            organization_id=organization_id,
            limit_type=limit_type
        ).inc()
    
    @staticmethod
    def update_provider_health(provider: str, healthy: bool):
        """Update provider health status"""
        PROVIDER_HEALTH.labels(provider=provider).set(1 if healthy else 0)
    
    @staticmethod
    def record_provider_response_time(provider: str, model: str, response_time: float):
        """Record provider response time"""
        PROVIDER_RESPONSE_TIME.labels(
            provider=provider,
            model=model
        ).observe(response_time)
    
    @staticmethod
    def update_organization_count(count: int):
        """Update active organization count"""
        ACTIVE_ORGANIZATIONS.set(count)
    
    @staticmethod
    def update_api_key_count(count: int):
        """Update active API key count"""
        ACTIVE_API_KEYS.set(count)
    
    @staticmethod
    def update_monthly_usage(organization_id: str, requests: int, tokens: int, cost: float):
        """Update monthly usage metrics"""
        MONTHLY_USAGE.labels(
            organization_id=organization_id,
            metric="requests"
        ).set(requests)
        
        MONTHLY_USAGE.labels(
            organization_id=organization_id,
            metric="tokens"
        ).set(tokens)
        
        MONTHLY_USAGE.labels(
            organization_id=organization_id,
            metric="cost"
        ).set(cost)


# Global metrics collector instance
metrics = MetricsCollector()