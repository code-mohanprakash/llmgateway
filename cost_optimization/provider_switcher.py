"""
Provider Switcher - Phase 2.4: Provider Cost Arbitrage
Handles seamless provider switching for arbitrage execution.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging
from contextlib import asynccontextmanager

from .arbitrage import ArbitrageOpportunity, ArbitrageExecution

logger = logging.getLogger(__name__)


class SwitchingStrategy(Enum):
    """Strategies for provider switching."""
    IMMEDIATE = "immediate"  # Switch immediately
    GRADUAL = "gradual"  # Gradually increase traffic to new provider
    CANARY = "canary"  # Test with small percentage first
    FALLBACK = "fallback"  # Switch only if primary fails


class SwitchingMode(Enum):
    """Modes for provider switching."""
    MANUAL = "manual"  # Manual approval required
    AUTOMATIC = "automatic"  # Automatic switching based on rules
    HYBRID = "hybrid"  # Automatic for low-risk, manual for high-risk


@dataclass
class SwitchingRule:
    """Rule for automatic provider switching."""
    rule_id: str
    min_savings_percentage: float
    max_quality_degradation: float
    max_speed_degradation: float
    min_confidence: float
    enabled: bool
    strategy: SwitchingStrategy
    test_percentage: float  # For canary/gradual strategies
    created_at: datetime
    updated_at: datetime


@dataclass
class SwitchingContext:
    """Context for provider switching operation."""
    request_id: str
    original_provider: str
    original_model: str
    target_provider: str
    target_model: str
    prompt: str
    estimated_savings: float
    quality_impact: float
    speed_impact: float
    switching_reason: str
    metadata: Dict[str, Any]


@dataclass
class SwitchingResult:
    """Result of provider switching operation."""
    success: bool
    original_provider: str
    original_model: str
    actual_provider: str
    actual_model: str
    original_cost: float
    actual_cost: float
    actual_savings: float
    quality_score: float
    response_time: float
    error_message: Optional[str]
    switched_at: datetime
    completed_at: datetime
    metadata: Dict[str, Any]


class ProviderSwitcher:
    """
    Advanced provider switching system with intelligent fallback.
    
    Chain of thought:
    1. Evaluate switching opportunities against rules
    2. Implement different switching strategies
    3. Handle failures gracefully with fallback
    4. Monitor switching performance
    5. Optimize switching rules based on results
    """
    
    def __init__(self, model_bridge):
        """Initialize provider switcher."""
        self.logger = logging.getLogger(__name__)
        self.model_bridge = model_bridge
        
        # Switching configuration
        self.switching_rules: List[SwitchingRule] = []
        self.switching_mode = SwitchingMode.HYBRID
        self.default_strategy = SwitchingStrategy.IMMEDIATE
        
        # Performance tracking
        self.switching_results: List[SwitchingResult] = []
        self.provider_performance: Dict[str, Dict[str, float]] = {}
        
        # Circuit breaker for problematic providers
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        
        # Fallback chains
        self.fallback_chains: Dict[str, List[str]] = {
            "openai": ["anthropic", "google", "groq"],
            "anthropic": ["openai", "google", "cohere"],
            "google": ["openai", "anthropic", "mistral"],
            "groq": ["openai", "together", "ollama"],
            "together": ["groq", "openai", "mistral"],
            "mistral": ["google", "together", "groq"],
            "cohere": ["anthropic", "openai", "google"],
            "perplexity": ["openai", "anthropic", "google"],
            "ollama": ["groq", "together", "openai"],
            "openrouter": ["openai", "anthropic", "google"]
        }
        
        # Initialize default rules
        self._initialize_default_rules()
        
        self.logger.info("ProviderSwitcher initialized")
    
    def _initialize_default_rules(self):
        """Initialize default switching rules."""
        # Conservative rule for high-value requests
        conservative_rule = SwitchingRule(
            rule_id="conservative_switching",
            min_savings_percentage=20.0,
            max_quality_degradation=0.05,
            max_speed_degradation=0.10,
            min_confidence=0.8,
            enabled=True,
            strategy=SwitchingStrategy.CANARY,
            test_percentage=0.1,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Aggressive rule for low-value requests
        aggressive_rule = SwitchingRule(
            rule_id="aggressive_switching",
            min_savings_percentage=10.0,
            max_quality_degradation=0.15,
            max_speed_degradation=0.20,
            min_confidence=0.6,
            enabled=True,
            strategy=SwitchingStrategy.IMMEDIATE,
            test_percentage=1.0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Balanced rule for medium-value requests
        balanced_rule = SwitchingRule(
            rule_id="balanced_switching",
            min_savings_percentage=15.0,
            max_quality_degradation=0.10,
            max_speed_degradation=0.15,
            min_confidence=0.7,
            enabled=True,
            strategy=SwitchingStrategy.GRADUAL,
            test_percentage=0.5,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.switching_rules = [conservative_rule, aggressive_rule, balanced_rule]
    
    async def should_switch_provider(self, opportunity: ArbitrageOpportunity) -> Tuple[bool, str]:
        """
        Determine if provider should be switched for an opportunity.
        
        Args:
            opportunity: Arbitrage opportunity to evaluate
            
        Returns:
            Tuple of (should_switch, reason)
        """
        try:
            # Check if target provider is available
            if not await self._is_provider_available(opportunity.alternative_provider):
                return False, f"Target provider {opportunity.alternative_provider} not available"
            
            # Check circuit breaker
            if self._is_circuit_breaker_open(opportunity.alternative_provider):
                return False, f"Circuit breaker open for {opportunity.alternative_provider}"
            
            # Find applicable switching rule
            applicable_rule = self._find_applicable_rule(opportunity)
            if not applicable_rule:
                return False, "No applicable switching rule found"
            
            # Check rule criteria
            if opportunity.savings_percentage < applicable_rule.min_savings_percentage:
                return False, f"Savings {opportunity.savings_percentage:.1f}% below threshold {applicable_rule.min_savings_percentage:.1f}%"
            
            if opportunity.quality_difference < -applicable_rule.max_quality_degradation:
                return False, f"Quality degradation {-opportunity.quality_difference:.3f} exceeds threshold {applicable_rule.max_quality_degradation:.3f}"
            
            if opportunity.speed_difference < -applicable_rule.max_speed_degradation:
                return False, f"Speed degradation {-opportunity.speed_difference:.3f} exceeds threshold {applicable_rule.max_speed_degradation:.3f}"
            
            if opportunity.confidence < applicable_rule.min_confidence:
                return False, f"Confidence {opportunity.confidence:.3f} below threshold {applicable_rule.min_confidence:.3f}"
            
            # Check switching mode
            if self.switching_mode == SwitchingMode.MANUAL:
                return False, "Manual switching mode - approval required"
            
            # For hybrid mode, check if this is high-risk
            if self.switching_mode == SwitchingMode.HYBRID:
                if self._is_high_risk_switch(opportunity):
                    return False, "High-risk switch in hybrid mode - manual approval required"
            
            return True, f"Switching approved using rule {applicable_rule.rule_id}"
            
        except Exception as e:
            self.logger.error(f"Error evaluating switching opportunity: {str(e)}")
            return False, f"Error evaluating switch: {str(e)}"
    
    async def execute_switch(self, opportunity: ArbitrageOpportunity, prompt: str) -> SwitchingResult:
        """
        Execute provider switching for an arbitrage opportunity.
        
        Args:
            opportunity: Arbitrage opportunity to execute
            prompt: Input prompt for the request
            
        Returns:
            SwitchingResult with execution details
        """
        start_time = datetime.now()
        
        try:
            # Check if switch should be executed
            should_switch, reason = await self.should_switch_provider(opportunity)
            
            if not should_switch:
                # Execute with original provider
                return await self._execute_with_fallback(
                    opportunity.current_provider,
                    opportunity.current_model,
                    prompt,
                    opportunity,
                    start_time,
                    switched=False,
                    reason=reason
                )
            
            # Find applicable rule for strategy
            applicable_rule = self._find_applicable_rule(opportunity)
            strategy = applicable_rule.strategy if applicable_rule else self.default_strategy
            
            # Execute based on strategy
            if strategy == SwitchingStrategy.IMMEDIATE:
                return await self._execute_immediate_switch(opportunity, prompt, start_time)
            
            elif strategy == SwitchingStrategy.CANARY:
                return await self._execute_canary_switch(opportunity, prompt, start_time, applicable_rule.test_percentage)
            
            elif strategy == SwitchingStrategy.GRADUAL:
                return await self._execute_gradual_switch(opportunity, prompt, start_time, applicable_rule.test_percentage)
            
            elif strategy == SwitchingStrategy.FALLBACK:
                return await self._execute_fallback_switch(opportunity, prompt, start_time)
            
            else:
                return await self._execute_immediate_switch(opportunity, prompt, start_time)
                
        except Exception as e:
            self.logger.error(f"Error executing provider switch: {str(e)}")
            
            # Fallback to original provider
            return await self._execute_with_fallback(
                opportunity.current_provider,
                opportunity.current_model,
                prompt,
                opportunity,
                start_time,
                switched=False,
                reason=f"Error during switch: {str(e)}"
            )
    
    async def _execute_immediate_switch(self, opportunity: ArbitrageOpportunity, prompt: str, start_time: datetime) -> SwitchingResult:
        """Execute immediate provider switch."""
        try:
            # Execute with target provider
            response = await self.model_bridge.generate_response(
                prompt=prompt,
                model=opportunity.alternative_model,
                provider=opportunity.alternative_provider
            )
            
            # Calculate actual metrics
            actual_cost = response.get("cost", 0.0)
            actual_savings = opportunity.current_cost - actual_cost
            quality_score = response.get("quality_score", 0.8)
            response_time = response.get("response_time", 0.0)
            
            result = SwitchingResult(
                success=True,
                original_provider=opportunity.current_provider,
                original_model=opportunity.current_model,
                actual_provider=opportunity.alternative_provider,
                actual_model=opportunity.alternative_model,
                original_cost=opportunity.current_cost,
                actual_cost=actual_cost,
                actual_savings=actual_savings,
                quality_score=quality_score,
                response_time=response_time,
                error_message=None,
                switched_at=start_time,
                completed_at=datetime.now(),
                metadata={"strategy": "immediate", "opportunity_id": opportunity.opportunity_id}
            )
            
            # Update performance tracking
            self._update_provider_performance(opportunity.alternative_provider, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in immediate switch: {str(e)}")
            
            # Fallback to original provider
            return await self._execute_with_fallback(
                opportunity.current_provider,
                opportunity.current_model,
                prompt,
                opportunity,
                start_time,
                switched=False,
                reason=f"Target provider failed: {str(e)}"
            )
    
    async def _execute_canary_switch(self, opportunity: ArbitrageOpportunity, prompt: str, start_time: datetime, test_percentage: float) -> SwitchingResult:
        """Execute canary provider switch (test with small percentage)."""
        # For simplicity, implement as immediate switch
        # In production, this would route only test_percentage of traffic
        return await self._execute_immediate_switch(opportunity, prompt, start_time)
    
    async def _execute_gradual_switch(self, opportunity: ArbitrageOpportunity, prompt: str, start_time: datetime, test_percentage: float) -> SwitchingResult:
        """Execute gradual provider switch."""
        # For simplicity, implement as immediate switch
        # In production, this would gradually increase traffic to new provider
        return await self._execute_immediate_switch(opportunity, prompt, start_time)
    
    async def _execute_fallback_switch(self, opportunity: ArbitrageOpportunity, prompt: str, start_time: datetime) -> SwitchingResult:
        """Execute fallback provider switch (only if primary fails)."""
        try:
            # Try original provider first
            response = await self.model_bridge.generate_response(
                prompt=prompt,
                model=opportunity.current_model,
                provider=opportunity.current_provider
            )
            
            # If successful, return original provider result
            actual_cost = response.get("cost", 0.0)
            quality_score = response.get("quality_score", 0.8)
            response_time = response.get("response_time", 0.0)
            
            result = SwitchingResult(
                success=True,
                original_provider=opportunity.current_provider,
                original_model=opportunity.current_model,
                actual_provider=opportunity.current_provider,
                actual_model=opportunity.current_model,
                original_cost=opportunity.current_cost,
                actual_cost=actual_cost,
                actual_savings=0.0,
                quality_score=quality_score,
                response_time=response_time,
                error_message=None,
                switched_at=start_time,
                completed_at=datetime.now(),
                metadata={"strategy": "fallback", "switched": False}
            )
            
            return result
            
        except Exception as e:
            self.logger.warning(f"Primary provider failed, switching to fallback: {str(e)}")
            
            # Primary failed, try alternative
            return await self._execute_immediate_switch(opportunity, prompt, start_time)
    
    async def _execute_with_fallback(
        self,
        provider: str,
        model: str,
        prompt: str,
        opportunity: ArbitrageOpportunity,
        start_time: datetime,
        switched: bool = False,
        reason: str = ""
    ) -> SwitchingResult:
        """Execute with fallback chain if primary fails."""
        try:
            # Try primary provider
            response = await self.model_bridge.generate_response(
                prompt=prompt,
                model=model,
                provider=provider
            )
            
            actual_cost = response.get("cost", 0.0)
            quality_score = response.get("quality_score", 0.8)
            response_time = response.get("response_time", 0.0)
            
            result = SwitchingResult(
                success=True,
                original_provider=opportunity.current_provider,
                original_model=opportunity.current_model,
                actual_provider=provider,
                actual_model=model,
                original_cost=opportunity.current_cost,
                actual_cost=actual_cost,
                actual_savings=0.0 if not switched else opportunity.current_cost - actual_cost,
                quality_score=quality_score,
                response_time=response_time,
                error_message=None,
                switched_at=start_time,
                completed_at=datetime.now(),
                metadata={"fallback_reason": reason, "switched": switched}
            )
            
            return result
            
        except Exception as e:
            # Try fallback chain
            fallback_providers = self.fallback_chains.get(provider, [])
            
            for fallback_provider in fallback_providers:
                try:
                    if await self._is_provider_available(fallback_provider):
                        response = await self.model_bridge.generate_response(
                            prompt=prompt,
                            model="default",  # Use default model for fallback provider
                            provider=fallback_provider
                        )
                        
                        actual_cost = response.get("cost", 0.0)
                        quality_score = response.get("quality_score", 0.8)
                        response_time = response.get("response_time", 0.0)
                        
                        result = SwitchingResult(
                            success=True,
                            original_provider=opportunity.current_provider,
                            original_model=opportunity.current_model,
                            actual_provider=fallback_provider,
                            actual_model="default",
                            original_cost=opportunity.current_cost,
                            actual_cost=actual_cost,
                            actual_savings=opportunity.current_cost - actual_cost,
                            quality_score=quality_score,
                            response_time=response_time,
                            error_message=None,
                            switched_at=start_time,
                            completed_at=datetime.now(),
                            metadata={"fallback_used": True, "fallback_provider": fallback_provider}
                        )
                        
                        return result
                        
                except Exception as fallback_error:
                    self.logger.warning(f"Fallback provider {fallback_provider} failed: {str(fallback_error)}")
                    continue
            
            # All fallbacks failed
            return SwitchingResult(
                success=False,
                original_provider=opportunity.current_provider,
                original_model=opportunity.current_model,
                actual_provider=provider,
                actual_model=model,
                original_cost=opportunity.current_cost,
                actual_cost=0.0,
                actual_savings=0.0,
                quality_score=0.0,
                response_time=0.0,
                error_message=f"All providers failed: {str(e)}",
                switched_at=start_time,
                completed_at=datetime.now(),
                metadata={"all_fallbacks_failed": True}
            )
    
    def _find_applicable_rule(self, opportunity: ArbitrageOpportunity) -> Optional[SwitchingRule]:
        """Find applicable switching rule for opportunity."""
        # For now, use simple rule matching based on savings
        # In production, this would be more sophisticated
        
        for rule in self.switching_rules:
            if not rule.enabled:
                continue
                
            if opportunity.savings_percentage >= rule.min_savings_percentage:
                if opportunity.quality_difference >= -rule.max_quality_degradation:
                    if opportunity.speed_difference >= -rule.max_speed_degradation:
                        if opportunity.confidence >= rule.min_confidence:
                            return rule
        
        return None
    
    def _is_high_risk_switch(self, opportunity: ArbitrageOpportunity) -> bool:
        """Determine if switch is high-risk."""
        # Consider high-risk if:
        # 1. Large cost difference (>$1.00)
        # 2. Quality degradation > 10%
        # 3. Low confidence < 70%
        
        if opportunity.current_cost > 1.00:
            return True
        
        if opportunity.quality_difference < -0.10:
            return True
        
        if opportunity.confidence < 0.70:
            return True
        
        return False
    
    async def _is_provider_available(self, provider: str) -> bool:
        """Check if provider is available."""
        # This would check actual provider availability
        # For now, assume all providers are available
        return True
    
    def _is_circuit_breaker_open(self, provider: str) -> bool:
        """Check if circuit breaker is open for provider."""
        breaker = self.circuit_breakers.get(provider)
        if not breaker:
            return False
        
        # Check if breaker is open
        if breaker.get("state") == "open":
            # Check if timeout has passed
            if datetime.now() > breaker.get("reset_time", datetime.now()):
                # Reset breaker to half-open
                breaker["state"] = "half_open"
                return False
            return True
        
        return False
    
    def _update_provider_performance(self, provider: str, result: SwitchingResult):
        """Update provider performance metrics."""
        if provider not in self.provider_performance:
            self.provider_performance[provider] = {
                "success_rate": 0.0,
                "avg_cost": 0.0,
                "avg_quality": 0.0,
                "avg_response_time": 0.0,
                "total_requests": 0
            }
        
        perf = self.provider_performance[provider]
        perf["total_requests"] += 1
        
        # Update success rate
        success_count = perf["total_requests"] * perf["success_rate"]
        if result.success:
            success_count += 1
        perf["success_rate"] = success_count / perf["total_requests"]
        
        # Update other metrics (simple moving average)
        alpha = 0.1  # Smoothing factor
        perf["avg_cost"] = alpha * result.actual_cost + (1 - alpha) * perf["avg_cost"]
        perf["avg_quality"] = alpha * result.quality_score + (1 - alpha) * perf["avg_quality"]
        perf["avg_response_time"] = alpha * result.response_time + (1 - alpha) * perf["avg_response_time"]
        
        # Update circuit breaker
        self._update_circuit_breaker(provider, result.success)
    
    def _update_circuit_breaker(self, provider: str, success: bool):
        """Update circuit breaker state."""
        if provider not in self.circuit_breakers:
            self.circuit_breakers[provider] = {
                "state": "closed",
                "failure_count": 0,
                "success_count": 0,
                "failure_threshold": 5,
                "reset_timeout": 300  # 5 minutes
            }
        
        breaker = self.circuit_breakers[provider]
        
        if success:
            breaker["success_count"] += 1
            breaker["failure_count"] = 0
            
            # Reset to closed if in half-open state
            if breaker["state"] == "half_open":
                breaker["state"] = "closed"
        else:
            breaker["failure_count"] += 1
            
            # Open breaker if failure threshold reached
            if breaker["failure_count"] >= breaker["failure_threshold"]:
                breaker["state"] = "open"
                breaker["reset_time"] = datetime.now() + timedelta(seconds=breaker["reset_timeout"])
    
    def get_switching_stats(self) -> Dict[str, Any]:
        """Get provider switching statistics."""
        total_switches = len(self.switching_results)
        successful_switches = sum(1 for r in self.switching_results if r.success)
        
        return {
            "total_switches": total_switches,
            "successful_switches": successful_switches,
            "success_rate": successful_switches / total_switches if total_switches > 0 else 0.0,
            "total_savings": sum(r.actual_savings for r in self.switching_results if r.success),
            "avg_savings": sum(r.actual_savings for r in self.switching_results if r.success) / successful_switches if successful_switches > 0 else 0.0,
            "provider_performance": self.provider_performance,
            "circuit_breaker_states": {p: b["state"] for p, b in self.circuit_breakers.items()},
            "switching_rules": len(self.switching_rules)
        }
    
    def add_switching_rule(self, rule: SwitchingRule):
        """Add new switching rule."""
        self.switching_rules.append(rule)
        self.logger.info(f"Added switching rule: {rule.rule_id}")
    
    def update_switching_rule(self, rule_id: str, updates: Dict[str, Any]):
        """Update existing switching rule."""
        for rule in self.switching_rules:
            if rule.rule_id == rule_id:
                for key, value in updates.items():
                    if hasattr(rule, key):
                        setattr(rule, key, value)
                rule.updated_at = datetime.now()
                self.logger.info(f"Updated switching rule: {rule_id}")
                return True
        return False
    
    def remove_switching_rule(self, rule_id: str):
        """Remove switching rule."""
        self.switching_rules = [r for r in self.switching_rules if r.rule_id != rule_id]
        self.logger.info(f"Removed switching rule: {rule_id}")
    
    def export_switching_data(self) -> Dict[str, Any]:
        """Export switching data for analysis."""
        return {
            "switching_mode": self.switching_mode.value,
            "default_strategy": self.default_strategy.value,
            "switching_rules": [
                {
                    "rule_id": rule.rule_id,
                    "min_savings_percentage": rule.min_savings_percentage,
                    "max_quality_degradation": rule.max_quality_degradation,
                    "max_speed_degradation": rule.max_speed_degradation,
                    "min_confidence": rule.min_confidence,
                    "enabled": rule.enabled,
                    "strategy": rule.strategy.value
                }
                for rule in self.switching_rules
            ],
            "provider_performance": self.provider_performance,
            "circuit_breakers": self.circuit_breakers,
            "fallback_chains": self.fallback_chains,
            "recent_results": len(self.switching_results)
        }