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

# Import advanced routing components
try:
    from advanced_routing import LoadBalancer, LoadBalancingStrategy, PredictiveRouter, WeightManager, GeoRouter, LatencyMonitor
    ADVANCED_ROUTING_AVAILABLE = True
except ImportError:
    LoadBalancer = None
    LoadBalancingStrategy = None
    PredictiveRouter = None
    WeightManager = None
    GeoRouter = None
    LatencyMonitor = None
    ADVANCED_ROUTING_AVAILABLE = False

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
        
        # Advanced load balancer (if available)
        if ADVANCED_ROUTING_AVAILABLE:
            self.load_balancer = LoadBalancer(LoadBalancingStrategy.INTELLIGENT)
            self._load_balancer_enabled = True
            logger.info("Advanced load balancer enabled")
            
            # Predictive router
            self.predictive_router = PredictiveRouter()
            self._predictive_routing_enabled = True
            logger.info("Predictive routing enabled")
            
            # Weight manager
            self.weight_manager = WeightManager()
            self._weight_management_enabled = True
            logger.info("Dynamic weight management enabled")
            
            # Geographic router
            self.geo_router = GeoRouter()
            self._geo_routing_enabled = True
            logger.info("Geographic routing enabled")
            
            # Latency monitor
            self.latency_monitor = LatencyMonitor()
            self._latency_monitoring_enabled = True
            logger.info("Latency monitoring enabled")
        else:
            self.load_balancer = None
            self._load_balancer_enabled = False
            self.predictive_router = None
            self._predictive_routing_enabled = False
            self.weight_manager = None
            self._weight_management_enabled = False
            self.geo_router = None
            self._geo_routing_enabled = False
            self.latency_monitor = None
            self._latency_monitoring_enabled = False
            logger.info("Advanced routing not available, using fallback routing")
        
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
            
            # Initialize load balancer if available
            if self._load_balancer_enabled:
                await self.load_balancer.initialize()
            
            # Initialize weight manager if available
            if self._weight_management_enabled:
                await self.weight_manager.start()
            
            # Initialize latency monitor if available
            if self._latency_monitoring_enabled:
                await self.latency_monitor.start_monitoring()
                
            # Connect geo router to latency monitor
            if self._geo_routing_enabled and self._latency_monitoring_enabled:
                self.geo_router.set_latency_monitor(self.latency_monitor)
            
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
                
                # Register with load balancer if available
                if self._load_balancer_enabled:
                    base_weight = provider_config.get("priority", 1)
                    # Convert priority to weight (lower priority = higher weight)
                    weight = 1.0 / max(base_weight, 0.1)
                    self.load_balancer.register_provider(provider_name, provider, weight)
                
                # Register with predictive router if available
                if self._predictive_routing_enabled:
                    self.predictive_router.register_provider(provider_name, provider)
                
                # Register with weight manager if available
                if self._weight_management_enabled:
                    base_weight = provider_config.get("priority", 1)
                    # Convert priority to weight (lower priority = higher weight)
                    weight = 1.0 / max(base_weight, 0.1)
                    self.weight_manager.register_provider(provider_name, weight)
                
                # Register with latency monitor if available
                if self._latency_monitoring_enabled:
                    # Get provider endpoints from config or use defaults
                    endpoints = provider_config.get("endpoints", [])
                    if not endpoints:
                        # Use default endpoints based on provider
                        default_endpoints = {
                            'openai': ['https://api.openai.com/v1/models'],
                            'anthropic': ['https://api.anthropic.com/v1/models'],
                            'google': ['https://generativelanguage.googleapis.com/v1/models'],
                            'groq': ['https://api.groq.com/openai/v1/models']
                        }
                        endpoints = default_endpoints.get(provider_name, [])
                    
                    if endpoints:
                        self.latency_monitor.register_provider(provider_name, endpoints)
                
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
        
        # Use predictive routing if available
        if self._predictive_routing_enabled:
            return await self._route_with_predictive_routing(request, model_spec, method_name, characteristics)
        elif self._load_balancer_enabled:
            return await self._route_with_load_balancer(request, model_spec, method_name, characteristics)
        
        # Fallback to original routing logic
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
    
    async def _route_with_load_balancer(
        self, 
        request: GenerationRequest, 
        model_spec: str, 
        method_name: str, 
        characteristics: Dict[str, Any]
    ) -> GenerationResponse:
        """Route request using the advanced load balancer"""
        
        # Resolve model specification to provider/model pairs
        model_options = self._resolve_model_spec(model_spec)
        
        # Try each model option with load balancer provider selection
        last_error = None
        
        for alias in model_options:
            try:
                # Check if model supports required capability
                provider = self.providers.get(alias.provider)
                if not provider:
                    continue
                
                if hasattr(request, 'output_schema') and request.output_schema:
                    if not provider.supports_capability(alias.model_id, ModelCapability.STRUCTURED_OUTPUT):
                        continue
                
                # Use load balancer to select optimal provider for this model type
                selected_provider = await self.load_balancer.select_provider(characteristics)
                if not selected_provider or selected_provider != alias.provider:
                    continue
                
                # Execute request through load balancer
                response = await self.load_balancer.execute_request(
                    selected_provider, request, alias.model_id, method_name
                )
                
                # Update performance stats
                if self._performance_tracking and response.response_time is not None:
                    self._update_performance_stats(
                        alias.provider, 
                        alias.model_id, 
                        response.response_time,
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
                
                # Return successful response
                if not response.error:
                    return response
                
                last_error = response.error
                
                # If fallback is disabled, return first response
                if not self._fallback_enabled:
                    return response
                    
            except Exception as e:
                last_error = str(e)
                logger.error(f"Error with load balanced provider {alias.provider}, model {alias.model_id}: {str(e)}")
                continue
        
        # All providers failed
        return GenerationResponse(
            content="",
            model_id=model_spec,
            provider_name="gateway",
            error=f"All load balanced providers failed. Last error: {last_error}"
        )
    
    async def _route_with_predictive_routing(
        self, 
        request: GenerationRequest, 
        model_spec: str, 
        method_name: str, 
        characteristics: Dict[str, Any]
    ) -> GenerationResponse:
        """Route request using predictive routing with ML-based predictions"""
        
        # Resolve model specification to provider/model pairs
        model_options = self._resolve_model_spec(model_spec)
        
        # Get available providers for prediction
        available_providers = []
        provider_model_map = {}
        
        for alias in model_options:
            if alias.provider in self.providers:
                available_providers.append(alias.provider)
                provider_model_map[alias.provider] = alias.model_id
        
        if not available_providers:
            return GenerationResponse(
                content="",
                model_id=model_spec,
                provider_name="gateway",
                error="No available providers for predictive routing"
            )
        
        # Get predictive routing recommendation
        try:
            prediction = await self.predictive_router.predict_optimal_routing(
                request, available_providers
            )
            
            # Try providers in order of prediction confidence
            providers_to_try = [
                (prediction.primary_provider, prediction.primary_confidence, provider_model_map[prediction.primary_provider])
            ]
            
            # Add alternatives
            for alt in prediction.alternative_providers:
                if alt['provider'] in provider_model_map:
                    providers_to_try.append((
                        alt['provider'], 
                        alt['confidence'], 
                        provider_model_map[alt['provider']]
                    ))
            
            last_error = None
            
            for provider_name, confidence, model_id in providers_to_try:
                try:
                    provider = self.providers[provider_name]
                    
                    # Check if provider supports required capability
                    if hasattr(request, 'output_schema') and request.output_schema:
                        if not provider.supports_capability(model_id, ModelCapability.STRUCTURED_OUTPUT):
                            continue
                    
                    # Execute request
                    start_time = time.time()
                    method = getattr(provider, method_name)
                    response = await method(request, model_id)
                    execution_time = time.time() - start_time
                    
                    # Update predictive router with training data
                    self.predictive_router.add_training_data(
                        provider_name, request, execution_time, not response.error
                    )
                    
                    # Update weight manager with performance data
                    if self._weight_management_enabled:
                        self.weight_manager.record_performance(
                            provider_name, execution_time, not response.error, 
                            response.cost or 0.0, 1.0  # availability
                        )
                    
                    # Update performance stats
                    if self._performance_tracking and response.response_time is not None:
                        self._update_performance_stats(
                            provider_name, 
                            model_id, 
                            response.response_time,
                            response.cost or 0,
                            not response.error
                        )
                    
                    # Update intelligent router performance history
                    if response.response_time is not None:
                        await self.intelligent_router.update_performance_history(
                            provider_name, 
                            response.response_time, 
                            response.cost or 0, 
                            not response.error
                        )
                    
                    # Add prediction metadata to response
                    if hasattr(response, 'metadata'):
                        response.metadata = response.metadata or {}
                    else:
                        response.metadata = {}
                    
                    response.metadata.update({
                        'prediction_confidence': confidence,
                        'predicted_response_time': prediction.predicted_response_time,
                        'predicted_success_rate': prediction.predicted_success_rate,
                        'prediction_reasoning': prediction.reasoning,
                        'pattern_match': prediction.pattern_match
                    })
                    
                    # Return successful response
                    if not response.error:
                        logger.info(f"Predictive routing successful: {provider_name} (confidence: {confidence:.2f})")
                        return response
                    
                    last_error = response.error
                    
                    # If fallback is disabled, return first response
                    if not self._fallback_enabled:
                        return response
                        
                except Exception as e:
                    last_error = str(e)
                    logger.error(f"Error with predictive routing provider {provider_name}: {str(e)}")
                    
                    # Still add training data for failures
                    execution_time = time.time() - start_time if 'start_time' in locals() else 0
                    self.predictive_router.add_training_data(
                        provider_name, request, execution_time, False
                    )
                    
                    # Update weight manager with failure data
                    if self._weight_management_enabled:
                        self.weight_manager.record_performance(
                            provider_name, execution_time, False, 0.0, 0.0  # Failed request
                        )
                    continue
            
            # All providers failed
            return GenerationResponse(
                content="",
                model_id=model_spec,
                provider_name="gateway",
                error=f"All predictive routing providers failed. Last error: {last_error}",
                metadata={'prediction_reasoning': prediction.reasoning}
            )
            
        except Exception as e:
            logger.error(f"Error in predictive routing: {str(e)}")
            # Fallback to load balancer or original routing
            if self._load_balancer_enabled:
                return await self._route_with_load_balancer(request, model_spec, method_name, characteristics)
            else:
                return await self._route_original(request, model_spec, method_name, characteristics)
    
    async def _route_original(
        self, 
        request: GenerationRequest, 
        model_spec: str, 
        method_name: str, 
        characteristics: Dict[str, Any]
    ) -> GenerationResponse:
        """Original routing logic as fallback"""
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
    
    def get_load_balancer_stats(self) -> Optional[Dict[str, Any]]:
        """Get load balancer statistics if available"""
        if self._load_balancer_enabled and self.load_balancer:
            return self.load_balancer.get_load_balancer_stats()
        return None
    
    def get_advanced_routing_status(self) -> Dict[str, Any]:
        """Get status of advanced routing features"""
        return {
            "load_balancer_enabled": self._load_balancer_enabled,
            "load_balancer_available": ADVANCED_ROUTING_AVAILABLE,
            "predictive_routing_enabled": self._predictive_routing_enabled,
            "weight_management_enabled": self._weight_management_enabled,
            "geo_routing_enabled": self._geo_routing_enabled,
            "latency_monitoring_enabled": self._latency_monitoring_enabled,
            "intelligent_routing_enabled": True,
            "fallback_enabled": self._fallback_enabled,
            "performance_tracking": self._performance_tracking
        }
    
    def get_predictive_routing_stats(self) -> Optional[Dict[str, Any]]:
        """Get predictive routing statistics if available"""
        if self._predictive_routing_enabled and self.predictive_router:
            return self.predictive_router.get_prediction_analytics()
        return None
    
    def save_predictive_models(self, filepath: str) -> bool:
        """Save predictive models to file"""
        if self._predictive_routing_enabled and self.predictive_router:
            try:
                self.predictive_router.save_models(filepath)
                return True
            except Exception as e:
                logger.error(f"Error saving predictive models: {str(e)}")
                return False
        return False
    
    def load_predictive_models(self, filepath: str) -> bool:
        """Load predictive models from file"""
        if self._predictive_routing_enabled and self.predictive_router:
            try:
                self.predictive_router.load_models(filepath)
                return True
            except Exception as e:
                logger.error(f"Error loading predictive models: {str(e)}")
                return False
        return False
    
    def get_weight_management_stats(self) -> Optional[Dict[str, Any]]:
        """Get weight management statistics if available"""
        if self._weight_management_enabled and self.weight_manager:
            return self.weight_manager.get_weight_analytics()
        return None
    
    def get_provider_weights(self) -> Optional[Dict[str, Any]]:
        """Get current provider weights if available"""
        if self._weight_management_enabled and self.weight_manager:
            weights = self.weight_manager.get_provider_weights()
            return {name: metrics.to_dict() for name, metrics in weights.items()}
        return None
    
    def update_weight_configuration(self, new_config: Dict[str, Any]) -> bool:
        """Update weight manager configuration"""
        if self._weight_management_enabled and self.weight_manager:
            try:
                self.weight_manager.update_configuration(new_config)
                return True
            except Exception as e:
                logger.error(f"Error updating weight configuration: {str(e)}")
                return False
        return False
    
    def get_geo_routing_stats(self) -> Optional[Dict[str, Any]]:
        """Get geographic routing statistics if available"""
        if self._geo_routing_enabled and self.geo_router:
            return self.geo_router.get_geo_routing_analytics()
        return None
    
    def get_latency_monitoring_stats(self) -> Optional[Dict[str, Any]]:
        """Get latency monitoring statistics if available"""
        if self._latency_monitoring_enabled and self.latency_monitor:
            return self.latency_monitor.get_latency_analytics()
        return None
    
    def get_provider_latency_stats(self, provider_name: str) -> Optional[Dict[str, Any]]:
        """Get latency statistics for a specific provider"""
        if self._latency_monitoring_enabled and self.latency_monitor:
            stats = self.latency_monitor.get_provider_latency_stats(provider_name)
            return stats.to_dict() if stats else None
        return None
    
    async def route_with_geo_routing(self, request: GenerationRequest, 
                                   client_ip: str, 
                                   available_providers: List[str]) -> Optional[Dict[str, Any]]:
        """Route request using geographic routing"""
        if not self._geo_routing_enabled or not self.geo_router:
            return None
        
        try:
            decision = await self.geo_router.route_request(request, client_ip, available_providers)
            return decision.to_dict()
        except Exception as e:
            logger.error(f"Error in geographic routing: {str(e)}")
            return None
    
    async def shutdown(self):
        """Shutdown the gateway and cleanup resources"""
        if self._load_balancer_enabled and self.load_balancer:
            await self.load_balancer.shutdown()
        if self._weight_management_enabled and self.weight_manager:
            await self.weight_manager.stop()
        if self._latency_monitoring_enabled and self.latency_monitor:
            await self.latency_monitor.stop_monitoring()
        logger.info("Enhanced Model Bridge shutdown complete")


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