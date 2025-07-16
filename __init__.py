"""
Model Bridge - Standalone Enhanced Multi-Provider Model Bridge
"""

from .model_bridge import (
    EnhancedModelBridge,
    enhanced_gateway,
    model_bridge,
    generate_text,
    generate_structured_output,
    initialize_gateway
)

__version__ = "1.0.0"
__all__ = [
    "EnhancedModelBridge",
    "enhanced_gateway", 
    "model_bridge",
    "generate_text",
    "generate_structured_output",
    "initialize_gateway"
]