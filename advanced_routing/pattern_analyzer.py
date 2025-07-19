"""
Advanced Request Pattern Analysis
Analyzes request patterns to identify optimal routing strategies
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import json
import hashlib
import re
from statistics import mean, median, mode

from providers.base import GenerationRequest

logger = logging.getLogger(__name__)


@dataclass
class RequestCluster:
    """Represents a cluster of similar requests"""
    cluster_id: str
    centroid_features: Dict[str, float]
    request_count: int
    avg_response_time: float
    success_rate: float
    preferred_providers: List[str]
    common_keywords: List[str]
    time_patterns: Dict[str, int]  # hour -> count
    complexity_distribution: Dict[str, int]
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RequestFeatures:
    """Extracted features from a request"""
    length: int
    word_count: int
    sentence_count: int
    question_count: int
    code_blocks: int
    urls: int
    keywords: Set[str]
    language_indicators: Set[str]
    complexity_indicators: Set[str]
    sentiment_indicators: Set[str]
    domain_indicators: Set[str]


class AdvancedPatternAnalyzer:
    """
    Advanced pattern analysis with clustering and feature extraction
    """
    
    def __init__(self, max_history_size: int = 5000):
        self.max_history_size = max_history_size
        self.request_history: List[Dict[str, Any]] = []
        self.request_clusters: Dict[str, RequestCluster] = {}
        self.feature_extractors = self._initialize_feature_extractors()
        self.clustering_threshold = 0.7
        self.min_cluster_size = 10
        self.last_clustering_time = datetime.utcnow()
        self.clustering_interval = timedelta(hours=1)
        
        # Pattern keywords for different domains
        self.domain_keywords = {
            'code': ['function', 'class', 'def', 'import', 'return', 'if', 'for', 'while', 'try', 'except'],
            'analysis': ['analyze', 'examine', 'compare', 'evaluate', 'assess', 'review', 'study'],
            'creative': ['write', 'create', 'generate', 'story', 'poem', 'article', 'blog'],
            'technical': ['implement', 'develop', 'design', 'architecture', 'system', 'database'],
            'business': ['strategy', 'market', 'revenue', 'profit', 'customer', 'sales', 'growth'],
            'education': ['explain', 'teach', 'learn', 'understand', 'concept', 'theory', 'example'],
            'research': ['research', 'study', 'survey', 'data', 'findings', 'methodology', 'hypothesis']
        }
        
        self.complexity_keywords = {
            'simple': ['simple', 'basic', 'easy', 'quick', 'brief', 'short'],
            'medium': ['detailed', 'thorough', 'comprehensive', 'complete'],
            'complex': ['complex', 'advanced', 'sophisticated', 'in-depth', 'detailed analysis', 'comprehensive study']
        }
    
    def _initialize_feature_extractors(self) -> Dict[str, Any]:
        """Initialize feature extraction patterns"""
        return {
            'code_block_pattern': re.compile(r'```[\s\S]*?```|`[^`]+`'),
            'url_pattern': re.compile(r'https?://[^\s]+'),
            'question_pattern': re.compile(r'\?'),
            'sentence_pattern': re.compile(r'[.!?]+'),
            'word_pattern': re.compile(r'\b\w+\b'),
            'email_pattern': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'number_pattern': re.compile(r'\b\d+(?:\.\d+)?\b'),
            'caps_pattern': re.compile(r'\b[A-Z]{2,}\b')
        }
    
    def extract_features(self, request: GenerationRequest) -> RequestFeatures:
        """Extract comprehensive features from a request"""
        text = request.prompt
        if request.system_message:
            text += " " + request.system_message
        
        text_lower = text.lower()
        
        # Basic text features
        length = len(text)
        words = self.feature_extractors['word_pattern'].findall(text)
        word_count = len(words)
        sentence_count = len(self.feature_extractors['sentence_pattern'].findall(text))
        question_count = len(self.feature_extractors['question_pattern'].findall(text))
        
        # Code and technical features
        code_blocks = len(self.feature_extractors['code_block_pattern'].findall(text))
        urls = len(self.feature_extractors['url_pattern'].findall(text))
        
        # Extract keywords
        keywords = set()
        for word in words:
            if len(word) > 3:  # Filter short words
                keywords.add(word.lower())
        
        # Language indicators
        language_indicators = set()
        language_keywords = {
            'python': ['python', 'django', 'flask', 'pandas', 'numpy'],
            'javascript': ['javascript', 'js', 'node', 'react', 'vue'],
            'java': ['java', 'spring', 'maven', 'gradle'],
            'sql': ['sql', 'database', 'mysql', 'postgresql'],
            'html': ['html', 'css', 'bootstrap', 'tailwind'],
            'api': ['api', 'rest', 'graphql', 'endpoint']
        }
        
        for lang, lang_keywords in language_keywords.items():
            if any(kw in text_lower for kw in lang_keywords):
                language_indicators.add(lang)
        
        # Complexity indicators
        complexity_indicators = set()
        for complexity, comp_keywords in self.complexity_keywords.items():
            if any(kw in text_lower for kw in comp_keywords):
                complexity_indicators.add(complexity)
        
        # Sentiment indicators (simplified)
        sentiment_indicators = set()
        positive_words = ['good', 'great', 'excellent', 'amazing', 'perfect', 'love']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'problem', 'issue', 'error']
        
        if any(word in text_lower for word in positive_words):
            sentiment_indicators.add('positive')
        if any(word in text_lower for word in negative_words):
            sentiment_indicators.add('negative')
        
        # Domain indicators
        domain_indicators = set()
        for domain, domain_keywords in self.domain_keywords.items():
            if any(kw in text_lower for kw in domain_keywords):
                domain_indicators.add(domain)
        
        return RequestFeatures(
            length=length,
            word_count=word_count,
            sentence_count=sentence_count,
            question_count=question_count,
            code_blocks=code_blocks,
            urls=urls,
            keywords=keywords,
            language_indicators=language_indicators,
            complexity_indicators=complexity_indicators,
            sentiment_indicators=sentiment_indicators,
            domain_indicators=domain_indicators
        )
    
    def add_request_data(self, request: GenerationRequest, provider_used: str, 
                        response_time: float, success: bool):
        """Add request data for pattern analysis"""
        features = self.extract_features(request)
        
        request_data = {
            'request': request,
            'features': features,
            'provider_used': provider_used,
            'response_time': response_time,
            'success': success,
            'timestamp': datetime.utcnow(),
            'hour': datetime.utcnow().hour,
            'day_of_week': datetime.utcnow().weekday(),
            'task_type': getattr(request, 'task_type', None),
            'complexity': getattr(request, 'complexity', None)
        }
        
        self.request_history.append(request_data)
        
        # Maintain history size
        if len(self.request_history) > self.max_history_size:
            self.request_history.pop(0)
        
        # Periodic clustering
        if datetime.utcnow() - self.last_clustering_time > self.clustering_interval:
            # Note: In a real implementation, you would schedule this as a background task
            # For now, we'll call it synchronously
            asyncio.create_task(self._perform_clustering())
    
    async def _perform_clustering(self):
        """Perform clustering analysis on request history"""
        try:
            if len(self.request_history) < self.min_cluster_size * 2:
                return
            
            logger.info("Performing request clustering analysis...")
            
            # Simple clustering based on feature similarity
            clusters = defaultdict(list)
            
            for request_data in self.request_history:
                cluster_id = self._find_best_cluster(request_data)
                clusters[cluster_id].append(request_data)
            
            # Update request clusters
            self.request_clusters = {}
            
            for cluster_id, cluster_requests in clusters.items():
                if len(cluster_requests) >= self.min_cluster_size:
                    cluster = self._create_cluster(cluster_id, cluster_requests)
                    self.request_clusters[cluster_id] = cluster
            
            self.last_clustering_time = datetime.utcnow()
            logger.info(f"Created {len(self.request_clusters)} request clusters")
            
        except Exception as e:
            logger.error(f"Error in clustering analysis: {str(e)}")
    
    def _find_best_cluster(self, request_data: Dict[str, Any]) -> str:
        """Find the best cluster for a request"""
        features = request_data['features']
        
        # Create cluster key based on dominant features
        cluster_key_parts = []
        
        # Length category
        if features.length < 100:
            cluster_key_parts.append("short")
        elif features.length < 500:
            cluster_key_parts.append("medium")
        else:
            cluster_key_parts.append("long")
        
        # Domain indicators
        if features.domain_indicators:
            primary_domain = sorted(features.domain_indicators)[0]  # Use first alphabetically for consistency
            cluster_key_parts.append(f"domain_{primary_domain}")
        
        # Complexity indicators
        if features.complexity_indicators:
            primary_complexity = sorted(features.complexity_indicators)[0]
            cluster_key_parts.append(f"complexity_{primary_complexity}")
        
        # Task type
        task_type = request_data.get('task_type', 'general')
        cluster_key_parts.append(f"task_{task_type}")
        
        # Code presence
        if features.code_blocks > 0:
            cluster_key_parts.append("has_code")
        
        # Question type
        if features.question_count > 0:
            cluster_key_parts.append("has_questions")
        
        return "_".join(cluster_key_parts)
    
    def _create_cluster(self, cluster_id: str, cluster_requests: List[Dict[str, Any]]) -> RequestCluster:
        """Create a RequestCluster from grouped requests"""
        # Calculate centroid features
        centroid_features = {
            'avg_length': mean(r['features'].length for r in cluster_requests),
            'avg_word_count': mean(r['features'].word_count for r in cluster_requests),
            'avg_sentence_count': mean(r['features'].sentence_count for r in cluster_requests),
            'avg_question_count': mean(r['features'].question_count for r in cluster_requests),
            'avg_code_blocks': mean(r['features'].code_blocks for r in cluster_requests),
            'avg_urls': mean(r['features'].urls for r in cluster_requests)
        }
        
        # Performance metrics
        avg_response_time = mean(r['response_time'] for r in cluster_requests)
        success_rate = sum(r['success'] for r in cluster_requests) / len(cluster_requests)
        
        # Provider preferences
        provider_counts = Counter(r['provider_used'] for r in cluster_requests)
        preferred_providers = [provider for provider, count in provider_counts.most_common(5)]
        
        # Common keywords
        all_keywords = []
        for r in cluster_requests:
            all_keywords.extend(r['features'].keywords)
        
        keyword_counts = Counter(all_keywords)
        common_keywords = [kw for kw, count in keyword_counts.most_common(10) if count >= 3]
        
        # Time patterns
        hour_counts = Counter(r['hour'] for r in cluster_requests)
        time_patterns = dict(hour_counts)
        
        # Complexity distribution
        complexity_counts = Counter(r['complexity'] for r in cluster_requests if r['complexity'])
        complexity_distribution = dict(complexity_counts)
        
        return RequestCluster(
            cluster_id=cluster_id,
            centroid_features=centroid_features,
            request_count=len(cluster_requests),
            avg_response_time=avg_response_time,
            success_rate=success_rate,
            preferred_providers=preferred_providers,
            common_keywords=common_keywords,
            time_patterns=time_patterns,
            complexity_distribution=complexity_distribution
        )
    
    def find_matching_cluster(self, request: GenerationRequest) -> Optional[RequestCluster]:
        """Find the best matching cluster for a request"""
        if not self.request_clusters:
            return None
        
        # Create temporary request data
        temp_request_data = {
            'request': request,
            'features': self.extract_features(request),
            'task_type': getattr(request, 'task_type', None),
            'complexity': getattr(request, 'complexity', None)
        }
        
        # Find best cluster
        cluster_id = self._find_best_cluster(temp_request_data)
        return self.request_clusters.get(cluster_id)
    
    def get_cluster_recommendations(self, cluster: RequestCluster) -> Dict[str, Any]:
        """Get routing recommendations based on cluster analysis"""
        recommendations = {
            'primary_providers': cluster.preferred_providers[:3],
            'expected_response_time': cluster.avg_response_time,
            'expected_success_rate': cluster.success_rate,
            'optimal_hours': [],
            'complexity_insights': cluster.complexity_distribution,
            'common_patterns': cluster.common_keywords[:5]
        }
        
        # Find optimal hours (when performance is best)
        if cluster.time_patterns:
            # Simple heuristic: hours with more requests tend to have better performance
            sorted_hours = sorted(cluster.time_patterns.items(), key=lambda x: x[1], reverse=True)
            recommendations['optimal_hours'] = [hour for hour, count in sorted_hours[:6]]
        
        return recommendations
    
    def get_pattern_insights(self) -> Dict[str, Any]:
        """Get comprehensive pattern insights"""
        insights = {
            'total_clusters': len(self.request_clusters),
            'total_requests_analyzed': len(self.request_history),
            'cluster_summary': [],
            'domain_distribution': defaultdict(int),
            'complexity_trends': defaultdict(int),
            'performance_patterns': {},
            'time_usage_patterns': defaultdict(int)
        }
        
        # Analyze clusters
        for cluster_id, cluster in self.request_clusters.items():
            cluster_summary = {
                'cluster_id': cluster_id,
                'request_count': cluster.request_count,
                'avg_response_time': cluster.avg_response_time,
                'success_rate': cluster.success_rate,
                'top_providers': cluster.preferred_providers[:3],
                'main_keywords': cluster.common_keywords[:5]
            }
            insights['cluster_summary'].append(cluster_summary)
            
            # Aggregate domain distribution
            for keyword in cluster.common_keywords:
                for domain, domain_keywords in self.domain_keywords.items():
                    if keyword in domain_keywords:
                        insights['domain_distribution'][domain] += cluster.request_count
            
            # Aggregate complexity trends
            for complexity, count in cluster.complexity_distribution.items():
                insights['complexity_trends'][complexity] += count
            
            # Time usage patterns
            for hour, count in cluster.time_patterns.items():
                insights['time_usage_patterns'][hour] += count
        
        # Sort clusters by request count
        insights['cluster_summary'].sort(key=lambda x: x['request_count'], reverse=True)
        
        # Performance patterns
        if self.request_history:
            recent_requests = self.request_history[-1000:]  # Last 1000 requests
            
            # Provider performance
            provider_perf = defaultdict(list)
            for req in recent_requests:
                provider_perf[req['provider_used']].append(req['response_time'])
            
            insights['performance_patterns'] = {
                provider: {
                    'avg_response_time': mean(times),
                    'median_response_time': median(times),
                    'request_count': len(times)
                }
                for provider, times in provider_perf.items()
                if len(times) >= 5
            }
        
        return insights
    
    def export_patterns(self, filepath: str):
        """Export patterns to file"""
        try:
            export_data = {
                'clusters': {},
                'insights': self.get_pattern_insights(),
                'export_timestamp': datetime.utcnow().isoformat()
            }
            
            # Export clusters
            for cluster_id, cluster in self.request_clusters.items():
                export_data['clusters'][cluster_id] = {
                    'cluster_id': cluster.cluster_id,
                    'centroid_features': cluster.centroid_features,
                    'request_count': cluster.request_count,
                    'avg_response_time': cluster.avg_response_time,
                    'success_rate': cluster.success_rate,
                    'preferred_providers': cluster.preferred_providers,
                    'common_keywords': cluster.common_keywords,
                    'time_patterns': cluster.time_patterns,
                    'complexity_distribution': cluster.complexity_distribution,
                    'created_at': cluster.created_at.isoformat(),
                    'last_updated': cluster.last_updated.isoformat()
                }
            
            with open(filepath, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Patterns exported to {filepath}")
            
        except Exception as e:
            logger.error(f"Error exporting patterns: {str(e)}")
    
    def import_patterns(self, filepath: str):
        """Import patterns from file"""
        try:
            with open(filepath, 'r') as f:
                import_data = json.load(f)
            
            # Import clusters
            self.request_clusters = {}
            for cluster_id, cluster_data in import_data.get('clusters', {}).items():
                cluster = RequestCluster(
                    cluster_id=cluster_data['cluster_id'],
                    centroid_features=cluster_data['centroid_features'],
                    request_count=cluster_data['request_count'],
                    avg_response_time=cluster_data['avg_response_time'],
                    success_rate=cluster_data['success_rate'],
                    preferred_providers=cluster_data['preferred_providers'],
                    common_keywords=cluster_data['common_keywords'],
                    time_patterns=cluster_data['time_patterns'],
                    complexity_distribution=cluster_data['complexity_distribution'],
                    created_at=datetime.fromisoformat(cluster_data['created_at']),
                    last_updated=datetime.fromisoformat(cluster_data['last_updated'])
                )
                self.request_clusters[cluster_id] = cluster
            
            logger.info(f"Patterns imported from {filepath}")
            
        except Exception as e:
            logger.error(f"Error importing patterns: {str(e)}")


# Global pattern analyzer instance
pattern_analyzer = AdvancedPatternAnalyzer()