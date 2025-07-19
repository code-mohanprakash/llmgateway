"""
ML Utilities for Predictive Routing
Provides lightweight ML capabilities for provider performance prediction
"""

import numpy as np
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict
import math

logger = logging.getLogger(__name__)


@dataclass
class PredictionFeatures:
    """Features used for ML prediction"""
    request_length: float
    request_complexity: float
    task_type_encoded: float
    time_of_day: float
    day_of_week: float
    historical_avg_response_time: float
    historical_success_rate: float
    recent_error_rate: float
    provider_load: float
    request_similarity: float


@dataclass
class ModelPrediction:
    """Prediction result from ML model"""
    predicted_response_time: float
    predicted_success_rate: float
    confidence_score: float
    feature_importance: Dict[str, float]


class SimpleLinearRegression:
    """
    Lightweight linear regression implementation
    Avoids heavy dependencies like scikit-learn
    """
    
    def __init__(self):
        self.weights = None
        self.bias = None
        self.is_trained = False
        self.feature_means = None
        self.feature_stds = None
    
    def _normalize_features(self, X: np.ndarray) -> np.ndarray:
        """Normalize features using z-score normalization"""
        if self.feature_means is None:
            self.feature_means = np.mean(X, axis=0)
            self.feature_stds = np.std(X, axis=0)
            # Avoid division by zero
            self.feature_stds[self.feature_stds == 0] = 1.0
        
        return (X - self.feature_means) / self.feature_stds
    
    def train(self, X: np.ndarray, y: np.ndarray, learning_rate: float = 0.01, epochs: int = 1000):
        """Train the linear regression model"""
        if len(X) == 0:
            logger.warning("No training data provided")
            return
        
        # Normalize features
        X_norm = self._normalize_features(X)
        
        # Initialize weights and bias
        n_features = X_norm.shape[1]
        self.weights = np.random.normal(0, 0.01, n_features)
        self.bias = 0.0
        
        # Gradient descent
        n_samples = len(X_norm)
        for epoch in range(epochs):
            # Forward pass
            predictions = np.dot(X_norm, self.weights) + self.bias
            
            # Compute loss (MSE)
            loss = np.mean((predictions - y) ** 2)
            
            # Backward pass
            dw = (2 / n_samples) * np.dot(X_norm.T, (predictions - y))
            db = (2 / n_samples) * np.sum(predictions - y)
            
            # Update weights
            self.weights -= learning_rate * dw
            self.bias -= learning_rate * db
            
            # Early stopping if loss is very small
            if loss < 1e-6:
                break
        
        self.is_trained = True
        logger.info(f"Model trained with final loss: {loss:.6f}")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions"""
        if not self.is_trained:
            logger.warning("Model not trained, returning zeros")
            return np.zeros(len(X))
        
        X_norm = (X - self.feature_means) / self.feature_stds
        return np.dot(X_norm, self.weights) + self.bias
    
    def get_feature_importance(self) -> np.ndarray:
        """Get feature importance based on absolute weights"""
        if not self.is_trained:
            return np.zeros(len(self.weights) if self.weights is not None else 0)
        
        # Normalize weights to get relative importance
        abs_weights = np.abs(self.weights)
        if np.sum(abs_weights) == 0:
            return abs_weights
        
        return abs_weights / np.sum(abs_weights)


class PerformancePredictor:
    """
    Lightweight ML model for predicting provider performance
    Uses simple linear regression with engineered features
    """
    
    def __init__(self, max_history_size: int = 1000):
        self.max_history_size = max_history_size
        self.response_time_models: Dict[str, SimpleLinearRegression] = {}
        self.success_rate_models: Dict[str, SimpleLinearRegression] = {}
        self.training_data: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.feature_stats: Dict[str, Dict[str, float]] = {}
        self.task_type_encoding: Dict[str, int] = {}
        self.last_training_time: Dict[str, datetime] = {}
        self.retrain_interval = timedelta(minutes=30)
    
    def _encode_task_type(self, task_type: Optional[str]) -> float:
        """Encode task type as numeric value"""
        if task_type is None:
            return 0.0
        
        if task_type not in self.task_type_encoding:
            self.task_type_encoding[task_type] = len(self.task_type_encoding) + 1
        
        return float(self.task_type_encoding[task_type])
    
    def _extract_features(self, request_data: Dict[str, Any], provider_name: str) -> PredictionFeatures:
        """Extract features from request data"""
        # Request features
        prompt = request_data.get('prompt', '')
        request_length = len(prompt) / 1000.0  # Normalize to thousands of chars
        
        # Simple complexity estimation based on length and content
        complexity_indicators = ['analyze', 'explain', 'complex', 'detailed', 'comprehensive']
        complexity_score = sum(1 for word in complexity_indicators if word in prompt.lower())
        request_complexity = min(complexity_score / len(complexity_indicators), 1.0)
        
        # Task type encoding
        task_type = request_data.get('task_type')
        task_type_encoded = self._encode_task_type(task_type)
        
        # Time features
        now = datetime.utcnow()
        time_of_day = now.hour / 24.0
        day_of_week = now.weekday() / 7.0
        
        # Provider historical features
        provider_stats = self.feature_stats.get(provider_name, {})
        historical_avg_response_time = provider_stats.get('avg_response_time', 2.0)
        historical_success_rate = provider_stats.get('success_rate', 0.95)
        recent_error_rate = provider_stats.get('recent_error_rate', 0.05)
        
        # Provider load (simplified)
        provider_load = provider_stats.get('load', 0.5)
        
        # Request similarity (placeholder - could be improved with embeddings)
        request_similarity = 0.5
        
        return PredictionFeatures(
            request_length=request_length,
            request_complexity=request_complexity,
            task_type_encoded=task_type_encoded,
            time_of_day=time_of_day,
            day_of_week=day_of_week,
            historical_avg_response_time=historical_avg_response_time,
            historical_success_rate=historical_success_rate,
            recent_error_rate=recent_error_rate,
            provider_load=provider_load,
            request_similarity=request_similarity
        )
    
    def add_training_data(self, provider_name: str, request_data: Dict[str, Any], 
                         response_time: float, success: bool):
        """Add training data point"""
        training_point = {
            'request_data': request_data,
            'response_time': response_time,
            'success': success,
            'timestamp': datetime.utcnow()
        }
        
        self.training_data[provider_name].append(training_point)
        
        # Keep only recent data
        if len(self.training_data[provider_name]) > self.max_history_size:
            self.training_data[provider_name].pop(0)
        
        # Update feature statistics
        self._update_feature_stats(provider_name)
        
        # Check if we need to retrain
        if self._should_retrain(provider_name):
            self._train_models(provider_name)
    
    def _update_feature_stats(self, provider_name: str):
        """Update feature statistics for a provider"""
        data = self.training_data[provider_name]
        if not data:
            return
        
        # Calculate recent statistics (last 50 requests)
        recent_data = data[-50:]
        
        response_times = [d['response_time'] for d in recent_data]
        successes = [d['success'] for d in recent_data]
        
        self.feature_stats[provider_name] = {
            'avg_response_time': np.mean(response_times),
            'success_rate': np.mean(successes),
            'recent_error_rate': 1.0 - np.mean(successes),
            'load': len(recent_data) / 100.0,  # Simplified load metric
            'last_updated': datetime.utcnow()
        }
    
    def _should_retrain(self, provider_name: str) -> bool:
        """Check if model should be retrained"""
        if provider_name not in self.last_training_time:
            return len(self.training_data[provider_name]) >= 20  # Minimum data for training
        
        time_since_training = datetime.utcnow() - self.last_training_time[provider_name]
        return time_since_training >= self.retrain_interval
    
    def _train_models(self, provider_name: str):
        """Train ML models for a provider"""
        data = self.training_data[provider_name]
        if len(data) < 10:  # Need minimum data
            return
        
        try:
            # Prepare training data
            X = []
            y_response_time = []
            y_success_rate = []
            
            for point in data:
                features = self._extract_features(point['request_data'], provider_name)
                feature_vector = [
                    features.request_length,
                    features.request_complexity,
                    features.task_type_encoded,
                    features.time_of_day,
                    features.day_of_week,
                    features.historical_avg_response_time,
                    features.historical_success_rate,
                    features.recent_error_rate,
                    features.provider_load,
                    features.request_similarity
                ]
                
                X.append(feature_vector)
                y_response_time.append(point['response_time'])
                y_success_rate.append(float(point['success']))
            
            X = np.array(X)
            y_response_time = np.array(y_response_time)
            y_success_rate = np.array(y_success_rate)
            
            # Train response time model
            if provider_name not in self.response_time_models:
                self.response_time_models[provider_name] = SimpleLinearRegression()
            
            self.response_time_models[provider_name].train(X, y_response_time)
            
            # Train success rate model
            if provider_name not in self.success_rate_models:
                self.success_rate_models[provider_name] = SimpleLinearRegression()
            
            self.success_rate_models[provider_name].train(X, y_success_rate)
            
            self.last_training_time[provider_name] = datetime.utcnow()
            
            logger.info(f"Trained models for provider {provider_name} with {len(data)} data points")
            
        except Exception as e:
            logger.error(f"Error training models for {provider_name}: {str(e)}")
    
    def predict_performance(self, provider_name: str, request_data: Dict[str, Any]) -> ModelPrediction:
        """Predict provider performance for a request"""
        # Extract features
        features = self._extract_features(request_data, provider_name)
        feature_vector = np.array([[
            features.request_length,
            features.request_complexity,
            features.task_type_encoded,
            features.time_of_day,
            features.day_of_week,
            features.historical_avg_response_time,
            features.historical_success_rate,
            features.recent_error_rate,
            features.provider_load,
            features.request_similarity
        ]])
        
        # Default predictions
        predicted_response_time = features.historical_avg_response_time
        predicted_success_rate = features.historical_success_rate
        confidence_score = 0.5  # Low confidence without trained models
        
        # Use trained models if available
        if provider_name in self.response_time_models:
            try:
                predicted_response_time = float(self.response_time_models[provider_name].predict(feature_vector)[0])
                confidence_score = min(confidence_score + 0.3, 1.0)
            except Exception as e:
                logger.warning(f"Error predicting response time for {provider_name}: {str(e)}")
        
        if provider_name in self.success_rate_models:
            try:
                predicted_success_rate = float(self.success_rate_models[provider_name].predict(feature_vector)[0])
                predicted_success_rate = max(0.0, min(1.0, predicted_success_rate))  # Clamp to [0,1]
                confidence_score = min(confidence_score + 0.3, 1.0)
            except Exception as e:
                logger.warning(f"Error predicting success rate for {provider_name}: {str(e)}")
        
        # Calculate feature importance
        feature_importance = {}
        if provider_name in self.response_time_models:
            try:
                importance = self.response_time_models[provider_name].get_feature_importance()
                feature_names = [
                    'request_length', 'request_complexity', 'task_type', 'time_of_day',
                    'day_of_week', 'historical_response_time', 'historical_success_rate',
                    'recent_error_rate', 'provider_load', 'request_similarity'
                ]
                feature_importance = {name: float(imp) for name, imp in zip(feature_names, importance)}
            except Exception as e:
                logger.warning(f"Error calculating feature importance for {provider_name}: {str(e)}")
        
        return ModelPrediction(
            predicted_response_time=predicted_response_time,
            predicted_success_rate=predicted_success_rate,
            confidence_score=confidence_score,
            feature_importance=feature_importance
        )
    
    def get_model_stats(self) -> Dict[str, Any]:
        """Get statistics about the trained models"""
        stats = {
            'providers_with_models': len(self.response_time_models),
            'total_training_data': sum(len(data) for data in self.training_data.values()),
            'last_training_times': {
                provider: time.isoformat() 
                for provider, time in self.last_training_time.items()
            },
            'feature_stats': self.feature_stats.copy(),
            'task_type_encoding': self.task_type_encoding.copy()
        }
        
        return stats
    
    def save_models(self, filepath: str):
        """Save trained models to file"""
        try:
            model_data = {
                'response_time_models': {},
                'success_rate_models': {},
                'feature_stats': self.feature_stats,
                'task_type_encoding': self.task_type_encoding,
                'last_training_time': {
                    provider: time.isoformat() 
                    for provider, time in self.last_training_time.items()
                }
            }
            
            # Save model parameters
            for provider, model in self.response_time_models.items():
                if model.is_trained:
                    model_data['response_time_models'][provider] = {
                        'weights': model.weights.tolist() if model.weights is not None else None,
                        'bias': float(model.bias) if model.bias is not None else None,
                        'feature_means': model.feature_means.tolist() if model.feature_means is not None else None,
                        'feature_stds': model.feature_stds.tolist() if model.feature_stds is not None else None
                    }
            
            for provider, model in self.success_rate_models.items():
                if model.is_trained:
                    model_data['success_rate_models'][provider] = {
                        'weights': model.weights.tolist() if model.weights is not None else None,
                        'bias': float(model.bias) if model.bias is not None else None,
                        'feature_means': model.feature_means.tolist() if model.feature_means is not None else None,
                        'feature_stds': model.feature_stds.tolist() if model.feature_stds is not None else None
                    }
            
            with open(filepath, 'w') as f:
                json.dump(model_data, f, indent=2)
            
            logger.info(f"Models saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving models: {str(e)}")
    
    def load_models(self, filepath: str):
        """Load trained models from file"""
        try:
            with open(filepath, 'r') as f:
                model_data = json.load(f)
            
            # Load feature stats and encoding
            self.feature_stats = model_data.get('feature_stats', {})
            self.task_type_encoding = model_data.get('task_type_encoding', {})
            
            # Load training times
            for provider, time_str in model_data.get('last_training_time', {}).items():
                self.last_training_time[provider] = datetime.fromisoformat(time_str)
            
            # Load response time models
            for provider, model_params in model_data.get('response_time_models', {}).items():
                model = SimpleLinearRegression()
                if model_params['weights'] is not None:
                    model.weights = np.array(model_params['weights'])
                    model.bias = model_params['bias']
                    model.feature_means = np.array(model_params['feature_means'])
                    model.feature_stds = np.array(model_params['feature_stds'])
                    model.is_trained = True
                self.response_time_models[provider] = model
            
            # Load success rate models
            for provider, model_params in model_data.get('success_rate_models', {}).items():
                model = SimpleLinearRegression()
                if model_params['weights'] is not None:
                    model.weights = np.array(model_params['weights'])
                    model.bias = model_params['bias']
                    model.feature_means = np.array(model_params['feature_means'])
                    model.feature_stds = np.array(model_params['feature_stds'])
                    model.is_trained = True
                self.success_rate_models[provider] = model
            
            logger.info(f"Models loaded from {filepath}")
            
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")


# Global predictor instance
performance_predictor = PerformancePredictor()