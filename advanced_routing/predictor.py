"""
ML-based Predictive Routing System
Implements request pattern analysis and provider performance prediction
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict
import json
import hashlib

from providers.base import BaseModelProvider, GenerationRequest
from utils.ml_utils import PerformancePredictor, ModelPrediction

logger = logging.getLogger(__name__)


@dataclass
class RequestPattern:
    """Represents a pattern in request characteristics"""
    pattern_id: str
    avg_request_length: float
    common_task_types: List[str]
    avg_complexity: float
    frequency: int
    success_rate: float
    avg_response_time: float
    preferred_providers: List[str]
    confidence_score: float


@dataclass
class RoutingPrediction:
    """Complete routing prediction with confidence and alternatives"""
    primary_provider: str
    primary_confidence: float
    predicted_response_time: float
    predicted_success_rate: float
    alternative_providers: List[Dict[str, Any]]
    reasoning: str
    pattern_match: Optional[str] = None


class PatternAnalyzer:
    """
    Analyzes request patterns to identify common usage patterns
    and optimize routing decisions
    """
    
    def __init__(self, pattern_window_size: int = 1000):
        self.pattern_window_size = pattern_window_size
        self.request_history: List[Dict[str, Any]] = []
        self.identified_patterns: Dict[str, RequestPattern] = {}
        self.pattern_cache: Dict[str, str] = {}  # request_hash -> pattern_id
        self.last_analysis_time = datetime.utcnow()
        self.analysis_interval = timedelta(minutes=15)
    
    def add_request(self, request: GenerationRequest, provider_used: str, 
                   response_time: float, success: bool):
        """Add a request to the pattern analysis"""
        request_data = {
            'prompt': request.prompt,
            'prompt_length': len(request.prompt),
            'system_message': request.system_message,
            'temperature': request.temperature,
            'max_tokens': request.max_tokens,
            'task_type': getattr(request, 'task_type', None),
            'complexity': getattr(request, 'complexity', None),
            'provider_used': provider_used,
            'response_time': response_time,
            'success': success,
            'timestamp': datetime.utcnow()
        }
        
        self.request_history.append(request_data)
        
        # Keep only recent history
        if len(self.request_history) > self.pattern_window_size:
            self.request_history.pop(0)
        
        # Periodic pattern analysis
        if datetime.utcnow() - self.last_analysis_time > self.analysis_interval:
            self._analyze_patterns()
    
    def _analyze_patterns(self):
        """Analyze request history to identify patterns"""
        try:
            if len(self.request_history) < 50:  # Need minimum data
                return
            
            logger.info("Analyzing request patterns...")
            
            # Group requests by characteristics
            pattern_groups = defaultdict(list)
            
            for request in self.request_history:
                # Create pattern key based on request characteristics
                pattern_key = self._create_pattern_key(request)
                pattern_groups[pattern_key].append(request)
            
            # Identify significant patterns (with enough requests)
            self.identified_patterns = {}
            
            for pattern_key, requests in pattern_groups.items():
                if len(requests) >= 10:  # Minimum requests for a pattern
                    pattern = self._create_pattern_from_requests(pattern_key, requests)
                    self.identified_patterns[pattern_key] = pattern
            
            # Update pattern cache
            self._update_pattern_cache()
            
            self.last_analysis_time = datetime.utcnow()
            logger.info(f"Identified {len(self.identified_patterns)} request patterns")
            
        except Exception as e:
            logger.error(f"Error analyzing patterns: {str(e)}")
    
    def _create_pattern_key(self, request: Dict[str, Any]) -> str:
        """Create a pattern key from request characteristics"""
        # Discretize continuous values
        length_bucket = min(int(request['prompt_length'] / 500), 10)  # 500-char buckets
        
        task_type = request.get('task_type', 'unknown')
        complexity = request.get('complexity', 'medium')
        
        # Create pattern key
        key_parts = [
            f"length_{length_bucket}",
            f"task_{task_type}",
            f"complexity_{complexity}"
        ]
        
        # Add system message presence
        if request.get('system_message'):
            key_parts.append("has_system")
        
        # Add temperature range
        temp = request.get('temperature', 0.7)
        if temp is not None:
            temp_bucket = 'low' if temp < 0.3 else 'high' if temp > 0.7 else 'medium'
            key_parts.append(f"temp_{temp_bucket}")
        
        return "_".join(key_parts)
    
    def _create_pattern_from_requests(self, pattern_key: str, requests: List[Dict[str, Any]]) -> RequestPattern:
        """Create a RequestPattern from a group of similar requests"""
        # Calculate statistics
        avg_length = sum(r['prompt_length'] for r in requests) / len(requests)
        
        task_types = [r.get('task_type') for r in requests if r.get('task_type')]
        common_task_types = list(set(task_types))
        
        # Estimate complexity
        complexity_scores = []
        for r in requests:
            complexity = r.get('complexity', 'medium')
            if complexity == 'simple':
                complexity_scores.append(1)
            elif complexity == 'complex':
                complexity_scores.append(3)
            else:
                complexity_scores.append(2)
        
        avg_complexity = sum(complexity_scores) / len(complexity_scores) if complexity_scores else 2.0
        
        # Performance metrics
        success_rate = sum(r['success'] for r in requests) / len(requests)
        avg_response_time = sum(r['response_time'] for r in requests) / len(requests)
        
        # Provider preferences
        provider_counts = defaultdict(int)
        provider_performance = defaultdict(list)
        
        for r in requests:
            provider = r['provider_used']
            provider_counts[provider] += 1
            provider_performance[provider].append(r['response_time'])
        
        # Rank providers by performance
        provider_rankings = []
        for provider, response_times in provider_performance.items():
            avg_rt = sum(response_times) / len(response_times)
            provider_rankings.append((provider, avg_rt, provider_counts[provider]))
        
        # Sort by response time (ascending) and frequency (descending)
        provider_rankings.sort(key=lambda x: (x[1], -x[2]))
        preferred_providers = [p[0] for p in provider_rankings]
        
        # Calculate confidence based on data amount and consistency
        confidence_score = min(len(requests) / 100.0, 1.0)  # More data = higher confidence
        
        return RequestPattern(
            pattern_id=pattern_key,
            avg_request_length=avg_length,
            common_task_types=common_task_types,
            avg_complexity=avg_complexity,
            frequency=len(requests),
            success_rate=success_rate,
            avg_response_time=avg_response_time,
            preferred_providers=preferred_providers,
            confidence_score=confidence_score
        )
    
    def _update_pattern_cache(self):
        """Update cache mapping request hashes to pattern IDs"""
        self.pattern_cache = {}
        
        for request in self.request_history[-200:]:  # Cache recent requests
            request_hash = self._hash_request(request)
            pattern_key = self._create_pattern_key(request)
            if pattern_key in self.identified_patterns:
                self.pattern_cache[request_hash] = pattern_key
    
    def _hash_request(self, request: Dict[str, Any]) -> str:
        """Create a hash for a request"""
        # Use key characteristics for hashing
        hash_data = {
            'prompt_length': request['prompt_length'],
            'task_type': request.get('task_type'),
            'complexity': request.get('complexity'),
            'has_system': bool(request.get('system_message')),
            'temperature': request.get('temperature')
        }
        
        hash_str = json.dumps(hash_data, sort_keys=True)
        return hashlib.md5(hash_str.encode()).hexdigest()
    
    def find_matching_pattern(self, request: GenerationRequest) -> Optional[RequestPattern]:
        """Find the best matching pattern for a request"""
        request_data = {
            'prompt': request.prompt,
            'prompt_length': len(request.prompt),
            'system_message': request.system_message,
            'temperature': request.temperature,
            'task_type': getattr(request, 'task_type', None),
            'complexity': getattr(request, 'complexity', None)
        }
        
        # Try cache first
        request_hash = self._hash_request(request_data)
        if request_hash in self.pattern_cache:
            pattern_id = self.pattern_cache[request_hash]
            return self.identified_patterns.get(pattern_id)
        
        # Find best matching pattern
        pattern_key = self._create_pattern_key(request_data)
        return self.identified_patterns.get(pattern_key)
    
    def get_patterns_summary(self) -> Dict[str, Any]:
        """Get summary of identified patterns"""
        patterns_summary = []
        
        for pattern_id, pattern in self.identified_patterns.items():
            patterns_summary.append({
                'pattern_id': pattern_id,
                'frequency': pattern.frequency,
                'success_rate': pattern.success_rate,
                'avg_response_time': pattern.avg_response_time,
                'preferred_providers': pattern.preferred_providers[:3],  # Top 3
                'confidence_score': pattern.confidence_score
            })
        
        # Sort by frequency
        patterns_summary.sort(key=lambda x: x['frequency'], reverse=True)
        
        return {
            'total_patterns': len(self.identified_patterns),
            'total_requests_analyzed': len(self.request_history),
            'patterns': patterns_summary[:10],  # Top 10 patterns
            'last_analysis': self.last_analysis_time.isoformat()
        }


class PredictiveRouter:
    """
    Advanced predictive routing system that combines ML predictions
    with pattern analysis for optimal provider selection
    """
    
    def __init__(self):
        self.performance_predictor = PerformancePredictor()
        self.pattern_analyzer = PatternAnalyzer()
        self.providers: Dict[str, BaseModelProvider] = {}
        self.prediction_cache: Dict[str, Tuple[RoutingPrediction, datetime]] = {}
        self.cache_ttl = timedelta(minutes=5)
        self.confidence_threshold = 0.6
    
    def register_provider(self, name: str, provider: BaseModelProvider):
        """Register a provider with the predictive router"""
        self.providers[name] = provider
        logger.info(f"Registered provider {name} with predictive router")
    
    def add_training_data(self, provider_name: str, request: GenerationRequest, 
                         response_time: float, success: bool):
        """Add training data to both predictor and pattern analyzer"""
        request_data = {
            'prompt': request.prompt,
            'system_message': request.system_message,
            'temperature': request.temperature,
            'max_tokens': request.max_tokens,
            'task_type': getattr(request, 'task_type', None),
            'complexity': getattr(request, 'complexity', None)
        }
        
        # Train performance predictor
        self.performance_predictor.add_training_data(
            provider_name, request_data, response_time, success
        )
        
        # Update pattern analyzer
        self.pattern_analyzer.add_request(request, provider_name, response_time, success)
    
    async def predict_optimal_routing(self, request: GenerationRequest, 
                                    available_providers: List[str]) -> RoutingPrediction:
        """Predict optimal routing for a request"""
        # Check cache first
        cache_key = self._create_cache_key(request, available_providers)
        if cache_key in self.prediction_cache:
            prediction, timestamp = self.prediction_cache[cache_key]
            if datetime.utcnow() - timestamp < self.cache_ttl:
                return prediction
        
        # Find matching pattern
        matching_pattern = self.pattern_analyzer.find_matching_pattern(request)
        
        # Get predictions for all available providers
        provider_predictions = {}
        
        request_data = {
            'prompt': request.prompt,
            'system_message': request.system_message,
            'temperature': request.temperature,
            'max_tokens': request.max_tokens,
            'task_type': getattr(request, 'task_type', None),
            'complexity': getattr(request, 'complexity', None)
        }
        
        for provider_name in available_providers:
            try:
                prediction = self.performance_predictor.predict_performance(
                    provider_name, request_data
                )
                provider_predictions[provider_name] = prediction
            except Exception as e:
                logger.warning(f"Error predicting for provider {provider_name}: {str(e)}")
                # Fallback prediction
                provider_predictions[provider_name] = ModelPrediction(
                    predicted_response_time=2.0,
                    predicted_success_rate=0.9,
                    confidence_score=0.3,
                    feature_importance={}
                )
        
        # Select optimal provider
        routing_prediction = self._select_optimal_provider(
            provider_predictions, matching_pattern, request
        )
        
        # Cache prediction
        self.prediction_cache[cache_key] = (routing_prediction, datetime.utcnow())
        
        # Clean old cache entries
        self._clean_cache()
        
        return routing_prediction
    
    def _create_cache_key(self, request: GenerationRequest, available_providers: List[str]) -> str:
        """Create cache key for a request"""
        key_data = {
            'prompt_hash': hashlib.md5(request.prompt.encode()).hexdigest(),
            'system_message': bool(request.system_message),
            'temperature': request.temperature,
            'max_tokens': request.max_tokens,
            'task_type': getattr(request, 'task_type', None),
            'complexity': getattr(request, 'complexity', None),
            'providers': sorted(available_providers)
        }
        
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _select_optimal_provider(self, provider_predictions: Dict[str, ModelPrediction], 
                               matching_pattern: Optional[RequestPattern], 
                               request: GenerationRequest) -> RoutingPrediction:
        """Select optimal provider based on predictions and patterns"""
        
        # Calculate composite scores for each provider
        provider_scores = {}
        
        for provider_name, prediction in provider_predictions.items():
            # Base score from ML prediction
            # Normalize response time (lower is better)
            response_time_score = max(0, 1.0 - prediction.predicted_response_time / 10.0)
            success_rate_score = prediction.predicted_success_rate
            confidence_score = prediction.confidence_score
            
            # Weighted composite score
            ml_score = (
                response_time_score * 0.4 +
                success_rate_score * 0.4 +
                confidence_score * 0.2
            )
            
            # Pattern-based boost
            pattern_boost = 0.0
            if matching_pattern:
                if provider_name in matching_pattern.preferred_providers:
                    # Boost based on position in preferred providers
                    position = matching_pattern.preferred_providers.index(provider_name)
                    pattern_boost = (len(matching_pattern.preferred_providers) - position) / len(matching_pattern.preferred_providers)
                    pattern_boost *= matching_pattern.confidence_score * 0.3
            
            # Final score
            final_score = ml_score + pattern_boost
            provider_scores[provider_name] = {
                'score': final_score,
                'ml_score': ml_score,
                'pattern_boost': pattern_boost,
                'prediction': prediction
            }
        
        # Sort providers by score
        sorted_providers = sorted(provider_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        
        # Primary provider
        primary_provider = sorted_providers[0][0]
        primary_data = sorted_providers[0][1]
        
        # Alternative providers
        alternatives = []
        for provider_name, data in sorted_providers[1:4]:  # Top 3 alternatives
            alternatives.append({
                'provider': provider_name,
                'score': data['score'],
                'predicted_response_time': data['prediction'].predicted_response_time,
                'predicted_success_rate': data['prediction'].predicted_success_rate,
                'confidence': data['prediction'].confidence_score
            })
        
        # Generate reasoning
        reasoning = self._generate_reasoning(primary_provider, primary_data, matching_pattern)
        
        return RoutingPrediction(
            primary_provider=primary_provider,
            primary_confidence=primary_data['prediction'].confidence_score,
            predicted_response_time=primary_data['prediction'].predicted_response_time,
            predicted_success_rate=primary_data['prediction'].predicted_success_rate,
            alternative_providers=alternatives,
            reasoning=reasoning,
            pattern_match=matching_pattern.pattern_id if matching_pattern else None
        )
    
    def _generate_reasoning(self, primary_provider: str, primary_data: Dict[str, Any], 
                          matching_pattern: Optional[RequestPattern]) -> str:
        """Generate human-readable reasoning for the routing decision"""
        reasoning_parts = []
        
        # ML-based reasoning
        prediction = primary_data['prediction']
        reasoning_parts.append(
            f"ML prediction: {prediction.predicted_response_time:.2f}s response time, "
            f"{prediction.predicted_success_rate:.1%} success rate"
        )
        
        # Pattern-based reasoning
        if matching_pattern and primary_data['pattern_boost'] > 0:
            reasoning_parts.append(
                f"Pattern match: Similar requests performed well with {primary_provider} "
                f"(pattern confidence: {matching_pattern.confidence_score:.1%})"
            )
        
        # Feature importance
        if prediction.feature_importance:
            top_features = sorted(prediction.feature_importance.items(), 
                                key=lambda x: x[1], reverse=True)[:2]
            if top_features:
                feature_names = [f.replace('_', ' ') for f, _ in top_features]
                reasoning_parts.append(f"Key factors: {', '.join(feature_names)}")
        
        return ". ".join(reasoning_parts)
    
    def _clean_cache(self):
        """Clean expired cache entries"""
        current_time = datetime.utcnow()
        expired_keys = [
            key for key, (_, timestamp) in self.prediction_cache.items()
            if current_time - timestamp >= self.cache_ttl
        ]
        
        for key in expired_keys:
            del self.prediction_cache[key]
    
    def get_prediction_analytics(self) -> Dict[str, Any]:
        """Get analytics about predictions and patterns"""
        model_stats = self.performance_predictor.get_model_stats()
        patterns_summary = self.pattern_analyzer.get_patterns_summary()
        
        return {
            'model_stats': model_stats,
            'patterns_summary': patterns_summary,
            'cache_stats': {
                'cached_predictions': len(self.prediction_cache),
                'cache_ttl_minutes': self.cache_ttl.total_seconds() / 60
            },
            'confidence_threshold': self.confidence_threshold
        }
    
    def save_models(self, filepath: str):
        """Save trained models to file"""
        self.performance_predictor.save_models(filepath)
    
    def load_models(self, filepath: str):
        """Load trained models from file"""
        self.performance_predictor.load_models(filepath)


# Global predictive router instance
predictive_router = PredictiveRouter()