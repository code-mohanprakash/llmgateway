"""
Pricing Engine - Phase 2.1: Token-level Cost Prediction
Manages pricing models and tiers for different providers and models.
"""

import asyncio
import json
import yaml
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class PricingTier(Enum):
    """Pricing tiers for different usage levels."""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


@dataclass
class ModelPricing:
    """Pricing information for a specific model."""
    model_id: str
    provider: str
    input_price_per_1k: float  # Price per 1K input tokens
    output_price_per_1k: float  # Price per 1K output tokens
    minimum_charge: float  # Minimum charge per request
    tier: PricingTier
    volume_discounts: Dict[int, float]  # Usage level -> discount multiplier
    rate_limits: Dict[str, int]  # Rate limits (requests_per_minute, tokens_per_minute)
    last_updated: datetime
    currency: str = "USD"


@dataclass
class PricingRule:
    """Dynamic pricing rule based on conditions."""
    rule_id: str
    conditions: Dict[str, Any]  # Conditions for rule application
    price_adjustment: float  # Multiplier for price adjustment
    valid_until: Optional[datetime]
    priority: int  # Higher priority rules override lower ones


class PricingEngine:
    """
    Advanced pricing engine with dynamic pricing and volume discounts.
    
    Chain of thought:
    1. Maintain accurate pricing data for all providers
    2. Handle volume discounts and tier-based pricing
    3. Support dynamic pricing based on demand/supply
    4. Provide cost optimization recommendations
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize pricing engine with configuration."""
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path or "config/pricing_config.yaml"
        
        # Pricing data storage
        self.model_pricing: Dict[str, ModelPricing] = {}
        self.pricing_rules: List[PricingRule] = []
        
        # Default pricing for common models
        self._initialize_default_pricing()
        
        # Load configuration if available
        self._load_pricing_config()
        
        self.logger.info(f"PricingEngine initialized with {len(self.model_pricing)} models")
    
    def _initialize_default_pricing(self):
        """Initialize default pricing for common models."""
        # OpenAI pricing (as of 2024)
        openai_models = {
            "gpt-4o": ModelPricing(
                model_id="gpt-4o",
                provider="openai",
                input_price_per_1k=0.005,
                output_price_per_1k=0.015,
                minimum_charge=0.0001,
                tier=PricingTier.PREMIUM,
                volume_discounts={1000000: 0.9, 10000000: 0.8},
                rate_limits={"requests_per_minute": 10000, "tokens_per_minute": 2000000},
                last_updated=datetime.now()
            ),
            "gpt-4o-mini": ModelPricing(
                model_id="gpt-4o-mini",
                provider="openai",
                input_price_per_1k=0.00015,
                output_price_per_1k=0.0006,
                minimum_charge=0.00001,
                tier=PricingTier.BASIC,
                volume_discounts={1000000: 0.9, 10000000: 0.8},
                rate_limits={"requests_per_minute": 20000, "tokens_per_minute": 5000000},
                last_updated=datetime.now()
            ),
            "gpt-3.5-turbo": ModelPricing(
                model_id="gpt-3.5-turbo",
                provider="openai",
                input_price_per_1k=0.0005,
                output_price_per_1k=0.0015,
                minimum_charge=0.00001,
                tier=PricingTier.BASIC,
                volume_discounts={1000000: 0.9, 10000000: 0.8},
                rate_limits={"requests_per_minute": 10000, "tokens_per_minute": 1000000},
                last_updated=datetime.now()
            )
        }
        
        # Anthropic pricing
        anthropic_models = {
            "claude-3-5-sonnet-20241022": ModelPricing(
                model_id="claude-3-5-sonnet-20241022",
                provider="anthropic",
                input_price_per_1k=0.003,
                output_price_per_1k=0.015,
                minimum_charge=0.0001,
                tier=PricingTier.PREMIUM,
                volume_discounts={1000000: 0.9, 10000000: 0.8},
                rate_limits={"requests_per_minute": 5000, "tokens_per_minute": 1000000},
                last_updated=datetime.now()
            ),
            "claude-3-haiku-20240307": ModelPricing(
                model_id="claude-3-haiku-20240307",
                provider="anthropic",
                input_price_per_1k=0.00025,
                output_price_per_1k=0.00125,
                minimum_charge=0.00001,
                tier=PricingTier.BASIC,
                volume_discounts={1000000: 0.9, 10000000: 0.8},
                rate_limits={"requests_per_minute": 10000, "tokens_per_minute": 2000000},
                last_updated=datetime.now()
            )
        }
        
        # Google pricing
        google_models = {
            "gemini-1.5-pro": ModelPricing(
                model_id="gemini-1.5-pro",
                provider="google",
                input_price_per_1k=0.0035,
                output_price_per_1k=0.0105,
                minimum_charge=0.0001,
                tier=PricingTier.PREMIUM,
                volume_discounts={1000000: 0.9, 10000000: 0.8},
                rate_limits={"requests_per_minute": 2000, "tokens_per_minute": 1000000},
                last_updated=datetime.now()
            ),
            "gemini-1.5-flash": ModelPricing(
                model_id="gemini-1.5-flash",
                provider="google",
                input_price_per_1k=0.000075,
                output_price_per_1k=0.0003,
                minimum_charge=0.00001,
                tier=PricingTier.BASIC,
                volume_discounts={1000000: 0.9, 10000000: 0.8},
                rate_limits={"requests_per_minute": 15000, "tokens_per_minute": 4000000},
                last_updated=datetime.now()
            )
        }
        
        # Open source / free tier models
        free_models = {
            "llama3:8b": ModelPricing(
                model_id="llama3:8b",
                provider="ollama",
                input_price_per_1k=0.0,
                output_price_per_1k=0.0,
                minimum_charge=0.0,
                tier=PricingTier.FREE,
                volume_discounts={},
                rate_limits={"requests_per_minute": 100, "tokens_per_minute": 50000},
                last_updated=datetime.now()
            ),
            "deepseek/deepseek-r1-0528:free": ModelPricing(
                model_id="deepseek/deepseek-r1-0528:free",
                provider="openrouter",
                input_price_per_1k=0.0,
                output_price_per_1k=0.0,
                minimum_charge=0.0,
                tier=PricingTier.FREE,
                volume_discounts={},
                rate_limits={"requests_per_minute": 20, "tokens_per_minute": 10000},
                last_updated=datetime.now()
            )
        }
        
        # Combine all models
        all_models = {**openai_models, **anthropic_models, **google_models, **free_models}
        
        # Create model keys (provider/model_id format)
        for model_id, pricing in all_models.items():
            key = f"{pricing.provider}/{model_id}"
            self.model_pricing[key] = pricing
    
    def _load_pricing_config(self):
        """Load pricing configuration from file."""
        try:
            config_path = Path(self.config_path)
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    self._process_pricing_config(config)
                    self.logger.info(f"Loaded pricing config from {config_path}")
            else:
                self.logger.info(f"No pricing config found at {config_path}, using defaults")
        except Exception as e:
            self.logger.error(f"Error loading pricing config: {str(e)}")
    
    def _process_pricing_config(self, config: Dict[str, Any]):
        """Process pricing configuration data."""
        # Update model pricing from config
        if "models" in config:
            for model_key, model_config in config["models"].items():
                try:
                    pricing = ModelPricing(**model_config)
                    self.model_pricing[model_key] = pricing
                except Exception as e:
                    self.logger.error(f"Error processing model config {model_key}: {str(e)}")
        
        # Load pricing rules
        if "rules" in config:
            for rule_config in config["rules"]:
                try:
                    rule = PricingRule(**rule_config)
                    self.pricing_rules.append(rule)
                except Exception as e:
                    self.logger.error(f"Error processing pricing rule: {str(e)}")
    
    async def get_model_pricing(self, model_id: str, provider: str) -> ModelPricing:
        """
        Get pricing information for a model.
        
        Args:
            model_id: Model identifier
            provider: Provider name
            
        Returns:
            ModelPricing object with current pricing
        """
        # Try exact match first
        key = f"{provider}/{model_id}"
        if key in self.model_pricing:
            pricing = self.model_pricing[key]
            return self._apply_pricing_rules(pricing)
        
        # Try provider-specific fallback
        provider_models = [k for k in self.model_pricing.keys() if k.startswith(f"{provider}/")]
        if provider_models:
            # Use the first matching provider model as fallback
            fallback_key = provider_models[0]
            base_pricing = self.model_pricing[fallback_key]
            
            # Create adjusted pricing for the specific model
            adjusted_pricing = ModelPricing(
                model_id=model_id,
                provider=provider,
                input_price_per_1k=base_pricing.input_price_per_1k,
                output_price_per_1k=base_pricing.output_price_per_1k,
                minimum_charge=base_pricing.minimum_charge,
                tier=base_pricing.tier,
                volume_discounts=base_pricing.volume_discounts,
                rate_limits=base_pricing.rate_limits,
                last_updated=datetime.now()
            )
            
            return self._apply_pricing_rules(adjusted_pricing)
        
        # Generic fallback pricing
        return self._get_fallback_pricing(model_id, provider)
    
    def _apply_pricing_rules(self, base_pricing: ModelPricing) -> ModelPricing:
        """Apply dynamic pricing rules to base pricing."""
        current_time = datetime.now()
        applicable_rules = []
        
        # Find applicable rules
        for rule in self.pricing_rules:
            if rule.valid_until and rule.valid_until < current_time:
                continue
                
            # Check conditions
            if self._check_rule_conditions(rule.conditions, base_pricing):
                applicable_rules.append(rule)
        
        # Apply rules by priority
        applicable_rules.sort(key=lambda r: r.priority, reverse=True)
        
        adjusted_pricing = base_pricing
        for rule in applicable_rules:
            # Apply price adjustment
            adjusted_pricing.input_price_per_1k *= rule.price_adjustment
            adjusted_pricing.output_price_per_1k *= rule.price_adjustment
            
            self.logger.debug(f"Applied pricing rule {rule.rule_id} to {base_pricing.model_id}")
        
        return adjusted_pricing
    
    def _check_rule_conditions(self, conditions: Dict[str, Any], pricing: ModelPricing) -> bool:
        """Check if pricing rule conditions are met."""
        for condition_key, condition_value in conditions.items():
            if condition_key == "provider" and pricing.provider != condition_value:
                return False
            elif condition_key == "tier" and pricing.tier.value != condition_value:
                return False
            elif condition_key == "model_pattern" and condition_value not in pricing.model_id:
                return False
        
        return True
    
    def _get_fallback_pricing(self, model_id: str, provider: str) -> ModelPricing:
        """Get fallback pricing for unknown models."""
        # Default pricing based on provider
        provider_defaults = {
            "openai": {"input": 0.001, "output": 0.002, "tier": PricingTier.BASIC},
            "anthropic": {"input": 0.0008, "output": 0.0024, "tier": PricingTier.BASIC},
            "google": {"input": 0.0005, "output": 0.0015, "tier": PricingTier.BASIC},
            "groq": {"input": 0.0001, "output": 0.0002, "tier": PricingTier.BASIC},
            "together": {"input": 0.0002, "output": 0.0006, "tier": PricingTier.BASIC},
            "mistral": {"input": 0.0003, "output": 0.0009, "tier": PricingTier.BASIC},
            "cohere": {"input": 0.0004, "output": 0.0012, "tier": PricingTier.BASIC},
            "perplexity": {"input": 0.0005, "output": 0.0015, "tier": PricingTier.BASIC},
            "ollama": {"input": 0.0, "output": 0.0, "tier": PricingTier.FREE},
            "openrouter": {"input": 0.0003, "output": 0.0009, "tier": PricingTier.BASIC}
        }
        
        defaults = provider_defaults.get(provider, {"input": 0.001, "output": 0.002, "tier": PricingTier.BASIC})
        
        return ModelPricing(
            model_id=model_id,
            provider=provider,
            input_price_per_1k=defaults["input"],
            output_price_per_1k=defaults["output"],
            minimum_charge=0.00001,
            tier=defaults["tier"],
            volume_discounts={},
            rate_limits={"requests_per_minute": 1000, "tokens_per_minute": 100000},
            last_updated=datetime.now()
        )
    
    def calculate_volume_discount(self, usage_tokens: int, pricing: ModelPricing) -> float:
        """Calculate volume discount multiplier based on usage."""
        if not pricing.volume_discounts:
            return 1.0
        
        # Find applicable discount tier
        applicable_discount = 1.0
        for threshold, discount in sorted(pricing.volume_discounts.items()):
            if usage_tokens >= threshold:
                applicable_discount = discount
            else:
                break
        
        return applicable_discount
    
    def get_cost_estimate(
        self,
        input_tokens: int,
        output_tokens: int,
        pricing: ModelPricing,
        volume_usage: int = 0
    ) -> Dict[str, float]:
        """
        Calculate detailed cost estimate.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            pricing: ModelPricing object
            volume_usage: Total tokens used this billing cycle
            
        Returns:
            Dictionary with cost breakdown
        """
        # Base costs
        input_cost = (input_tokens / 1000) * pricing.input_price_per_1k
        output_cost = (output_tokens / 1000) * pricing.output_price_per_1k
        subtotal = input_cost + output_cost
        
        # Apply volume discount
        volume_discount = self.calculate_volume_discount(volume_usage, pricing)
        discounted_cost = subtotal * volume_discount
        
        # Apply minimum charge
        final_cost = max(discounted_cost, pricing.minimum_charge)
        
        return {
            "input_cost": input_cost,
            "output_cost": output_cost,
            "subtotal": subtotal,
            "volume_discount": volume_discount,
            "discount_amount": subtotal - discounted_cost,
            "final_cost": final_cost,
            "minimum_charge_applied": final_cost == pricing.minimum_charge
        }
    
    def add_pricing_rule(self, rule: PricingRule):
        """Add a new pricing rule."""
        self.pricing_rules.append(rule)
        self.logger.info(f"Added pricing rule: {rule.rule_id}")
    
    def remove_pricing_rule(self, rule_id: str):
        """Remove a pricing rule."""
        self.pricing_rules = [r for r in self.pricing_rules if r.rule_id != rule_id]
        self.logger.info(f"Removed pricing rule: {rule_id}")
    
    def get_provider_models(self, provider: str) -> List[str]:
        """Get all available models for a provider."""
        models = []
        for key, pricing in self.model_pricing.items():
            if pricing.provider == provider:
                models.append(pricing.model_id)
        return models
    
    def get_pricing_summary(self) -> Dict[str, Any]:
        """Get summary of pricing data."""
        provider_counts = {}
        tier_counts = {}
        
        for pricing in self.model_pricing.values():
            provider = pricing.provider
            tier = pricing.tier.value
            
            provider_counts[provider] = provider_counts.get(provider, 0) + 1
            tier_counts[tier] = tier_counts.get(tier, 0) + 1
        
        return {
            "total_models": len(self.model_pricing),
            "providers": provider_counts,
            "tiers": tier_counts,
            "active_rules": len(self.pricing_rules)
        }
    
    def export_pricing_config(self, output_path: str):
        """Export current pricing configuration to file."""
        try:
            config = {
                "models": {},
                "rules": []
            }
            
            # Export model pricing
            for key, pricing in self.model_pricing.items():
                config["models"][key] = asdict(pricing)
            
            # Export pricing rules
            for rule in self.pricing_rules:
                config["rules"].append(asdict(rule))
            
            with open(output_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            self.logger.info(f"Exported pricing config to {output_path}")
            
        except Exception as e:
            self.logger.error(f"Error exporting pricing config: {str(e)}")
            raise