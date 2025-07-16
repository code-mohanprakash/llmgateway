"""
Enhanced Unified Model Bridge - Standalone Version
Central service that manages ALL model providers and routes requests intelligently
"""
import asyncio
import json
import yaml
import os
from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path
from dataclasses import asdict
import time
import logging
import uuid
from datetime import datetime, timedelta

from providers.base import (
    BaseModelProvider, 
    GenerationRequest, 
    GenerationResponse, 
    ModelMetadata, 
    ModelCapability
)

# Import all providers with error handling
from providers.openai import OpenAIProvider
from providers.anthropic import AnthropicProvider
from providers.google import GoogleProvider

# Import optional providers with error handling
try:
    from providers.groq import GroqProvider
    GROQ_AVAILABLE = True
except ImportError:
    GroqProvider = None
    GROQ_AVAILABLE = False

try:
    from providers.together import TogetherProvider
    TOGETHER_AVAILABLE = True
except ImportError:
    TogetherProvider = None
    TOGETHER_AVAILABLE = False

try:
    from providers.mistral import MistralProvider
    MISTRAL_AVAILABLE = True
except ImportError:
    MistralProvider = None
    MISTRAL_AVAILABLE = False

try:
    from providers.cohere import CohereProvider
    COHERE_AVAILABLE = True
except ImportError:
    CohereProvider = None
    COHERE_AVAILABLE = False

try:
    from providers.perplexity import PerplexityProvider
    PERPLEXITY_AVAILABLE = True
except ImportError:
    PerplexityProvider = None
    PERPLEXITY_AVAILABLE = False

try:
    from providers.huggingface import HuggingFaceProvider
    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HuggingFaceProvider = None
    HUGGINGFACE_AVAILABLE = False

try:
    from providers.ollama_enhanced import OllamaEnhancedProvider
    OLLAMA_AVAILABLE = True
except ImportError:
    OllamaEnhancedProvider = None
    OLLAMA_AVAILABLE = False

try:
    from providers.openrouter import OpenRouterProvider
    OPENROUTER_AVAILABLE = True
except ImportError:
    OpenRouterProvider = None
    OPENROUTER_AVAILABLE = False

try:
    from providers.deepseek import DeepSeekProvider
    DEEPSEEK_AVAILABLE = True
except ImportError:
    DeepSeekProvider = None
    DEEPSEEK_AVAILABLE = False

try:
    from providers.mock import MockProvider
    MOCK_AVAILABLE = True
except ImportError:
    MockProvider = None
    MOCK_AVAILABLE = False

from utils.config import Config
from utils.logging_setup import get_logger

logger = get_logger(__name__)


class IntelligentRouter:
    """Enhanced intelligent router for smart provider selection"""
    
    def __init__(self):
        self.performance_history = {}
        self.cost_predictions = {}
        self.user_preferences = {}
        self.provider_health_cache = {}
        self.last_health_check = None
        self.health_check_interval = 300  # 5 minutes
        
    def analyze_request_characteristics(self, request: GenerationRequest) -> Dict[str, Any]:
        """Analyze request to determine optimal routing strategy"""
        characteristics = {
            "complexity": "medium",
            "urgency": "normal",
            "cost_sensitivity": "medium",
            "quality_requirement": "medium",
            "task_type": getattr(request, 'task_type', None) or "general"
        }
        
        # Analyze prompt length and complexity
        prompt_length = len(request.prompt)
        if prompt_length < 100:
            characteristics["complexity"] = "simple"
        elif prompt_length > 1000:
            characteristics["complexity"] = "complex"
        
        # Analyze task type for routing
        task_type = getattr(request, 'task_type', None)
        if task_type:
            if task_type in ["sentiment_analysis", "triage", "outcome_detection"]:
                characteristics["urgency"] = "high"
                characteristics["cost_sensitivity"] = "high"
            elif task_type in ["critique", "refinement", "initial_analysis_complex"]:
                characteristics["quality_requirement"] = "high"
                characteristics["cost_sensitivity"] = "low"
        
        # Override with explicit complexity
        complexity = getattr(request, 'complexity', None)
        if complexity:
            characteristics["complexity"] = complexity
        
        return characteristics
    
    def get_provider_ranking(self, characteristics: Dict[str, Any], available_providers: Dict[str, BaseModelProvider]) -> List[Tuple[str, float]]:
        """Rank providers based on request characteristics and performance history"""
        rankings = []
        
        for provider_name, provider in available_providers.items():
            score = self._calculate_provider_score(provider_name, characteristics)
            rankings.append((provider_name, score))
        
        # Sort by score (higher is better)
        rankings.sort(key=lambda x: x[1], reverse=True)
        return rankings
    
    def _calculate_provider_score(self, provider_name: str, characteristics: Dict[str, Any]) -> float:
        """Calculate provider score based on characteristics and performance"""
        score = 0.0
        
        # Base score
        score += 50.0
        
        # Performance-based scoring
        if provider_name in self.performance_history:
            perf = self.performance_history[provider_name]
            success_rate = perf.get("success_rate", 0.5)
            avg_response_time = perf.get("avg_response_time", 5.0)
            avg_cost = perf.get("avg_cost", 0.01)
            
            # Success rate bonus (0-20 points)
            score += success_rate * 20
            
            # Response time bonus (0-15 points)
            if avg_response_time < 2.0:
                score += 15
            elif avg_response_time < 5.0:
                score += 10
            elif avg_response_time < 10.0:
                score += 5
            
            # Cost optimization (0-15 points)
            if characteristics["cost_sensitivity"] == "high":
                if avg_cost < 0.001:
                    score += 15
                elif avg_cost < 0.01:
                    score += 10
                elif avg_cost < 0.05:
                    score += 5
            elif characteristics["cost_sensitivity"] == "low":
                # Prefer higher quality (cost) for complex tasks
                if avg_cost > 0.01:
                    score += 10
        
        # Characteristic-based scoring
        if characteristics["urgency"] == "high":
            # Prefer fast providers
            if provider_name in ["groq", "openai", "google"]:
                score += 10
        elif characteristics["quality_requirement"] == "high":
            # Prefer high-quality providers
            if provider_name in ["anthropic", "openai"]:
                score += 15
        
        # Health check penalty
        if provider_name in self.provider_health_cache:
            health = self.provider_health_cache[provider_name]
            if health.get("status") != "healthy":
                score -= 50  # Heavy penalty for unhealthy providers
        
        return max(0.0, score)  # Ensure non-negative score
    
    async def update_performance_history(self, provider_name: str, response_time: float, cost: float, success: bool):
        """Update performance history for a provider"""
        if provider_name not in self.performance_history:
            self.performance_history[provider_name] = {
                "total_requests": 0,
                "successful_requests": 0,
                "total_response_time": 0,
                "total_cost": 0,
                "avg_response_time": 0,
                "avg_cost": 0,
                "success_rate": 0,
                "last_updated": datetime.utcnow()
            }
        
        perf = self.performance_history[provider_name]
        perf["total_requests"] += 1
        perf["total_response_time"] += response_time
        perf["total_cost"] += cost
        perf["last_updated"] = datetime.utcnow()
        
        if success:
            perf["successful_requests"] += 1
        
        # Update averages
        perf["avg_response_time"] = perf["total_response_time"] / perf["total_requests"]
        perf["avg_cost"] = perf["total_cost"] / perf["total_requests"]
        perf["success_rate"] = perf["successful_requests"] / perf["total_requests"]
    
    async def update_provider_health(self, provider_name: str, health_status: Dict[str, Any]):
        """Update provider health cache"""
        self.provider_health_cache[provider_name] = health_status
        self.last_health_check = datetime.utcnow()
    
    def get_routing_recommendations(self) -> Dict[str, Any]:
        """Get routing recommendations for dashboard"""
        recommendations = {
            "top_performers": [],
            "cost_optimizers": [],
            "speed_optimizers": [],
            "quality_optimizers": [],
            "health_status": self.provider_health_cache.copy()
        }
        
        # Sort providers by different metrics
        providers_by_success = sorted(
            self.performance_history.items(),
            key=lambda x: x[1].get("success_rate", 0),
            reverse=True
        )
        
        providers_by_cost = sorted(
            self.performance_history.items(),
            key=lambda x: x[1].get("avg_cost", float('inf'))
        )
        
        providers_by_speed = sorted(
            self.performance_history.items(),
            key=lambda x: x[1].get("avg_response_time", float('inf'))
        )
        
        # Top 3 in each category
        recommendations["top_performers"] = [
            {"provider": name, "success_rate": perf.get("success_rate", 0)}
            for name, perf in providers_by_success[:3]
        ]
        
        recommendations["cost_optimizers"] = [
            {"provider": name, "avg_cost": perf.get("avg_cost", 0)}
            for name, perf in providers_by_cost[:3]
        ]
        
        recommendations["speed_optimizers"] = [
            {"provider": name, "avg_response_time": perf.get("avg_response_time", 0)}
            for name, perf in providers_by_speed[:3]
        ]
        
        return recommendations


class ModelAlias:
    """Configuration for model aliases"""
    def __init__(self, alias: str, provider: str, model_id: str, priority: int = 0):
        self.alias = alias
        self.provider = provider
        self.model_id = model_id
        self.priority = priority


class EnhancedModelBridge:
    """Enhanced central gateway for ALL LLM providers with intelligent routing"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "models_config.yaml"
        self.providers: Dict[str, BaseModelProvider] = {}
        self.model_aliases: Dict[str, List[ModelAlias]] = {}
        self.provider_configs: Dict[str, Dict[str, Any]] = {}
        self.task_routing: Dict[str, Dict[str, str]] = {}
        self._initialized = False
        self._fallback_enabled = True
        self._cost_optimization = True
        self._performance_tracking = True
        
        # Enhanced intelligent routing
        self.intelligent_router = IntelligentRouter()
        
        # Performance tracking
        self.performance_stats: Dict[str, Dict[str, Any]] = {}
        
        # Initialize configuration
        self.config = Config()
        
        # All available provider classes (only those with dependencies installed)
        self.provider_classes = {
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
            "google": GoogleProvider,
        }
        
        # Add optional providers if available
        if GROQ_AVAILABLE:
            self.provider_classes["groq"] = GroqProvider
        if TOGETHER_AVAILABLE:
            self.provider_classes["together"] = TogetherProvider
        if MISTRAL_AVAILABLE:
            self.provider_classes["mistral"] = MistralProvider
        if COHERE_AVAILABLE:
            self.provider_classes["cohere"] = CohereProvider
        if PERPLEXITY_AVAILABLE:
            self.provider_classes["perplexity"] = PerplexityProvider
        if HUGGINGFACE_AVAILABLE:
            self.provider_classes["huggingface"] = HuggingFaceProvider
        if OLLAMA_AVAILABLE:
            self.provider_classes["ollama"] = OllamaEnhancedProvider
        if OPENROUTER_AVAILABLE:
            self.provider_classes["openrouter"] = OpenRouterProvider
        if DEEPSEEK_AVAILABLE:
            self.provider_classes["deepseek"] = DeepSeekProvider
        if MOCK_AVAILABLE:
            self.provider_classes["mock"] = MockProvider
        
        logger.info(f"Available provider classes: {list(self.provider_classes.keys())}")
        
        # Load configuration
        self._load_configuration()
        
        # Setup model aliases
        self._setup_dynamic_model_aliases(self.model_aliases)
    
    async def initialize(self, force_reload: bool = False) -> bool:
        """Initialize the gateway and all providers"""
        if self._initialized and not force_reload:
            return True
        
        try:
            # Load configuration
            gateway_config = self._load_configuration()
            
            # Set gateway settings
            self._fallback_enabled = gateway_config.get("gateway", {}).get("fallback_enabled", True)
            self._cost_optimization = gateway_config.get("gateway", {}).get("cost_optimization", True)
            self._performance_tracking = gateway_config.get("gateway", {}).get("performance_tracking", True)
            
            # Initialize only providers with valid API keys
            initialization_results = []
            available_providers = self.config.available_providers
            
            logger.info(f"Available providers with API keys: {available_providers}")
            
            if not available_providers:
                logger.warning("No providers with valid API keys found. Please set at least one API key.")
                return False
            
            for provider_name in available_providers:
                if provider_name not in self.provider_classes:
                    logger.warning(f"Provider {provider_name} not supported or dependencies not installed, skipping")
                    continue
                
                provider_config = gateway_config.get("providers", {}).get(provider_name, {})
                provider_config["api_key"] = self.config.providers[provider_name].api_key
                provider_config["enabled"] = True
                provider_config["priority"] = self.config.providers[provider_name].priority
                
                try:
                    result = await self._initialize_provider(provider_name, provider_config)
                    initialization_results.append(result)
                except Exception as e:
                    logger.error(f"Failed to initialize provider {provider_name}: {str(e)}")
                    initialization_results.append(False)
            
            # Setup model aliases based on available providers
            self._setup_dynamic_model_aliases(gateway_config.get("model_aliases", {}))
            
            # Setup task routing
            self.task_routing = gateway_config.get("task_routing", {})
            
            # Check if at least one provider initialized successfully
            if any(initialization_results):
                self._initialized = True
                logger.info(f"Enhanced Model Bridge initialized with {len(self.providers)} providers")
                await self._log_available_models()
                return True
            else:
                logger.error("No providers initialized successfully")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize Enhanced Model Bridge: {str(e)}")
            return False
    
    def _setup_dynamic_model_aliases(self, aliases_config: Dict[str, List[Dict[str, Any]]]):
        """Setup model aliases based on available providers"""
        self.model_aliases = {}
        
        for alias_name, alias_configs in aliases_config.items():
            available_aliases = []
            
            for alias_config in alias_configs:
                provider = alias_config.get("provider")
                model_id = alias_config.get("model_id")
                priority = alias_config.get("priority", 999)
                
                # Only include aliases for available providers
                if provider in self.providers:
                    available_aliases.append(ModelAlias(alias_name, provider, model_id, priority))
            
            if available_aliases:
                # Sort by priority (lower number = higher priority)
                available_aliases.sort(key=lambda x: x.priority)
                self.model_aliases[alias_name] = available_aliases
                logger.info(f"Setup alias '{alias_name}' with {len(available_aliases)} available models")
    
    async def _log_available_models(self):
        """Log all available models for debugging"""
        total_models = 0
        for provider_name, provider in self.providers.items():
            models = provider.get_available_models()
            total_models += len(models)
            logger.info(f"Provider {provider_name}: {len(models)} models available")
        
        logger.info(f"Total models available across all providers: {total_models}")
    
    def _load_configuration(self) -> Dict[str, Any]:
        """Load gateway configuration from file or create default"""
        config_path = Path(self.config_path)
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f) if config_path.suffix.lower() == '.yaml' else json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {str(e)}")
        
        # Create and save default configuration
        default_config = self._get_default_configuration()
        self._save_configuration(default_config)
        return default_config
    
    def _get_default_configuration(self) -> Dict[str, Any]:
        """Get default gateway configuration"""
        return {
            "gateway": {
                "fallback_enabled": True,
                "timeout": 60,
                "max_retries": 3,
                "cost_optimization": True,
                "performance_tracking": True
            },
            "providers": {
                "openai": {
                    "enabled": True,
                    "priority": 1,
                    "api_key": None,
                    "temperature": 0.1
                },
                "anthropic": {
                    "enabled": True,
                    "priority": 2,
                    "api_key": None,
                    "temperature": 0.1
                },
                "google": {
                    "enabled": True,
                    "priority": 3,
                    "api_key": None,
                    "temperature": 0.1
                },
                "ollama": {
                    "enabled": True,
                    "priority": 10,
                    "base_url": "http://localhost:11434",
                    "auto_pull": True
                }
            },
            "model_aliases": {
                "fastest": [
                    {"provider": "openrouter", "model_id": "deepseek/deepseek-r1-0528:free", "priority": 1},
                    {"provider": "groq", "model_id": "llama3-8b-8192", "priority": 2},
                    {"provider": "ollama", "model_id": "llama3:8b", "priority": 3}
                ],
                "cheapest": [
                    {"provider": "openrouter", "model_id": "deepseek/deepseek-r1-0528:free", "priority": 1},
                    {"provider": "ollama", "model_id": "llama3:8b", "priority": 2},
                    {"provider": "google", "model_id": "gemini-1.5-flash", "priority": 3}
                ],
                "best": [
                    {"provider": "openrouter", "model_id": "deepseek/deepseek-r1", "priority": 1},
                    {"provider": "anthropic", "model_id": "claude-3-opus", "priority": 2},
                    {"provider": "openai", "model_id": "gpt-4-turbo", "priority": 3}
                ],
                "balanced": [
                    {"provider": "openrouter", "model_id": "deepseek/deepseek-r1-0528:free", "priority": 1},
                    {"provider": "anthropic", "model_id": "claude-3-sonnet", "priority": 2},
                    {"provider": "openai", "model_id": "gpt-4", "priority": 3},
                    {"provider": "google", "model_id": "gemini-1.5-pro", "priority": 4}
                ],
                "fast": [
                    {"provider": "openrouter", "model_id": "deepseek/deepseek-r1-0528:free", "priority": 1},
                    {"provider": "groq", "model_id": "llama3-8b-8192", "priority": 2},
                    {"provider": "google", "model_id": "gemini-1.5-flash", "priority": 3},
                    {"provider": "ollama", "model_id": "llama3:8b", "priority": 4}
                ],
                "powerful": [
                    {"provider": "openrouter", "model_id": "deepseek/deepseek-r1", "priority": 1},
                    {"provider": "anthropic", "model_id": "claude-3-opus", "priority": 2},
                    {"provider": "openai", "model_id": "gpt-4-turbo", "priority": 3},
                    {"provider": "google", "model_id": "gemini-1.5-pro", "priority": 4}
                ],
                "default_balanced": [
                    {"provider": "openrouter", "model_id": "deepseek/deepseek-r1-0528:free", "priority": 1},
                    {"provider": "anthropic", "model_id": "claude-3-sonnet", "priority": 2},
                    {"provider": "openai", "model_id": "gpt-4", "priority": 3},
                    {"provider": "google", "model_id": "gemini-1.5-pro", "priority": 4}
                ]
            },
            "task_routing": {
                "triage": "fast",
                "outcome_detection": "fast",
                "initial_analysis_simple": "fast",
                "initial_analysis_complex": "powerful",
                "critique": "powerful",
                "refinement": "powerful",
                "sentiment_analysis": "fast",
                "competitor_extraction": "default_balanced",
                "product_feedback_extraction": "default_balanced",
                "action_item_extraction": "default_balanced",
                "summary_generation": "fast"
            }
        }
    
    def _save_configuration(self, config_data: Dict[str, Any]):
        """Save configuration to file"""
        try:
            config_path = Path(self.config_path)
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w') as f:
                if config_path.suffix.lower() == '.yaml':
                    yaml.dump(config_data, f, indent=2)
                else:
                    json.dump(config_data, f, indent=2)
            
            logger.info(f"Configuration saved to {config_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {str(e)}")
    
    async def _initialize_provider(self, provider_name: str, provider_config: Dict[str, Any]) -> bool:
        """Initialize a single provider"""
        try:
            provider_class = self.provider_classes.get(provider_name)
            if not provider_class:
                logger.error(f"Unknown provider type: {provider_name}")
                return False
            
            # Create provider instance
            provider = provider_class(provider_config)
            
            # Initialize provider
            success = await provider.initialize()
            if success:
                self.providers[provider_name] = provider
                self.provider_configs[provider_name] = provider_config
                logger.info(f"Provider {provider_name} initialized successfully")
                return True
            else:
                logger.warning(f"Provider {provider_name} failed to initialize")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing provider {provider_name}: {str(e)}")
            return False
    
    async def generate_text(
        self,
        prompt: str,
        model: str = "balanced",
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        task_type: Optional[str] = None,
        complexity: Optional[str] = None,
        **kwargs
    ) -> GenerationResponse:
        """Generate text with intelligent routing"""
        
        # Create request
        request = GenerationRequest(
            prompt=prompt,
            system_message=system_message,
            temperature=temperature,
            max_tokens=max_tokens,
            extra_params=kwargs
        )
        
        # Intelligent model selection
        selected_model = await self._select_optimal_model(
            model, task_type, complexity, ModelCapability.TEXT_GENERATION
        )
        
        # Route request
        return await self._route_request(request, selected_model, "generate_text")
    
    async def generate_structured_output(
        self,
        prompt: str,
        schema: Dict[str, Any],
        model: str = "balanced",
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        task_type: Optional[str] = None,
        complexity: Optional[str] = None,
        **kwargs
    ) -> GenerationResponse:
        """Generate structured JSON output with intelligent routing"""
        
        # Create request
        request = GenerationRequest(
            prompt=prompt,
            system_message=system_message,
            temperature=temperature,
            output_schema=schema,
            extra_params=kwargs
        )
        
        # Intelligent model selection
        selected_model = await self._select_optimal_model(
            model, task_type, complexity, ModelCapability.STRUCTURED_OUTPUT
        )
        
        # Route request
        return await self._route_request(request, selected_model, "generate_structured_output")
    
    async def _select_optimal_model(
        self, 
        model_spec: str, 
        task_type: Optional[str], 
        complexity: Optional[str],
        required_capability: ModelCapability
    ) -> str:
        """Intelligently select the optimal model based on task requirements"""
        
        # Task-based routing
        if task_type and complexity and task_type in self.task_routing:
            task_config = self.task_routing[task_type]
            if f"complexity_{complexity}" in task_config:
                model_spec = task_config[f"complexity_{complexity}"]
        
        # Cost optimization
        if self._cost_optimization and complexity == "simple":
            model_spec = "cheapest"
        elif self._cost_optimization and complexity == "complex":
            model_spec = "best"
        
        return model_spec
    
    async def _route_request(
        self, 
        request: GenerationRequest, 
        model_spec: str, 
        method_name: str
    ) -> GenerationResponse:
        """Route request through providers with intelligent routing and fallback"""
        
        # Analyze request characteristics for intelligent routing
        characteristics = self.intelligent_router.analyze_request_characteristics(request)
        
        # Get provider rankings based on characteristics
        provider_rankings = self.intelligent_router.get_provider_ranking(characteristics, self.providers)
        
        # Resolve model specification to provider/model pairs
        model_options = self._resolve_model_spec(model_spec)
        
        # Reorder model options based on intelligent routing
        if provider_rankings:
            # Create a mapping of provider names to their rankings
            provider_rank_map = {name: rank for name, rank in provider_rankings}
            
            # Sort model options by provider ranking
            model_options.sort(key=lambda alias: provider_rank_map.get(alias.provider, 0), reverse=True)
        
        last_error = None
        
        for alias in model_options:
            provider = self.providers.get(alias.provider)
            if not provider:
                continue
            
            try:
                # Check if provider supports required capability
                if hasattr(request, 'output_schema') and request.output_schema:
                    if not provider.supports_capability(alias.model_id, ModelCapability.STRUCTURED_OUTPUT):
                        continue
                
                # Track performance
                start_time = time.time()
                
                # Make request
                method = getattr(provider, method_name)
                response = await method(request, alias.model_id)
                
                # Update performance stats
                if self._performance_tracking:
                    self._update_performance_stats(
                        alias.provider, 
                        alias.model_id, 
                        response.response_time or (time.time() - start_time),
                        response.cost or 0,
                        not response.error
                    )
                
                # Update intelligent router performance history
                if response.response_time is not None:
                    await self.intelligent_router.update_performance_history(
                        alias.provider, 
                        response.response_time, 
                        response.cost or 0, 
                        not response.error
                    )
                
                # Update provider health cache
                if response.error:
                    await self.intelligent_router.update_provider_health(
                        alias.provider, 
                        {"status": "unhealthy", "error": response.error}
                    )
                else:
                    await self.intelligent_router.update_provider_health(
                        alias.provider, 
                        {"status": "healthy"}
                    )
                
                # Return successful response
                if not response.error:
                    return response
                
                last_error = response.error
                
                # If fallback is disabled, return first response
                if not self._fallback_enabled:
                    return response
                    
            except Exception as e:
                last_error = str(e)
                logger.error(f"Error with provider {alias.provider}, model {alias.model_id}: {str(e)}")
                continue
        
        # All providers failed
        return GenerationResponse(
            content="",
            model_id=model_spec,
            provider_name="gateway",
            error=f"All providers failed. Last error: {last_error}"
        )
    
    def _resolve_model_spec(self, model_spec: str) -> List[ModelAlias]:
        """Resolve model specification to list of provider/model pairs"""
        
        # Check if it's an alias
        if model_spec in self.model_aliases:
            return self.model_aliases[model_spec]
        
        # Check if it's a direct provider:model specification
        if ":" in model_spec:
            provider_name, model_id = model_spec.split(":", 1)
            if provider_name in self.providers:
                return [ModelAlias(model_spec, provider_name, model_id, 1)]
        
        # Check if it's a model ID that exists in any provider
        for provider_name, provider in self.providers.items():
            models = provider.get_available_models()
            for model_metadata in models:
                if model_metadata.model_id == model_spec:
                    return [ModelAlias(model_spec, provider_name, model_spec, 1)]
        
        # Fallback to balanced alias
        return self.model_aliases.get("balanced", [])
    
    def _update_performance_stats(
        self, 
        provider: str, 
        model_id: str, 
        response_time: float, 
        cost: float, 
        success: bool
    ):
        """Update performance statistics"""
        key = f"{provider}:{model_id}"
        
        if key not in self.performance_stats:
            self.performance_stats[key] = {
                "total_requests": 0,
                "successful_requests": 0,
                "total_response_time": 0,
                "total_cost": 0,
                "avg_response_time": 0,
                "avg_cost": 0,
                "success_rate": 0
            }
        
        stats = self.performance_stats[key]
        stats["total_requests"] += 1
        stats["total_response_time"] += response_time
        stats["total_cost"] += cost
        
        if success:
            stats["successful_requests"] += 1
        
        # Update averages
        stats["avg_response_time"] = stats["total_response_time"] / stats["total_requests"]
        stats["avg_cost"] = stats["total_cost"] / stats["total_requests"]
        stats["success_rate"] = stats["successful_requests"] / stats["total_requests"]
    
    def get_available_models(self) -> Dict[str, List[ModelMetadata]]:
        """Get all available models from all providers"""
        all_models = {}
        for provider_name, provider in self.providers.items():
            all_models[provider_name] = provider.get_available_models()
        return all_models
    
    def get_model_aliases(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all configured model aliases"""
        aliases = {}
        for alias_name, alias_list in self.model_aliases.items():
            aliases[alias_name] = [
                {
                    "provider": alias.provider,
                    "model_id": alias.model_id,
                    "priority": alias.priority
                }
                for alias in alias_list
            ]
        return aliases
    
    def get_performance_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get performance statistics for all models"""
        return self.performance_stats.copy()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of all providers"""
        health_results = {}
        overall_healthy = False
        
        for provider_name, provider in self.providers.items():
            try:
                health_result = await provider.health_check()
                health_results[provider_name] = health_result
                if health_result.get("status") == "healthy":
                    overall_healthy = True
            except Exception as e:
                health_results[provider_name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "provider": provider_name
                }
        
        return {
            "status": "healthy" if overall_healthy else "unhealthy",
            "providers": health_results,
            "total_providers": len(self.providers),
            "healthy_providers": sum(1 for result in health_results.values() if result.get("status") == "healthy"),
            "gateway_features": {
                "fallback_enabled": self._fallback_enabled,
                "cost_optimization": self._cost_optimization,
                "performance_tracking": self._performance_tracking
            }
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive gateway statistics"""
        total_models = sum(len(provider.get_available_models()) for provider in self.providers.values())
        
        return {
            "providers_initialized": len(self.providers),
            "total_models": total_models,
            "model_aliases": len(self.model_aliases),
            "performance_stats": self.performance_stats,
            "gateway_config": {
                "fallback_enabled": self._fallback_enabled,
                "cost_optimization": self._cost_optimization,
                "performance_tracking": self._performance_tracking
            }
        }

    def get_routing_recommendations(self) -> Dict[str, Any]:
        """Get routing recommendations for dashboard"""
        return self.intelligent_router.get_routing_recommendations()


# Global gateway instance
enhanced_gateway = EnhancedModelBridge()

# Convenience functions for backward compatibility
async def generate_text(*args, **kwargs) -> GenerationResponse:
    """Generate text using the enhanced gateway"""
    if not enhanced_gateway._initialized:
        await enhanced_gateway.initialize()
    return await enhanced_gateway.generate_text(*args, **kwargs)

async def generate_structured_output(*args, **kwargs) -> GenerationResponse:
    """Generate structured output using the enhanced gateway"""
    if not enhanced_gateway._initialized:
        await enhanced_gateway.initialize()
    return await enhanced_gateway.generate_structured_output(*args, **kwargs)

async def initialize_gateway() -> bool:
    """Initialize the enhanced gateway"""
    return await enhanced_gateway.initialize()

# Main gateway export
model_bridge = enhanced_gateway