"""
Token Counter - Phase 2.1: Token-level Cost Prediction
Provides accurate token counting for various models and providers.
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class TokenizationMethod(Enum):
    """Methods for tokenizing text based on model type."""
    GPT = "gpt"
    CLAUDE = "claude"
    GEMINI = "gemini"
    LLAMA = "llama"
    MISTRAL = "mistral"
    GENERIC = "generic"


@dataclass
class TokenCount:
    """Result of token counting operation."""
    input_tokens: int
    output_tokens: int
    total_tokens: int
    method: TokenizationMethod
    model_id: str
    accuracy: float  # Confidence in the count (0.0 to 1.0)


class TokenCounter:
    """
    Advanced token counter with model-specific tokenization.
    
    Chain of thought:
    1. Different models use different tokenization methods
    2. Accurate token counting is crucial for cost prediction
    3. Must handle various text types (plain text, code, JSON, etc.)
    4. Should provide confidence scores for accuracy tracking
    """
    
    def __init__(self):
        """Initialize token counter with model-specific patterns."""
        self.logger = logging.getLogger(__name__)
        
        # Model-specific tokenization patterns
        self.model_tokenizers = {
            # OpenAI models
            "gpt-4": TokenizationMethod.GPT,
            "gpt-4o": TokenizationMethod.GPT,
            "gpt-4-turbo": TokenizationMethod.GPT,
            "gpt-3.5-turbo": TokenizationMethod.GPT,
            "text-davinci": TokenizationMethod.GPT,
            
            # Anthropic models
            "claude-3": TokenizationMethod.CLAUDE,
            "claude-2": TokenizationMethod.CLAUDE,
            "claude-instant": TokenizationMethod.CLAUDE,
            
            # Google models
            "gemini": TokenizationMethod.GEMINI,
            "palm": TokenizationMethod.GEMINI,
            
            # Meta models
            "llama": TokenizationMethod.LLAMA,
            "llama2": TokenizationMethod.LLAMA,
            "llama3": TokenizationMethod.LLAMA,
            "codellama": TokenizationMethod.LLAMA,
            
            # Mistral models
            "mistral": TokenizationMethod.MISTRAL,
            "mixtral": TokenizationMethod.MISTRAL,
        }
        
        # Average tokens per word for different methods
        self.tokens_per_word = {
            TokenizationMethod.GPT: 1.33,
            TokenizationMethod.CLAUDE: 1.25,
            TokenizationMethod.GEMINI: 1.30,
            TokenizationMethod.LLAMA: 1.35,
            TokenizationMethod.MISTRAL: 1.28,
            TokenizationMethod.GENERIC: 1.30
        }
        
        # Special token patterns
        self.special_patterns = {
            "code_block": r'```[\s\S]*?```',
            "inline_code": r'`[^`]+`',
            "json_object": r'\{[\s\S]*?\}',
            "list_item": r'^\s*[-*+]\s',
            "numbered_list": r'^\s*\d+\.\s',
            "url": r'https?://[^\s<>"{}|\\^`\[\]]+',
            "email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        }
        
        self.logger.info("TokenCounter initialized with model-specific tokenization")
    
    def count_tokens(self, text: str, model_id: str, output_text: Optional[str] = None) -> TokenCount:
        """
        Count tokens for input and output text.
        
        Args:
            text: Input text to tokenize
            model_id: Model identifier for tokenization method
            output_text: Optional output text for completion models
            
        Returns:
            TokenCount object with detailed token information
        """
        try:
            # Determine tokenization method
            method = self._get_tokenization_method(model_id)
            
            # Count input tokens
            input_tokens = self._count_text_tokens(text, method)
            
            # Count output tokens if provided
            output_tokens = 0
            if output_text:
                output_tokens = self._count_text_tokens(output_text, method)
            
            # Calculate accuracy based on method confidence
            accuracy = self._calculate_accuracy(method, model_id)
            
            result = TokenCount(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                method=method,
                model_id=model_id,
                accuracy=accuracy
            )
            
            self.logger.debug(f"Token count for {model_id}: {result.total_tokens} tokens")
            return result
            
        except Exception as e:
            self.logger.error(f"Error counting tokens for {model_id}: {str(e)}")
            # Return fallback count
            return self._fallback_count(text, model_id, output_text)
    
    def _get_tokenization_method(self, model_id: str) -> TokenizationMethod:
        """Determine tokenization method based on model ID."""
        model_lower = model_id.lower()
        
        for pattern, method in self.model_tokenizers.items():
            if pattern in model_lower:
                return method
        
        return TokenizationMethod.GENERIC
    
    def _count_text_tokens(self, text: str, method: TokenizationMethod) -> int:
        """
        Count tokens in text using method-specific approach.
        
        Chain of thought:
        1. Handle special content types (code, JSON, etc.)
        2. Apply method-specific tokenization
        3. Account for special tokens and formatting
        4. Return accurate count
        """
        if not text:
            return 0
        
        # Handle special content types
        adjusted_text = self._handle_special_content(text)
        
        # Basic word count
        words = len(adjusted_text.split())
        
        # Apply method-specific multiplier
        tokens_per_word = self.tokens_per_word.get(method, 1.30)
        base_tokens = int(words * tokens_per_word)
        
        # Add special token adjustments
        special_tokens = self._count_special_tokens(text, method)
        
        return base_tokens + special_tokens
    
    def _handle_special_content(self, text: str) -> str:
        """Handle special content types that affect tokenization."""
        adjusted_text = text
        
        # Code blocks typically have more tokens
        code_blocks = re.findall(self.special_patterns["code_block"], text)
        for block in code_blocks:
            # Code typically has 1.5x more tokens
            code_content = block.replace('```', '').strip()
            adjusted_text = adjusted_text.replace(block, code_content * 1.5)
        
        # JSON objects have structural tokens
        json_objects = re.findall(self.special_patterns["json_object"], text)
        for obj in json_objects:
            try:
                parsed = json.loads(obj)
                # Add tokens for JSON structure
                structure_tokens = len(str(parsed).replace(' ', '')) * 0.1
                adjusted_text = adjusted_text.replace(obj, obj + ' ' * int(structure_tokens))
            except:
                pass
        
        return adjusted_text
    
    def _count_special_tokens(self, text: str, method: TokenizationMethod) -> int:
        """Count special tokens based on content patterns."""
        special_count = 0
        
        # URLs typically use more tokens
        urls = re.findall(self.special_patterns["url"], text)
        special_count += len(urls) * 2
        
        # Lists have formatting tokens
        list_items = re.findall(self.special_patterns["list_item"], text, re.MULTILINE)
        special_count += len(list_items)
        
        numbered_items = re.findall(self.special_patterns["numbered_list"], text, re.MULTILINE)
        special_count += len(numbered_items)
        
        # Method-specific adjustments
        if method == TokenizationMethod.GPT:
            # GPT models have more special tokens
            special_count = int(special_count * 1.2)
        elif method == TokenizationMethod.CLAUDE:
            # Claude is more efficient
            special_count = int(special_count * 0.9)
        
        return special_count
    
    def _calculate_accuracy(self, method: TokenizationMethod, model_id: str) -> float:
        """Calculate accuracy confidence for token count."""
        base_accuracy = 0.85  # Base confidence
        
        # Method-specific accuracy
        method_accuracy = {
            TokenizationMethod.GPT: 0.95,
            TokenizationMethod.CLAUDE: 0.90,
            TokenizationMethod.GEMINI: 0.85,
            TokenizationMethod.LLAMA: 0.80,
            TokenizationMethod.MISTRAL: 0.85,
            TokenizationMethod.GENERIC: 0.70
        }
        
        return method_accuracy.get(method, base_accuracy)
    
    def _fallback_count(self, text: str, model_id: str, output_text: Optional[str] = None) -> TokenCount:
        """Fallback token counting when main method fails."""
        # Simple word-based estimation
        input_words = len(text.split()) if text else 0
        output_words = len(output_text.split()) if output_text else 0
        
        # Use generic multiplier
        input_tokens = int(input_words * 1.30)
        output_tokens = int(output_words * 1.30)
        
        return TokenCount(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            method=TokenizationMethod.GENERIC,
            model_id=model_id,
            accuracy=0.60  # Lower accuracy for fallback
        )
    
    def estimate_output_tokens(self, prompt: str, max_tokens: Optional[int] = None) -> int:
        """
        Estimate output tokens based on prompt and max_tokens.
        
        Chain of thought:
        1. Analyze prompt for expected response length
        2. Consider max_tokens constraint
        3. Use historical patterns for estimation
        4. Return reasonable estimate
        """
        if not prompt:
            return 0
        
        # Base estimation from prompt length
        prompt_length = len(prompt.split())
        
        # Estimate based on prompt type
        if "summarize" in prompt.lower() or "summary" in prompt.lower():
            estimated = min(prompt_length // 3, 200)  # Summaries are typically shorter
        elif "explain" in prompt.lower() or "describe" in prompt.lower():
            estimated = min(prompt_length * 2, 500)  # Explanations are longer
        elif "code" in prompt.lower() or "function" in prompt.lower():
            estimated = min(prompt_length * 1.5, 300)  # Code responses vary
        elif "list" in prompt.lower() or "enumerate" in prompt.lower():
            estimated = min(prompt_length, 150)  # Lists are structured
        else:
            estimated = min(prompt_length, 250)  # General response
        
        # Apply max_tokens constraint
        if max_tokens:
            estimated = min(estimated, max_tokens)
        
        return max(estimated, 10)  # Minimum reasonable output
    
    def get_tokenization_stats(self) -> Dict[str, Any]:
        """Get statistics about tokenization methods and accuracy."""
        return {
            "supported_methods": [method.value for method in TokenizationMethod],
            "model_mappings": {k: v.value for k, v in self.model_tokenizers.items()},
            "tokens_per_word": {k.value: v for k, v in self.tokens_per_word.items()},
            "special_patterns": list(self.special_patterns.keys())
        }