"""
Cost Predictor - Phase 2.1: Token-level Cost Prediction
Predicts costs for model requests based on token counts and provider pricing.
"""

import asyncio
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import logging

from .token_counter import TokenCounter, TokenCount
from .pricing_engine import PricingEngine, PricingTier

logger = logging.getLogger(__name__)


class CostAccuracy(Enum):
    """Accuracy levels for cost predictions."""
    HIGH = "high"        # 95%+ accuracy
    MEDIUM = "medium"    # 85-94% accuracy
    LOW = "low"          # 70-84% accuracy
    ESTIMATE = "estimate" # <70% accuracy


@dataclass
class CostPrediction:
    """Result of cost prediction operation."""
    estimated_cost: float
    input_cost: float
    output_cost: float
    total_tokens: int
    input_tokens: int
    output_tokens: int
    model_id: str
    provider: str
    accuracy: CostAccuracy
    confidence: float  # 0.0 to 1.0
    prediction_time: datetime
    factors: Dict[str, Any]  # Factors affecting prediction


@dataclass
class CostComparison:
    """Comparison of costs across providers."""
    predictions: List[CostPrediction]
    cheapest_provider: str
    most_expensive_provider: str
    cost_savings: float
    savings_percentage: float


class CostPredictor:
    """
    Advanced cost predictor with multi-provider support.
    
    Chain of thought:
    1. Combine token counting with pricing models
    2. Account for provider-specific pricing tiers
    3. Consider volume discounts and rate limits
    4. Provide accurate cost estimates with confidence
    """
    
    def __init__(self):
        """Initialize cost predictor with token counter and pricing engine."""
        self.logger = logging.getLogger(__name__)
        self.token_counter = TokenCounter()
        self.pricing_engine = PricingEngine()
        
        # Historical accuracy tracking
        self.prediction_history = []
        self.accuracy_cache = {}
        
        # Provider performance factors
        self.provider_factors = {
            "openai": {"reliability": 0.98, "speed": 0.90, "accuracy": 0.95},
            "anthropic": {"reliability": 0.96, "speed": 0.85, "accuracy": 0.92},
            "google": {"reliability": 0.94, "speed": 0.88, "accuracy": 0.89},
            "groq": {"reliability": 0.92, "speed": 0.95, "accuracy": 0.87},
            "together": {"reliability": 0.90, "speed": 0.92, "accuracy": 0.85},
            "mistral": {"reliability": 0.89, "speed": 0.87, "accuracy": 0.88},
            "cohere": {"reliability": 0.91, "speed": 0.86, "accuracy": 0.84},
            "perplexity": {"reliability": 0.88, "speed": 0.91, "accuracy": 0.83},
            "ollama": {"reliability": 0.85, "speed": 0.93, "accuracy": 0.80},
            "openrouter": {"reliability": 0.87, "speed": 0.89, "accuracy": 0.82}
        }
        
        self.logger.info("CostPredictor initialized with token counter and pricing engine")
    
    async def predict_cost(
        self,
        prompt: str,
        model_id: str,
        provider: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        complexity: str = "medium"
    ) -> CostPrediction:
        """
        Predict cost for a model request.
        
        Args:
            prompt: Input prompt text
            model_id: Model identifier
            provider: Provider name
            max_tokens: Maximum output tokens
            temperature: Model temperature (affects output length)
            complexity: Task complexity (simple/medium/complex)
            
        Returns:
            CostPrediction with detailed cost breakdown
        """
        try:
            # Count input tokens
            token_count = self.token_counter.count_tokens(prompt, model_id)
            
            # Estimate output tokens
            estimated_output = self._estimate_output_tokens(
                prompt, model_id, max_tokens, temperature, complexity
            )
            
            # Get pricing for model
            pricing = await self.pricing_engine.get_model_pricing(model_id, provider)
            
            # Calculate costs
            input_cost = (token_count.input_tokens / 1000) * pricing.input_price_per_1k
            output_cost = (estimated_output / 1000) * pricing.output_price_per_1k
            total_cost = input_cost + output_cost
            
            # Apply provider-specific factors
            factors = self._calculate_cost_factors(provider, model_id, complexity)
            adjusted_cost = total_cost * factors["cost_multiplier"]
            
            # Determine accuracy
            accuracy = self._determine_accuracy(token_count, pricing, provider)
            confidence = self._calculate_confidence(token_count, factors)
            
            prediction = CostPrediction(
                estimated_cost=adjusted_cost,
                input_cost=input_cost,
                output_cost=output_cost,
                total_tokens=token_count.input_tokens + estimated_output,
                input_tokens=token_count.input_tokens,
                output_tokens=estimated_output,
                model_id=model_id,
                provider=provider,
                accuracy=accuracy,
                confidence=confidence,
                prediction_time=datetime.now(),
                factors=factors
            )
            
            # Store prediction for accuracy tracking
            self.prediction_history.append(prediction)
            
            self.logger.debug(f"Cost prediction for {provider}/{model_id}: ${adjusted_cost:.6f}")
            return prediction
            
        except Exception as e:
            self.logger.error(f"Error predicting cost for {provider}/{model_id}: {str(e)}")
            return await self._fallback_prediction(prompt, model_id, provider, max_tokens)
    
    async def compare_providers(
        self,
        prompt: str,
        model_preferences: Dict[str, List[str]],  # provider -> [model_ids]
        max_tokens: Optional[int] = None,
        complexity: str = "medium"
    ) -> CostComparison:
        """
        Compare costs across multiple providers and models.
        
        Args:
            prompt: Input prompt text
            model_preferences: Dictionary of provider -> model list
            max_tokens: Maximum output tokens
            complexity: Task complexity
            
        Returns:
            CostComparison with provider analysis
        """
        try:
            predictions = []
            
            # Get predictions for all provider/model combinations
            for provider, models in model_preferences.items():
                for model_id in models:
                    try:
                        prediction = await self.predict_cost(
                            prompt, model_id, provider, max_tokens, complexity=complexity
                        )
                        predictions.append(prediction)
                    except Exception as e:
                        self.logger.warning(f"Failed to predict cost for {provider}/{model_id}: {str(e)}")
                        continue
            
            if not predictions:
                raise ValueError("No valid cost predictions available")
            
            # Sort by cost
            predictions.sort(key=lambda p: p.estimated_cost)
            
            cheapest = predictions[0]
            most_expensive = predictions[-1]
            
            cost_savings = most_expensive.estimated_cost - cheapest.estimated_cost
            savings_percentage = (cost_savings / most_expensive.estimated_cost) * 100
            
            comparison = CostComparison(
                predictions=predictions,
                cheapest_provider=f"{cheapest.provider}/{cheapest.model_id}",
                most_expensive_provider=f"{most_expensive.provider}/{most_expensive.model_id}",
                cost_savings=cost_savings,
                savings_percentage=savings_percentage
            )
            
            self.logger.info(f"Cost comparison complete: {len(predictions)} providers, {savings_percentage:.1f}% savings available")
            return comparison
            
        except Exception as e:
            self.logger.error(f"Error comparing provider costs: {str(e)}")
            raise
    
    def _estimate_output_tokens(
        self,
        prompt: str,
        model_id: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        complexity: str = "medium"
    ) -> int:
        """
        Estimate output tokens based on prompt and parameters.
        
        Chain of thought:
        1. Base estimation from token counter
        2. Adjust for temperature (higher = more verbose)
        3. Adjust for complexity (complex = longer responses)
        4. Apply model-specific patterns
        5. Respect max_tokens constraint
        """
        # Base estimation
        base_estimate = self.token_counter.estimate_output_tokens(prompt, max_tokens)
        
        # Temperature adjustment
        if temperature is not None:
            if temperature > 0.7:
                base_estimate = int(base_estimate * 1.3)  # Higher temperature = more verbose
            elif temperature < 0.3:
                base_estimate = int(base_estimate * 0.8)  # Lower temperature = more concise
        
        # Complexity adjustment
        complexity_multipliers = {
            "simple": 0.7,
            "medium": 1.0,
            "complex": 1.5
        }
        base_estimate = int(base_estimate * complexity_multipliers.get(complexity, 1.0))
        
        # Model-specific adjustments
        model_lower = model_id.lower()
        if "gpt-4" in model_lower:
            base_estimate = int(base_estimate * 1.2)  # GPT-4 tends to be more verbose
        elif "claude" in model_lower:
            base_estimate = int(base_estimate * 1.1)  # Claude is moderately verbose
        elif "gemini" in model_lower:
            base_estimate = int(base_estimate * 0.9)  # Gemini is more concise
        
        # Apply max_tokens constraint
        if max_tokens:
            base_estimate = min(base_estimate, max_tokens)
        
        return max(base_estimate, 5)  # Minimum reasonable output
    
    def _calculate_cost_factors(self, provider: str, model_id: str, complexity: str) -> Dict[str, Any]:
        """Calculate factors affecting cost prediction."""
        factors = {
            "cost_multiplier": 1.0,
            "provider_reliability": 1.0,
            "model_efficiency": 1.0,
            "complexity_factor": 1.0
        }
        
        # Provider-specific factors
        if provider in self.provider_factors:
            provider_data = self.provider_factors[provider]
            factors["provider_reliability"] = provider_data["reliability"]
            
            # Less reliable providers may need retries (increased cost)
            if provider_data["reliability"] < 0.90:
                factors["cost_multiplier"] *= 1.1
        
        # Model efficiency factors
        model_lower = model_id.lower()
        if "turbo" in model_lower or "flash" in model_lower:
            factors["model_efficiency"] = 1.2  # Faster models are more efficient
        elif "large" in model_lower or "70b" in model_lower:
            factors["model_efficiency"] = 0.8  # Larger models less efficient
        
        # Complexity factors
        complexity_factors = {
            "simple": 0.9,
            "medium": 1.0,
            "complex": 1.2
        }
        factors["complexity_factor"] = complexity_factors.get(complexity, 1.0)
        
        # Calculate final multiplier
        factors["cost_multiplier"] = (
            factors["cost_multiplier"] *
            factors["model_efficiency"] *
            factors["complexity_factor"]
        )
        
        return factors
    
    def _determine_accuracy(self, token_count: TokenCount, pricing: Any, provider: str) -> CostAccuracy:
        """Determine accuracy level for cost prediction."""
        base_accuracy = token_count.accuracy
        
        # Provider-specific accuracy
        if provider in self.provider_factors:
            provider_accuracy = self.provider_factors[provider]["accuracy"]
            combined_accuracy = (base_accuracy + provider_accuracy) / 2
        else:
            combined_accuracy = base_accuracy * 0.8  # Unknown provider penalty
        
        # Determine accuracy level
        if combined_accuracy >= 0.95:
            return CostAccuracy.HIGH
        elif combined_accuracy >= 0.85:
            return CostAccuracy.MEDIUM
        elif combined_accuracy >= 0.70:
            return CostAccuracy.LOW
        else:
            return CostAccuracy.ESTIMATE
    
    def _calculate_confidence(self, token_count: TokenCount, factors: Dict[str, Any]) -> float:
        """Calculate confidence score for prediction."""
        base_confidence = token_count.accuracy
        
        # Factor in provider reliability
        reliability_factor = factors.get("provider_reliability", 1.0)
        
        # Factor in model efficiency (more efficient = more predictable)
        efficiency_factor = factors.get("model_efficiency", 1.0)
        
        # Combine factors
        confidence = base_confidence * reliability_factor * min(efficiency_factor, 1.0)
        
        return min(confidence, 1.0)
    
    async def _fallback_prediction(
        self,
        prompt: str,
        model_id: str,
        provider: str,
        max_tokens: Optional[int] = None
    ) -> CostPrediction:
        """Fallback prediction when main method fails."""
        # Simple word-based estimation
        word_count = len(prompt.split())
        estimated_input_tokens = int(word_count * 1.3)
        estimated_output_tokens = min(word_count, max_tokens or 100)
        
        # Generic pricing (fallback)
        input_cost = (estimated_input_tokens / 1000) * 0.001  # $0.001 per 1K tokens
        output_cost = (estimated_output_tokens / 1000) * 0.002  # $0.002 per 1K tokens
        total_cost = input_cost + output_cost
        
        return CostPrediction(
            estimated_cost=total_cost,
            input_cost=input_cost,
            output_cost=output_cost,
            total_tokens=estimated_input_tokens + estimated_output_tokens,
            input_tokens=estimated_input_tokens,
            output_tokens=estimated_output_tokens,
            model_id=model_id,
            provider=provider,
            accuracy=CostAccuracy.ESTIMATE,
            confidence=0.50,
            prediction_time=datetime.now(),
            factors={"cost_multiplier": 1.0, "fallback": True}
        )
    
    def update_prediction_accuracy(self, prediction_id: str, actual_cost: float, actual_tokens: int):
        """Update prediction accuracy based on actual results."""
        # This would be called after a request completes to improve accuracy
        # Implementation would track actual vs predicted costs
        pass
    
    def get_prediction_stats(self) -> Dict[str, Any]:
        """Get statistics about prediction accuracy and performance."""
        if not self.prediction_history:
            return {"total_predictions": 0, "average_confidence": 0.0}
        
        total_predictions = len(self.prediction_history)
        avg_confidence = sum(p.confidence for p in self.prediction_history) / total_predictions
        
        accuracy_breakdown = {}
        for accuracy in CostAccuracy:
            count = sum(1 for p in self.prediction_history if p.accuracy == accuracy)
            accuracy_breakdown[accuracy.value] = count
        
        provider_breakdown = {}
        for prediction in self.prediction_history:
            provider = prediction.provider
            if provider not in provider_breakdown:
                provider_breakdown[provider] = {"count": 0, "avg_cost": 0.0}
            provider_breakdown[provider]["count"] += 1
            provider_breakdown[provider]["avg_cost"] = (
                provider_breakdown[provider]["avg_cost"] + prediction.estimated_cost
            ) / 2
        
        return {
            "total_predictions": total_predictions,
            "average_confidence": avg_confidence,
            "accuracy_breakdown": accuracy_breakdown,
            "provider_breakdown": provider_breakdown
        }