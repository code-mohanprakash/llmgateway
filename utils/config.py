"""
Configuration management for Model Bridge - Standalone Version
"""
import os
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class DynamicProviderConfig(BaseModel):
    """Dynamic provider configuration based on available API keys"""
    enabled: bool = False
    api_key: str = ""
    priority: int = 999  # Lower number = higher priority
    
    @classmethod
    def from_env(cls, provider_name: str) -> 'DynamicProviderConfig':
        """Create provider config from environment variables"""
        env_prefix = provider_name.upper()
        api_key = os.getenv(f"{env_prefix}_API_KEY", "")
        
        return cls(
            enabled=bool(api_key),
            api_key=api_key,
            priority=int(os.getenv(f"{env_prefix}_PRIORITY", "999"))
        )


class Config(BaseModel):
    """Application configuration for standalone Model Bridge"""
    
    # Dynamic Provider Configuration
    providers: Dict[str, DynamicProviderConfig] = Field(default_factory=lambda: {
        "openai": DynamicProviderConfig.from_env("openai"),
        "anthropic": DynamicProviderConfig.from_env("anthropic"),
        "google": DynamicProviderConfig.from_env("google"),
        "groq": DynamicProviderConfig.from_env("groq"),
        "together": DynamicProviderConfig.from_env("together"),
        "mistral": DynamicProviderConfig.from_env("mistral"),
        "cohere": DynamicProviderConfig.from_env("cohere"),
        "perplexity": DynamicProviderConfig.from_env("perplexity"),
        "huggingface": DynamicProviderConfig.from_env("huggingface"),
        "deepseek": DynamicProviderConfig.from_env("deepseek"),
        "ollama": DynamicProviderConfig.from_env("ollama"),
        "openrouter": DynamicProviderConfig.from_env("openrouter"),
        "mock": DynamicProviderConfig.from_env("mock"),
    })
    
    # Available providers (only those with valid API keys)
    @property
    def available_providers(self) -> List[str]:
        """Get list of providers with valid API keys"""
        return [name for name, config in self.providers.items() if config.enabled]
    
    @property
    def primary_provider(self) -> Optional[str]:
        """Get the primary provider (lowest priority number)"""
        enabled_providers = [(name, config) for name, config in self.providers.items() if config.enabled]
        if not enabled_providers:
            return None
        return min(enabled_providers, key=lambda x: x[1].priority)[0]
    
    # LLM Configuration
    model_name: str = "gpt-4"
    temperature: float = 0.1
    max_tokens: int = 4000
    
    # Logging Configuration
    log_level: str = Field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    
    # Model Routing Configuration: Maps a logical task to a model alias from models_config.yaml
    model_routing: dict = Field(default_factory=lambda: {
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
    })


# Global configuration instance
config = Config()