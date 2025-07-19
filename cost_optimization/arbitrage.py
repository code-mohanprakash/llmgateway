"""
Arbitrage - Phase 2.4: Provider Cost Arbitrage
Real-time cost comparison and arbitrage opportunity detection across providers.
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging
from collections import defaultdict, deque

from .cost_predictor import CostPredictor, CostPrediction
from .pricing_engine import PricingEngine

logger = logging.getLogger(__name__)


class ArbitrageType(Enum):
    """Types of arbitrage opportunities."""
    COST_ARBITRAGE = "cost_arbitrage"  # Pure cost difference
    QUALITY_ARBITRAGE = "quality_arbitrage"  # Better quality at similar cost
    SPEED_ARBITRAGE = "speed_arbitrage"  # Faster response at similar cost
    RELIABILITY_ARBITRAGE = "reliability_arbitrage"  # More reliable at similar cost


@dataclass
class ArbitrageOpportunity:
    """Arbitrage opportunity between providers."""
    opportunity_id: str
    prompt_hash: str
    current_provider: str
    current_model: str
    current_cost: float
    alternative_provider: str
    alternative_model: str
    alternative_cost: float
    cost_savings: float
    savings_percentage: float
    arbitrage_type: ArbitrageType
    quality_difference: float
    speed_difference: float
    reliability_difference: float
    confidence: float
    detected_at: datetime
    expires_at: datetime
    metadata: Dict[str, Any]


@dataclass
class ArbitrageExecution:
    """Record of executed arbitrage."""
    opportunity_id: str
    original_provider: str
    original_model: str
    original_cost: float
    switched_provider: str
    switched_model: str
    switched_cost: float
    actual_savings: float
    quality_impact: float
    speed_impact: float
    executed_at: datetime
    success: bool
    error_message: Optional[str]


@dataclass
class ArbitrageStats:
    """Statistics for arbitrage performance."""
    total_opportunities: int
    executed_opportunities: int
    execution_rate: float
    total_savings: float
    avg_savings_per_opportunity: float
    avg_quality_impact: float
    avg_speed_impact: float
    success_rate: float
    top_providers: List[Tuple[str, float]]  # (provider, savings)
    arbitrage_by_type: Dict[str, int]


class MarketData:
    """Real-time market data for arbitrage decisions."""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.cost_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        self.quality_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        self.speed_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        self.reliability_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
    
    def update_provider_metrics(
        self,
        provider: str,
        model: str,
        cost: float,
        quality: float,
        speed: float,
        reliability: float
    ):
        """Update provider metrics."""
        key = f"{provider}/{model}"
        
        self.cost_history[key].append((time.time(), cost))
        self.quality_history[key].append((time.time(), quality))
        self.speed_history[key].append((time.time(), speed))
        self.reliability_history[key].append((time.time(), reliability))
    
    def get_provider_metrics(self, provider: str, model: str) -> Dict[str, float]:
        """Get current metrics for a provider/model."""
        key = f"{provider}/{model}"
        
        # Calculate averages from recent history
        cost_avg = self._calculate_average(self.cost_history[key])
        quality_avg = self._calculate_average(self.quality_history[key])
        speed_avg = self._calculate_average(self.speed_history[key])
        reliability_avg = self._calculate_average(self.reliability_history[key])
        
        return {
            "cost": cost_avg,
            "quality": quality_avg,
            "speed": speed_avg,
            "reliability": reliability_avg
        }
    
    def _calculate_average(self, history: deque) -> float:
        """Calculate average from time-series data."""
        if not history:
            return 0.0
        
        # Use only recent data (last 60 seconds)
        cutoff_time = time.time() - 60
        recent_values = [value for timestamp, value in history if timestamp > cutoff_time]
        
        if not recent_values:
            # Fall back to all data if no recent data
            recent_values = [value for _, value in history]
        
        return sum(recent_values) / len(recent_values) if recent_values else 0.0


class Arbitrage:
    """
    Advanced arbitrage system with real-time opportunity detection.
    
    Chain of thought:
    1. Monitor pricing and performance across providers
    2. Detect arbitrage opportunities in real-time
    3. Calculate potential savings and quality impacts
    4. Execute arbitrage with minimal latency
    5. Track performance and optimize strategies
    """
    
    def __init__(self, cost_predictor: CostPredictor, pricing_engine: PricingEngine):
        """Initialize arbitrage system."""
        self.logger = logging.getLogger(__name__)
        self.cost_predictor = cost_predictor
        self.pricing_engine = pricing_engine
        
        # Market data tracking
        self.market_data = MarketData()
        
        # Arbitrage tracking
        self.opportunities: Dict[str, ArbitrageOpportunity] = {}
        self.executions: List[ArbitrageExecution] = []
        
        # Configuration
        self.min_savings_threshold = 0.10  # 10% minimum savings
        self.max_quality_degradation = 0.1  # 10% max quality loss
        self.max_speed_degradation = 0.2  # 20% max speed loss
        self.opportunity_ttl = 300  # 5 minutes
        
        # Provider compatibility matrix
        self.provider_compatibility = {
            "openai": ["anthropic", "google", "groq", "together"],
            "anthropic": ["openai", "google", "cohere"],
            "google": ["openai", "anthropic", "mistral"],
            "groq": ["openai", "together", "mistral"],
            "together": ["openai", "groq", "mistral"],
            "mistral": ["google", "groq", "together"],
            "cohere": ["anthropic", "openai"],
            "perplexity": ["openai", "anthropic"],
            "ollama": ["groq", "together"],
            "openrouter": ["openai", "anthropic", "google"]
        }
        
        # Model capability mapping
        self.model_capabilities = {
            "text_generation": ["gpt-4", "claude-3", "gemini", "llama3", "mistral"],
            "code_generation": ["gpt-4", "claude-3", "gemini", "codellama", "deepseek"],
            "analysis": ["gpt-4", "claude-3", "gemini", "mixtral"],
            "creative": ["gpt-4", "claude-3", "gemini", "llama3"]
        }
        
        self.logger.info("Arbitrage system initialized")
    
    async def detect_arbitrage_opportunities(
        self,
        prompt: str,
        current_provider: str,
        current_model: str,
        task_type: str = "text_generation",
        max_alternatives: int = 3
    ) -> List[ArbitrageOpportunity]:
        """
        Detect arbitrage opportunities for a given request.
        
        Args:
            prompt: Input prompt
            current_provider: Current provider
            current_model: Current model
            task_type: Type of task (affects model selection)
            max_alternatives: Maximum alternatives to consider
            
        Returns:
            List of arbitrage opportunities
        """
        try:
            # Get current cost prediction
            current_prediction = await self.cost_predictor.predict_cost(
                prompt, current_model, current_provider
            )
            
            # Get alternative providers
            alternative_providers = self._get_alternative_providers(
                current_provider, current_model, task_type
            )
            
            opportunities = []
            
            # Compare with alternatives
            for alt_provider, alt_model in alternative_providers[:max_alternatives]:
                try:
                    # Get alternative cost prediction
                    alt_prediction = await self.cost_predictor.predict_cost(
                        prompt, alt_model, alt_provider
                    )
                    
                    # Calculate opportunity
                    opportunity = await self._calculate_arbitrage_opportunity(
                        prompt, current_prediction, alt_prediction, task_type
                    )
                    
                    if opportunity:
                        opportunities.append(opportunity)
                        
                except Exception as e:
                    self.logger.warning(f"Error analyzing alternative {alt_provider}/{alt_model}: {str(e)}")
                    continue
            
            # Sort by savings (descending)
            opportunities.sort(key=lambda x: x.cost_savings, reverse=True)
            
            # Store opportunities
            for opp in opportunities:
                self.opportunities[opp.opportunity_id] = opp
            
            self.logger.debug(f"Found {len(opportunities)} arbitrage opportunities")
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Error detecting arbitrage opportunities: {str(e)}")
            return []
    
    async def _calculate_arbitrage_opportunity(
        self,
        prompt: str,
        current_prediction: CostPrediction,
        alternative_prediction: CostPrediction,
        task_type: str
    ) -> Optional[ArbitrageOpportunity]:
        """Calculate arbitrage opportunity between two predictions."""
        
        # Calculate cost savings
        cost_savings = current_prediction.estimated_cost - alternative_prediction.estimated_cost
        
        if cost_savings <= 0:
            return None
        
        savings_percentage = (cost_savings / current_prediction.estimated_cost) * 100
        
        # Check minimum savings threshold
        if savings_percentage < self.min_savings_threshold:
            return None
        
        # Get provider metrics
        current_metrics = self.market_data.get_provider_metrics(
            current_prediction.provider, current_prediction.model_id
        )
        alt_metrics = self.market_data.get_provider_metrics(
            alternative_prediction.provider, alternative_prediction.model_id
        )
        
        # Calculate quality difference
        quality_difference = alt_metrics.get("quality", 0.8) - current_metrics.get("quality", 0.8)
        
        # Calculate speed difference (negative means slower)
        speed_difference = alt_metrics.get("speed", 0.8) - current_metrics.get("speed", 0.8)
        
        # Calculate reliability difference
        reliability_difference = alt_metrics.get("reliability", 0.8) - current_metrics.get("reliability", 0.8)
        
        # Check quality degradation threshold
        if quality_difference < -self.max_quality_degradation:
            return None
        
        # Check speed degradation threshold
        if speed_difference < -self.max_speed_degradation:
            return None
        
        # Determine arbitrage type
        arbitrage_type = self._determine_arbitrage_type(
            cost_savings, quality_difference, speed_difference, reliability_difference
        )
        
        # Calculate confidence
        confidence = self._calculate_arbitrage_confidence(
            current_prediction, alternative_prediction, quality_difference, speed_difference
        )
        
        # Generate opportunity ID
        prompt_hash = self._hash_prompt(prompt)
        opportunity_id = f"arb_{prompt_hash}_{current_prediction.provider}_{alternative_prediction.provider}_{int(time.time())}"
        
        opportunity = ArbitrageOpportunity(
            opportunity_id=opportunity_id,
            prompt_hash=prompt_hash,
            current_provider=current_prediction.provider,
            current_model=current_prediction.model_id,
            current_cost=current_prediction.estimated_cost,
            alternative_provider=alternative_prediction.provider,
            alternative_model=alternative_prediction.model_id,
            alternative_cost=alternative_prediction.estimated_cost,
            cost_savings=cost_savings,
            savings_percentage=savings_percentage,
            arbitrage_type=arbitrage_type,
            quality_difference=quality_difference,
            speed_difference=speed_difference,
            reliability_difference=reliability_difference,
            confidence=confidence,
            detected_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=self.opportunity_ttl),
            metadata={
                "task_type": task_type,
                "current_metrics": current_metrics,
                "alternative_metrics": alt_metrics
            }
        )
        
        return opportunity
    
    def _get_alternative_providers(self, current_provider: str, current_model: str, task_type: str) -> List[Tuple[str, str]]:
        """Get alternative providers for arbitrage consideration."""
        alternatives = []
        
        # Get compatible providers
        compatible_providers = self.provider_compatibility.get(current_provider, [])
        
        # Get capable models for task type
        capable_models = self.model_capabilities.get(task_type, [])
        
        for provider in compatible_providers:
            # Get provider's models that can handle the task
            provider_models = self.pricing_engine.get_provider_models(provider)
            
            for model in provider_models:
                # Check if model is capable of handling the task
                if any(capable_model in model for capable_model in capable_models):
                    alternatives.append((provider, model))
        
        return alternatives
    
    def _determine_arbitrage_type(
        self,
        cost_savings: float,
        quality_difference: float,
        speed_difference: float,
        reliability_difference: float
    ) -> ArbitrageType:
        """Determine the type of arbitrage opportunity."""
        
        # Pure cost arbitrage (similar or better quality/speed/reliability)
        if quality_difference >= 0 and speed_difference >= 0 and reliability_difference >= 0:
            return ArbitrageType.COST_ARBITRAGE
        
        # Quality arbitrage (better quality at similar cost)
        if quality_difference > 0.1:
            return ArbitrageType.QUALITY_ARBITRAGE
        
        # Speed arbitrage (faster at similar cost)
        if speed_difference > 0.1:
            return ArbitrageType.SPEED_ARBITRAGE
        
        # Reliability arbitrage (more reliable at similar cost)
        if reliability_difference > 0.1:
            return ArbitrageType.RELIABILITY_ARBITRAGE
        
        # Default to cost arbitrage
        return ArbitrageType.COST_ARBITRAGE
    
    def _calculate_arbitrage_confidence(
        self,
        current_prediction: CostPrediction,
        alternative_prediction: CostPrediction,
        quality_difference: float,
        speed_difference: float
    ) -> float:
        """Calculate confidence in arbitrage opportunity."""
        
        # Base confidence from predictions
        base_confidence = (current_prediction.confidence + alternative_prediction.confidence) / 2
        
        # Quality factor (penalize negative quality difference)
        quality_factor = 1.0 if quality_difference >= 0 else 0.8
        
        # Speed factor (penalize negative speed difference)
        speed_factor = 1.0 if speed_difference >= 0 else 0.9
        
        # Historical success factor (placeholder - would use actual historical data)
        historical_factor = 0.9
        
        # Combine factors
        confidence = base_confidence * quality_factor * speed_factor * historical_factor
        
        return min(confidence, 1.0)
    
    async def execute_arbitrage(self, opportunity_id: str) -> ArbitrageExecution:
        """
        Execute an arbitrage opportunity.
        
        Args:
            opportunity_id: ID of the opportunity to execute
            
        Returns:
            ArbitrageExecution record
        """
        try:
            opportunity = self.opportunities.get(opportunity_id)
            if not opportunity:
                raise ValueError(f"Arbitrage opportunity {opportunity_id} not found")
            
            # Check if opportunity is still valid
            if datetime.now() > opportunity.expires_at:
                raise ValueError(f"Arbitrage opportunity {opportunity_id} has expired")
            
            # Execute the switch (this would integrate with the actual request routing)
            execution = ArbitrageExecution(
                opportunity_id=opportunity_id,
                original_provider=opportunity.current_provider,
                original_model=opportunity.current_model,
                original_cost=opportunity.current_cost,
                switched_provider=opportunity.alternative_provider,
                switched_model=opportunity.alternative_model,
                switched_cost=opportunity.alternative_cost,
                actual_savings=opportunity.cost_savings,
                quality_impact=opportunity.quality_difference,
                speed_impact=opportunity.speed_difference,
                executed_at=datetime.now(),
                success=True,
                error_message=None
            )
            
            # Store execution record
            self.executions.append(execution)
            
            # Update market data
            self.market_data.update_provider_metrics(
                opportunity.alternative_provider,
                opportunity.alternative_model,
                opportunity.alternative_cost,
                0.8 + opportunity.quality_difference,  # Placeholder quality
                0.8 + opportunity.speed_difference,    # Placeholder speed
                0.8 + opportunity.reliability_difference  # Placeholder reliability
            )
            
            self.logger.info(f"Executed arbitrage {opportunity_id}: saved ${opportunity.cost_savings:.6f}")
            return execution
            
        except Exception as e:
            self.logger.error(f"Error executing arbitrage {opportunity_id}: {str(e)}")
            
            # Create failed execution record
            execution = ArbitrageExecution(
                opportunity_id=opportunity_id,
                original_provider=opportunity.current_provider if opportunity else "",
                original_model=opportunity.current_model if opportunity else "",
                original_cost=opportunity.current_cost if opportunity else 0.0,
                switched_provider="",
                switched_model="",
                switched_cost=0.0,
                actual_savings=0.0,
                quality_impact=0.0,
                speed_impact=0.0,
                executed_at=datetime.now(),
                success=False,
                error_message=str(e)
            )
            
            self.executions.append(execution)
            return execution
    
    def _hash_prompt(self, prompt: str) -> str:
        """Generate hash for prompt."""
        import hashlib
        return hashlib.md5(prompt.encode()).hexdigest()[:8]
    
    def cleanup_expired_opportunities(self):
        """Clean up expired arbitrage opportunities."""
        now = datetime.now()
        expired_ids = [
            opp_id for opp_id, opp in self.opportunities.items()
            if now > opp.expires_at
        ]
        
        for opp_id in expired_ids:
            del self.opportunities[opp_id]
        
        if expired_ids:
            self.logger.debug(f"Cleaned up {len(expired_ids)} expired arbitrage opportunities")
    
    def get_arbitrage_stats(self) -> ArbitrageStats:
        """Get arbitrage performance statistics."""
        total_opportunities = len(self.opportunities) + len(self.executions)
        executed_opportunities = len(self.executions)
        successful_executions = sum(1 for exec in self.executions if exec.success)
        
        execution_rate = executed_opportunities / total_opportunities if total_opportunities > 0 else 0.0
        success_rate = successful_executions / executed_opportunities if executed_opportunities > 0 else 0.0
        
        total_savings = sum(exec.actual_savings for exec in self.executions if exec.success)
        avg_savings = total_savings / successful_executions if successful_executions > 0 else 0.0
        
        avg_quality_impact = sum(exec.quality_impact for exec in self.executions if exec.success) / successful_executions if successful_executions > 0 else 0.0
        avg_speed_impact = sum(exec.speed_impact for exec in self.executions if exec.success) / successful_executions if successful_executions > 0 else 0.0
        
        # Calculate top providers by savings
        provider_savings = defaultdict(float)
        for exec in self.executions:
            if exec.success:
                provider_savings[exec.switched_provider] += exec.actual_savings
        
        top_providers = sorted(provider_savings.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Calculate arbitrage by type
        arbitrage_by_type = defaultdict(int)
        for opp in self.opportunities.values():
            arbitrage_by_type[opp.arbitrage_type.value] += 1
        
        return ArbitrageStats(
            total_opportunities=total_opportunities,
            executed_opportunities=executed_opportunities,
            execution_rate=execution_rate,
            total_savings=total_savings,
            avg_savings_per_opportunity=avg_savings,
            avg_quality_impact=avg_quality_impact,
            avg_speed_impact=avg_speed_impact,
            success_rate=success_rate,
            top_providers=top_providers,
            arbitrage_by_type=dict(arbitrage_by_type)
        )
    
    def get_active_opportunities(self) -> List[ArbitrageOpportunity]:
        """Get all active arbitrage opportunities."""
        now = datetime.now()
        active_opportunities = [
            opp for opp in self.opportunities.values()
            if now <= opp.expires_at
        ]
        
        return sorted(active_opportunities, key=lambda x: x.cost_savings, reverse=True)
    
    def get_execution_history(self, limit: int = 100) -> List[ArbitrageExecution]:
        """Get recent execution history."""
        return sorted(self.executions, key=lambda x: x.executed_at, reverse=True)[:limit]
    
    def export_arbitrage_data(self) -> Dict[str, Any]:
        """Export arbitrage data for analysis."""
        return {
            "stats": self.get_arbitrage_stats().__dict__,
            "active_opportunities": len(self.get_active_opportunities()),
            "execution_history": len(self.executions),
            "market_data_points": sum(len(history) for history in self.market_data.cost_history.values()),
            "provider_compatibility": self.provider_compatibility,
            "model_capabilities": self.model_capabilities
        }