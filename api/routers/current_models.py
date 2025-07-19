"""
Current Models Documentation Endpoint
Provides up-to-date model information for API documentation
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/current-models/documentation")
async def get_current_models_documentation():
    """
    Get comprehensive documentation of all current models (2025)
    
    This endpoint provides detailed information about all available models
    including the latest Claude 4, GPT-4.1, o-series, and Gemini 2.0 models.
    """
    return {
        "last_updated": "2025-01-19",
        "version": "2025.1",
        "total_models": 120,
        "total_providers": 15,
        
        "featured_models": {
            "reasoning": [
                {
                    "model_id": "o3",
                    "provider": "openai", 
                    "name": "OpenAI o3",
                    "description": "Advanced reasoning model for complex problem solving",
                    "context_length": 128000,
                    "cost_per_1k_tokens": 0.06,
                    "best_for": "Mathematics, coding, complex reasoning tasks",
                    "release_date": "2025-01"
                },
                {
                    "model_id": "claude-4-opus",
                    "provider": "anthropic",
                    "name": "Claude 4 Opus", 
                    "description": "Flagship model with exceptional reasoning capabilities",
                    "context_length": 500000,
                    "cost_per_1k_tokens": 0.008,
                    "best_for": "Complex analysis, research, creative writing",
                    "release_date": "2025-01"
                }
            ],
            "fast": [
                {
                    "model_id": "gpt-4.1-nano",
                    "provider": "openai",
                    "name": "GPT-4.1 Nano",
                    "description": "Ultra-fast model for high-throughput applications", 
                    "context_length": 64000,
                    "cost_per_1k_tokens": 0.00005,
                    "best_for": "Real-time chat, simple tasks, high volume",
                    "release_date": "2025-01"
                },
                {
                    "model_id": "claude-4-haiku",
                    "provider": "anthropic",
                    "name": "Claude 4 Haiku",
                    "description": "Fast and efficient model with vision capabilities",
                    "context_length": 200000,
                    "cost_per_1k_tokens": 0.0003,
                    "best_for": "Quick responses, image analysis, customer support",
                    "release_date": "2025-01"
                }
            ],
            "multimodal": [
                {
                    "model_id": "gemini-2.0-pro-exp",
                    "provider": "google",
                    "name": "Gemini 2.0 Pro Experimental",
                    "description": "Advanced multimodal model with reasoning capabilities",
                    "context_length": 2000000,
                    "cost_per_1k_tokens": 0.004,
                    "best_for": "Complex multimodal tasks, document analysis",
                    "release_date": "2025-01"
                },
                {
                    "model_id": "gpt-4.1",
                    "provider": "openai", 
                    "name": "GPT-4.1",
                    "description": "Enhanced model with vision and function calling",
                    "context_length": 200000,
                    "cost_per_1k_tokens": 0.012,
                    "best_for": "General purpose, vision tasks, function calling",
                    "release_date": "2025-01"
                }
            ]
        },
        
        "providers": {
            "openai": {
                "latest_models": ["gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "o3", "o4-mini"],
                "capabilities": ["text", "vision", "function_calling", "json_mode", "advanced_reasoning"],
                "max_context": 200000,
                "pricing_range": "$0.00005 - $0.06 per 1K tokens"
            },
            "anthropic": {
                "latest_models": ["claude-4-opus", "claude-4-sonnet", "claude-4-haiku"],
                "capabilities": ["text", "vision", "code", "analysis", "tool_use"],
                "max_context": 500000,
                "pricing_range": "$0.0003 - $0.008 per 1K tokens"
            },
            "google": {
                "latest_models": ["gemini-2.0-pro-exp", "gemini-2.0-flash-exp", "gemini-2.0-flash-lite"],
                "capabilities": ["text", "vision", "multimodal", "reasoning", "function_calling"],
                "max_context": 2000000,
                "pricing_range": "$0.0005 - $0.004 per 1K tokens"
            }
        },
        
        "migration_guide": {
            "from_gpt4": {
                "recommended": "gpt-4.1",
                "reasoning": "Enhanced capabilities with better reasoning and extended context",
                "breaking_changes": "None - fully compatible API"
            },
            "from_claude3": {
                "recommended": "claude-4-sonnet", 
                "reasoning": "Significant improvements in reasoning and multimodal capabilities",
                "breaking_changes": "None - same API structure"
            },
            "from_gemini1_5": {
                "recommended": "gemini-2.0-flash-exp",
                "reasoning": "Better performance and new experimental features",
                "breaking_changes": "None - backward compatible"
            }
        },
        
        "compatibility": {
            "openai_api": "Full compatibility with OpenAI API format",
            "anthropic_api": "Full compatibility with Anthropic API format", 
            "google_api": "Full compatibility with Google AI API format",
            "unified_api": "Model Bridge provides unified API across all providers"
        },
        
        "example_requests": {
            "basic_completion": {
                "url": "/api/v1/completions",
                "method": "POST",
                "body": {
                    "model": "gpt-4.1",
                    "prompt": "Explain quantum computing",
                    "max_tokens": 1000,
                    "temperature": 0.7
                }
            },
            "vision_task": {
                "url": "/api/v1/completions", 
                "method": "POST",
                "body": {
                    "model": "claude-4-sonnet",
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "What's in this image?"},
                                {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
                            ]
                        }
                    ]
                }
            },
            "function_calling": {
                "url": "/api/v1/completions",
                "method": "POST", 
                "body": {
                    "model": "gpt-4.1",
                    "messages": [{"role": "user", "content": "What's the weather like?"}],
                    "functions": [
                        {
                            "name": "get_weather",
                            "description": "Get current weather",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "location": {"type": "string"}
                                }
                            }
                        }
                    ]
                }
            }
        },
        
        "changelog": {
            "2025-01-19": [
                "Added Claude 4 series (Opus, Sonnet, Haiku)",
                "Added GPT-4.1 series and nano variant",
                "Added o3 and o4-mini reasoning models",
                "Added Gemini 2.0 series",
                "Implemented dynamic model discovery",
                "Enhanced multimodal capabilities"
            ],
            "2024-12": [
                "Updated knowledge cutoffs to 2024-12 for latest models",
                "Improved pricing accuracy",
                "Enhanced capability detection"
            ]
        }
    }

@router.get("/current-models/pricing")
async def get_current_pricing():
    """Get current pricing information for all models"""
    return {
        "last_updated": "2025-01-19",
        "currency": "USD",
        "pricing_per_1k_tokens": {
            "ultra_premium": {
                "models": ["o3"],
                "range": "$0.06",
                "use_case": "Complex reasoning, research"
            },
            "premium": {
                "models": ["gpt-4.1", "claude-4-opus"],
                "range": "$0.008 - $0.012", 
                "use_case": "High-quality general purpose"
            },
            "balanced": {
                "models": ["claude-4-sonnet", "gemini-2.0-pro-exp", "o4-mini"],
                "range": "$0.0025 - $0.004",
                "use_case": "Production applications"
            },
            "efficient": {
                "models": ["claude-4-haiku", "gemini-2.0-flash-exp"],
                "range": "$0.0003 - $0.002",
                "use_case": "High-volume, fast responses"
            },
            "ultra_efficient": {
                "models": ["gpt-4.1-mini", "gpt-4.1-nano"],
                "range": "$0.00005 - $0.0001",
                "use_case": "Real-time, high-throughput"
            }
        },
        "cost_optimization": {
            "auto_routing": "Automatically route to most cost-effective model",
            "bulk_discounts": "Volume discounts available for enterprise",
            "free_tier": "1,000 requests/month on select models"
        }
    }

@router.get("/current-models/capabilities")
async def get_model_capabilities():
    """Get detailed capability matrix for all current models"""
    return {
        "capability_matrix": {
            "text_generation": {
                "models": ["all"],
                "quality": "Excellent across all providers"
            },
            "vision": {
                "models": ["gpt-4.1", "claude-4-*", "gemini-2.0-*"],
                "features": ["image_analysis", "document_reading", "chart_interpretation"]
            },
            "function_calling": {
                "models": ["gpt-4.1", "claude-4-*", "gemini-2.0-*"],
                "features": ["tool_use", "api_integration", "structured_output"]
            },
            "reasoning": {
                "advanced": ["o3", "claude-4-opus"],
                "good": ["o4-mini", "gpt-4.1", "claude-4-sonnet"],
                "basic": ["gpt-4.1-mini", "claude-4-haiku"]
            },
            "coding": {
                "excellent": ["o3", "claude-4-opus", "gpt-4.1"],
                "good": ["o4-mini", "claude-4-sonnet"],
                "basic": ["gpt-4.1-mini", "claude-4-haiku"]
            },
            "multimodal": {
                "advanced": ["gemini-2.0-pro-exp", "claude-4-opus"],
                "good": ["gemini-2.0-flash-exp", "claude-4-sonnet", "gpt-4.1"],
                "basic": ["claude-4-haiku", "gpt-4.1-mini"]
            }
        },
        "context_lengths": {
            "ultra_large": {
                "range": "2M tokens",
                "models": ["gemini-2.0-*"]
            },
            "large": {
                "range": "400-500K tokens", 
                "models": ["claude-4-opus", "claude-4-sonnet"]
            },
            "medium": {
                "range": "128-200K tokens",
                "models": ["gpt-4.1", "o3", "o4-mini", "claude-4-haiku"]
            },
            "small": {
                "range": "64K tokens",
                "models": ["gpt-4.1-nano"]
            }
        }
    }