"""
Throttler - Phase 2.2: Budget Management System
Implements intelligent throttling based on budget constraints and usage patterns.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class ThrottleAction(Enum):
    """Actions that can be taken when throttling."""
    ALLOW = "allow"
    DELAY = "delay"
    REJECT = "reject"
    DOWNGRADE = "downgrade"


class ThrottleReason(Enum):
    """Reasons for throttling."""
    BUDGET_EXCEEDED = "budget_exceeded"
    BUDGET_THRESHOLD = "budget_threshold"
    RATE_LIMIT = "rate_limit"
    COST_SPIKE = "cost_spike"
    PROVIDER_LIMIT = "provider_limit"
    QUALITY_LIMIT = "quality_limit"


@dataclass
class ThrottleConfig:
    """Configuration for throttling behavior."""
    organization_id: str
    enabled: bool
    budget_threshold: float  # Percentage at which to start throttling
    rate_limit_requests: int  # Max requests per minute
    rate_limit_tokens: int  # Max tokens per minute
    cost_spike_threshold: float  # Percentage increase that triggers throttling
    downgrade_models: Dict[str, str]  # model_id -> cheaper_model_id
    delay_base_ms: int  # Base delay in milliseconds
    delay_backoff_multiplier: float  # Backoff multiplier for repeated delays
    max_delay_ms: int  # Maximum delay in milliseconds
    rejection_threshold: float  # Budget percentage at which to reject requests
    created_at: datetime
    updated_at: datetime


@dataclass
class ThrottleDecision:
    """Decision made by throttler."""
    action: ThrottleAction
    reason: ThrottleReason
    delay_ms: int
    alternative_model: Optional[str]
    estimated_cost_savings: float
    message: str
    confidence: float  # 0.0 to 1.0
    metadata: Dict[str, Any]


@dataclass
class ThrottleStats:
    """Statistics about throttling decisions."""
    organization_id: str
    period_start: datetime
    period_end: datetime
    total_requests: int
    allowed_requests: int
    delayed_requests: int
    rejected_requests: int
    downgraded_requests: int
    total_delay_ms: int
    cost_savings: float
    avg_delay_ms: float
    throttle_reasons: Dict[str, int]  # reason -> count


class RequestWindow:
    """Sliding window for request tracking."""
    
    def __init__(self, window_size_seconds: int = 60):
        self.window_size = window_size_seconds
        self.requests = deque()
        self.tokens = deque()
        self.costs = deque()
    
    def add_request(self, tokens: int, cost: float):
        """Add a request to the window."""
        now = time.time()
        self.requests.append(now)
        self.tokens.append((now, tokens))
        self.costs.append((now, cost))
        self._cleanup_old_entries(now)
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current window statistics."""
        now = time.time()
        self._cleanup_old_entries(now)
        
        total_tokens = sum(tokens for _, tokens in self.tokens)
        total_cost = sum(cost for _, cost in self.costs)
        
        return {
            "requests": len(self.requests),
            "tokens": total_tokens,
            "cost": total_cost,
            "requests_per_minute": len(self.requests) * (60 / self.window_size),
            "tokens_per_minute": total_tokens * (60 / self.window_size),
            "cost_per_minute": total_cost * (60 / self.window_size)
        }
    
    def _cleanup_old_entries(self, now: float):
        """Remove entries older than window size."""
        cutoff = now - self.window_size
        
        while self.requests and self.requests[0] < cutoff:
            self.requests.popleft()
        
        while self.tokens and self.tokens[0][0] < cutoff:
            self.tokens.popleft()
        
        while self.costs and self.costs[0][0] < cutoff:
            self.costs.popleft()


class Throttler:
    """
    Intelligent throttling system with multiple strategies.
    
    Chain of thought:
    1. Monitor budget usage and request patterns
    2. Implement multiple throttling strategies (delay, reject, downgrade)
    3. Use sliding windows for rate limiting
    4. Detect cost spikes and unusual patterns
    5. Provide alternatives when throttling is needed
    """
    
    def __init__(self):
        """Initialize throttler with default settings."""
        self.logger = logging.getLogger(__name__)
        
        # Throttle configurations per organization
        self.throttle_configs: Dict[str, ThrottleConfig] = {}
        
        # Request tracking windows
        self.request_windows: Dict[str, RequestWindow] = {}
        
        # Throttle statistics
        self.throttle_stats: Dict[str, ThrottleStats] = {}
        
        # Delay tracking for backoff
        self.delay_history: Dict[str, List[float]] = defaultdict(list)
        
        # Cost baseline for spike detection
        self.cost_baselines: Dict[str, float] = {}
        
        self.logger.info("Throttler initialized")
    
    def set_throttle_config(self, config: ThrottleConfig):
        """Set throttle configuration for an organization."""
        self.throttle_configs[config.organization_id] = config
        
        # Initialize request window
        if config.organization_id not in self.request_windows:
            self.request_windows[config.organization_id] = RequestWindow()
        
        # Initialize stats
        if config.organization_id not in self.throttle_stats:
            self.throttle_stats[config.organization_id] = ThrottleStats(
                organization_id=config.organization_id,
                period_start=datetime.now(),
                period_end=datetime.now() + timedelta(days=1),
                total_requests=0,
                allowed_requests=0,
                delayed_requests=0,
                rejected_requests=0,
                downgraded_requests=0,
                total_delay_ms=0,
                cost_savings=0.0,
                avg_delay_ms=0.0,
                throttle_reasons=defaultdict(int)
            )
        
        self.logger.info(f"Set throttle config for organization {config.organization_id}")
    
    async def should_throttle(
        self,
        organization_id: str,
        estimated_cost: float,
        estimated_tokens: int,
        model_id: str,
        current_budget_usage: float,
        budget_total: float
    ) -> ThrottleDecision:
        """
        Determine if request should be throttled.
        
        Args:
            organization_id: Organization identifier
            estimated_cost: Estimated cost of the request
            estimated_tokens: Estimated tokens for the request
            model_id: Model being requested
            current_budget_usage: Current budget usage amount
            budget_total: Total budget amount
            
        Returns:
            ThrottleDecision with action to take
        """
        try:
            # Get throttle configuration
            config = self.throttle_configs.get(organization_id)
            if not config or not config.enabled:
                return ThrottleDecision(
                    action=ThrottleAction.ALLOW,
                    reason=ThrottleReason.BUDGET_THRESHOLD,
                    delay_ms=0,
                    alternative_model=None,
                    estimated_cost_savings=0.0,
                    message="Throttling not enabled",
                    confidence=1.0,
                    metadata={}
                )
            
            # Get request window
            window = self.request_windows.get(organization_id)
            if not window:
                window = RequestWindow()
                self.request_windows[organization_id] = window
            
            # Calculate current usage percentage
            usage_percentage = (current_budget_usage / budget_total) * 100
            
            # Check different throttling conditions
            decisions = []
            
            # 1. Budget-based throttling
            budget_decision = await self._check_budget_throttling(
                config, usage_percentage, estimated_cost, model_id
            )
            decisions.append(budget_decision)
            
            # 2. Rate limiting
            rate_decision = await self._check_rate_limiting(
                config, window, estimated_tokens
            )
            decisions.append(rate_decision)
            
            # 3. Cost spike detection
            spike_decision = await self._check_cost_spike(
                organization_id, config, estimated_cost, window
            )
            decisions.append(spike_decision)
            
            # Select the most restrictive decision
            final_decision = self._select_most_restrictive_decision(decisions)
            
            # Update statistics
            await self._update_throttle_stats(organization_id, final_decision)
            
            self.logger.debug(f"Throttle decision for {organization_id}: {final_decision.action.value}")
            return final_decision
            
        except Exception as e:
            self.logger.error(f"Error in throttle decision for {organization_id}: {str(e)}")
            return ThrottleDecision(
                action=ThrottleAction.ALLOW,
                reason=ThrottleReason.BUDGET_THRESHOLD,
                delay_ms=0,
                alternative_model=None,
                estimated_cost_savings=0.0,
                message="Error in throttling logic",
                confidence=0.0,
                metadata={"error": str(e)}
            )
    
    async def _check_budget_throttling(
        self,
        config: ThrottleConfig,
        usage_percentage: float,
        estimated_cost: float,
        model_id: str
    ) -> ThrottleDecision:
        """Check if budget-based throttling is needed."""
        # Check rejection threshold
        if usage_percentage >= config.rejection_threshold:
            return ThrottleDecision(
                action=ThrottleAction.REJECT,
                reason=ThrottleReason.BUDGET_EXCEEDED,
                delay_ms=0,
                alternative_model=None,
                estimated_cost_savings=estimated_cost,
                message=f"Budget usage at {usage_percentage:.1f}%, exceeds rejection threshold",
                confidence=0.95,
                metadata={"usage_percentage": usage_percentage}
            )
        
        # Check downgrade threshold
        if usage_percentage >= config.budget_threshold:
            alternative_model = config.downgrade_models.get(model_id)
            if alternative_model:
                # Estimate cost savings from downgrade
                cost_savings = estimated_cost * 0.5  # Assume 50% savings
                
                return ThrottleDecision(
                    action=ThrottleAction.DOWNGRADE,
                    reason=ThrottleReason.BUDGET_THRESHOLD,
                    delay_ms=0,
                    alternative_model=alternative_model,
                    estimated_cost_savings=cost_savings,
                    message=f"Budget usage at {usage_percentage:.1f}%, downgrading to {alternative_model}",
                    confidence=0.8,
                    metadata={"usage_percentage": usage_percentage, "savings": cost_savings}
                )
            else:
                # No downgrade available, add delay
                delay_ms = self._calculate_delay(config, usage_percentage)
                
                return ThrottleDecision(
                    action=ThrottleAction.DELAY,
                    reason=ThrottleReason.BUDGET_THRESHOLD,
                    delay_ms=delay_ms,
                    alternative_model=None,
                    estimated_cost_savings=0.0,
                    message=f"Budget usage at {usage_percentage:.1f}%, adding {delay_ms}ms delay",
                    confidence=0.7,
                    metadata={"usage_percentage": usage_percentage}
                )
        
        # No throttling needed
        return ThrottleDecision(
            action=ThrottleAction.ALLOW,
            reason=ThrottleReason.BUDGET_THRESHOLD,
            delay_ms=0,
            alternative_model=None,
            estimated_cost_savings=0.0,
            message="Budget usage within acceptable range",
            confidence=1.0,
            metadata={"usage_percentage": usage_percentage}
        )
    
    async def _check_rate_limiting(
        self,
        config: ThrottleConfig,
        window: RequestWindow,
        estimated_tokens: int
    ) -> ThrottleDecision:
        """Check if rate limiting is needed."""
        current_stats = window.get_current_stats()
        
        # Check request rate limit
        if current_stats["requests_per_minute"] >= config.rate_limit_requests:
            delay_ms = self._calculate_rate_limit_delay(config, current_stats["requests_per_minute"])
            
            return ThrottleDecision(
                action=ThrottleAction.DELAY,
                reason=ThrottleReason.RATE_LIMIT,
                delay_ms=delay_ms,
                alternative_model=None,
                estimated_cost_savings=0.0,
                message=f"Request rate limit exceeded: {current_stats['requests_per_minute']:.1f}/min",
                confidence=0.9,
                metadata={"current_rate": current_stats["requests_per_minute"]}
            )
        
        # Check token rate limit
        potential_tokens = current_stats["tokens_per_minute"] + estimated_tokens
        if potential_tokens >= config.rate_limit_tokens:
            delay_ms = self._calculate_rate_limit_delay(config, potential_tokens / config.rate_limit_tokens)
            
            return ThrottleDecision(
                action=ThrottleAction.DELAY,
                reason=ThrottleReason.RATE_LIMIT,
                delay_ms=delay_ms,
                alternative_model=None,
                estimated_cost_savings=0.0,
                message=f"Token rate limit exceeded: {potential_tokens}/min",
                confidence=0.9,
                metadata={"current_tokens": current_stats["tokens_per_minute"]}
            )
        
        # No rate limiting needed
        return ThrottleDecision(
            action=ThrottleAction.ALLOW,
            reason=ThrottleReason.RATE_LIMIT,
            delay_ms=0,
            alternative_model=None,
            estimated_cost_savings=0.0,
            message="Rate limits not exceeded",
            confidence=1.0,
            metadata={}
        )
    
    async def _check_cost_spike(
        self,
        organization_id: str,
        config: ThrottleConfig,
        estimated_cost: float,
        window: RequestWindow
    ) -> ThrottleDecision:
        """Check for cost spikes that might indicate unusual usage."""
        current_stats = window.get_current_stats()
        
        # Get baseline cost per minute
        baseline = self.cost_baselines.get(organization_id, 0.0)
        current_cost_rate = current_stats["cost_per_minute"]
        
        # Calculate spike percentage
        if baseline > 0:
            spike_percentage = ((current_cost_rate - baseline) / baseline) * 100
        else:
            spike_percentage = 0.0
        
        # Check if spike threshold is exceeded
        if spike_percentage >= config.cost_spike_threshold:
            delay_ms = self._calculate_spike_delay(config, spike_percentage)
            
            return ThrottleDecision(
                action=ThrottleAction.DELAY,
                reason=ThrottleReason.COST_SPIKE,
                delay_ms=delay_ms,
                alternative_model=None,
                estimated_cost_savings=0.0,
                message=f"Cost spike detected: {spike_percentage:.1f}% above baseline",
                confidence=0.6,
                metadata={"spike_percentage": spike_percentage, "baseline": baseline}
            )
        
        # Update baseline (exponential moving average)
        alpha = 0.1  # Smoothing factor
        self.cost_baselines[organization_id] = alpha * current_cost_rate + (1 - alpha) * baseline
        
        return ThrottleDecision(
            action=ThrottleAction.ALLOW,
            reason=ThrottleReason.COST_SPIKE,
            delay_ms=0,
            alternative_model=None,
            estimated_cost_savings=0.0,
            message="No cost spike detected",
            confidence=1.0,
            metadata={}
        )
    
    def _select_most_restrictive_decision(self, decisions: List[ThrottleDecision]) -> ThrottleDecision:
        """Select the most restrictive decision from a list."""
        # Priority order: REJECT > DOWNGRADE > DELAY > ALLOW
        action_priority = {
            ThrottleAction.REJECT: 4,
            ThrottleAction.DOWNGRADE: 3,
            ThrottleAction.DELAY: 2,
            ThrottleAction.ALLOW: 1
        }
        
        # Sort by priority (highest first)
        decisions.sort(key=lambda d: action_priority[d.action], reverse=True)
        
        most_restrictive = decisions[0]
        
        # If multiple delays, use the maximum delay
        if most_restrictive.action == ThrottleAction.DELAY:
            max_delay = max(d.delay_ms for d in decisions if d.action == ThrottleAction.DELAY)
            most_restrictive.delay_ms = max_delay
        
        return most_restrictive
    
    def _calculate_delay(self, config: ThrottleConfig, usage_percentage: float) -> int:
        """Calculate delay based on usage percentage."""
        # Linear increase in delay based on usage
        excess_percentage = usage_percentage - config.budget_threshold
        delay_factor = excess_percentage / (100 - config.budget_threshold)
        
        base_delay = config.delay_base_ms
        calculated_delay = int(base_delay * (1 + delay_factor * config.delay_backoff_multiplier))
        
        return min(calculated_delay, config.max_delay_ms)
    
    def _calculate_rate_limit_delay(self, config: ThrottleConfig, excess_factor: float) -> int:
        """Calculate delay for rate limiting."""
        # Exponential backoff for rate limiting
        delay_ms = int(config.delay_base_ms * (excess_factor ** 1.5))
        return min(delay_ms, config.max_delay_ms)
    
    def _calculate_spike_delay(self, config: ThrottleConfig, spike_percentage: float) -> int:
        """Calculate delay for cost spikes."""
        # Logarithmic delay for cost spikes
        import math
        delay_factor = math.log(1 + spike_percentage / 100)
        delay_ms = int(config.delay_base_ms * delay_factor)
        return min(delay_ms, config.max_delay_ms)
    
    async def _update_throttle_stats(self, organization_id: str, decision: ThrottleDecision):
        """Update throttle statistics."""
        stats = self.throttle_stats.get(organization_id)
        if not stats:
            return
        
        stats.total_requests += 1
        
        if decision.action == ThrottleAction.ALLOW:
            stats.allowed_requests += 1
        elif decision.action == ThrottleAction.DELAY:
            stats.delayed_requests += 1
            stats.total_delay_ms += decision.delay_ms
        elif decision.action == ThrottleAction.REJECT:
            stats.rejected_requests += 1
            stats.cost_savings += decision.estimated_cost_savings
        elif decision.action == ThrottleAction.DOWNGRADE:
            stats.downgraded_requests += 1
            stats.cost_savings += decision.estimated_cost_savings
        
        stats.throttle_reasons[decision.reason.value] += 1
        
        # Update average delay
        if stats.delayed_requests > 0:
            stats.avg_delay_ms = stats.total_delay_ms / stats.delayed_requests
    
    async def record_request(self, organization_id: str, tokens: int, cost: float):
        """Record a completed request for tracking."""
        window = self.request_windows.get(organization_id)
        if window:
            window.add_request(tokens, cost)
    
    def get_throttle_stats(self, organization_id: str) -> Optional[ThrottleStats]:
        """Get throttle statistics for an organization."""
        return self.throttle_stats.get(organization_id)
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get overall throttling statistics."""
        total_orgs = len(self.throttle_stats)
        total_requests = sum(stats.total_requests for stats in self.throttle_stats.values())
        total_savings = sum(stats.cost_savings for stats in self.throttle_stats.values())
        
        return {
            "total_organizations": total_orgs,
            "total_requests": total_requests,
            "total_cost_savings": total_savings,
            "organizations": {
                org_id: {
                    "total_requests": stats.total_requests,
                    "throttle_rate": (stats.total_requests - stats.allowed_requests) / max(stats.total_requests, 1),
                    "cost_savings": stats.cost_savings,
                    "avg_delay_ms": stats.avg_delay_ms
                }
                for org_id, stats in self.throttle_stats.items()
            }
        }