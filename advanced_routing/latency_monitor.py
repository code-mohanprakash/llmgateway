"""
Advanced Latency Monitoring System
Measures and tracks latency to different providers from various geographic locations
"""

import asyncio
import time
import statistics
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
import aiohttp
import socket
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


@dataclass
class LatencyMeasurement:
    """Individual latency measurement"""
    provider_name: str
    endpoint: str
    latency_ms: float
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None
    region: Optional[str] = None
    connection_type: str = "direct"  # direct, proxy, cdn
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'provider_name': self.provider_name,
            'endpoint': self.endpoint,
            'latency_ms': self.latency_ms,
            'timestamp': self.timestamp.isoformat(),
            'success': self.success,
            'error_message': self.error_message,
            'region': self.region,
            'connection_type': self.connection_type
        }


@dataclass
class LatencyStats:
    """Latency statistics for a provider"""
    provider_name: str
    avg_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    success_rate: float
    measurement_count: int
    last_measurement: datetime
    region: Optional[str] = None
    jitter_ms: float = 0.0  # Standard deviation
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'provider_name': self.provider_name,
            'avg_latency_ms': self.avg_latency_ms,
            'min_latency_ms': self.min_latency_ms,
            'max_latency_ms': self.max_latency_ms,
            'p50_latency_ms': self.p50_latency_ms,
            'p95_latency_ms': self.p95_latency_ms,
            'p99_latency_ms': self.p99_latency_ms,
            'success_rate': self.success_rate,
            'measurement_count': self.measurement_count,
            'last_measurement': self.last_measurement.isoformat(),
            'region': self.region,
            'jitter_ms': self.jitter_ms
        }


class LatencyMonitor:
    """
    Advanced latency monitoring system with geographic awareness
    
    Features:
    - Real-time latency measurement to provider endpoints
    - Geographic latency tracking
    - Connection type detection (direct, proxy, CDN)
    - Latency statistics and percentiles
    - Jitter measurement
    - Health monitoring integration
    """
    
    def __init__(self, measurement_interval: int = 300):  # 5 minutes
        self.measurement_interval = measurement_interval
        self.measurements: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.provider_endpoints: Dict[str, List[str]] = {}
        self.latency_stats: Dict[str, LatencyStats] = {}
        self.monitoring_active = False
        self.monitor_task: Optional[asyncio.Task] = None
        
        # Geographic configuration
        self.region_mapping = {
            'us-east-1': 'North America',
            'us-west-2': 'North America', 
            'eu-west-1': 'Europe',
            'eu-central-1': 'Europe',
            'ap-southeast-1': 'Asia Pacific',
            'ap-northeast-1': 'Asia Pacific'
        }
        
        # Provider endpoint configuration
        self.default_endpoints = {
            'openai': [
                'https://api.openai.com/v1/models',
                'https://api.openai.com/v1/chat/completions'
            ],
            'anthropic': [
                'https://api.anthropic.com/v1/messages',
                'https://api.anthropic.com/v1/models'
            ],
            'google': [
                'https://generativelanguage.googleapis.com/v1/models',
                'https://generativelanguage.googleapis.com/v1beta/models'
            ],
            'groq': [
                'https://api.groq.com/openai/v1/models',
                'https://api.groq.com/openai/v1/chat/completions'
            ]
        }
        
        # Timeout configuration
        self.timeout_config = aiohttp.ClientTimeout(
            total=10.0,
            connect=5.0,
            sock_read=5.0
        )
        
        # Initialize provider endpoints
        self.provider_endpoints = self.default_endpoints.copy()
    
    def register_provider(self, provider_name: str, endpoints: List[str]):
        """Register a provider with its endpoints for monitoring"""
        self.provider_endpoints[provider_name] = endpoints
        logger.info(f"Registered provider {provider_name} with {len(endpoints)} endpoints")
    
    def unregister_provider(self, provider_name: str):
        """Unregister a provider from monitoring"""
        if provider_name in self.provider_endpoints:
            del self.provider_endpoints[provider_name]
            if provider_name in self.measurements:
                del self.measurements[provider_name]
            if provider_name in self.latency_stats:
                del self.latency_stats[provider_name]
            logger.info(f"Unregistered provider {provider_name}")
    
    async def start_monitoring(self):
        """Start the latency monitoring background task"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Latency monitoring started")
    
    async def stop_monitoring(self):
        """Stop the latency monitoring background task"""
        self.monitoring_active = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Latency monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                await self._measure_all_providers()
                await asyncio.sleep(self.measurement_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in latency monitoring loop: {str(e)}")
                await asyncio.sleep(min(self.measurement_interval, 60))
    
    async def _measure_all_providers(self):
        """Measure latency to all registered providers"""
        tasks = []
        
        for provider_name, endpoints in self.provider_endpoints.items():
            for endpoint in endpoints:
                task = asyncio.create_task(
                    self._measure_endpoint_latency(provider_name, endpoint)
                )
                tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Latency measurement failed: {str(result)}")
                elif result:
                    await self._process_measurement(result)
    
    async def _measure_endpoint_latency(self, provider_name: str, endpoint: str) -> Optional[LatencyMeasurement]:
        """Measure latency to a specific endpoint"""
        start_time = time.time()
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout_config) as session:
                async with session.head(endpoint) as response:
                    end_time = time.time()
                    latency_ms = (end_time - start_time) * 1000
                    
                    # Determine region from response headers or endpoint
                    region = self._determine_region(response.headers, endpoint)
                    
                    # Detect connection type
                    connection_type = self._detect_connection_type(response.headers)
                    
                    return LatencyMeasurement(
                        provider_name=provider_name,
                        endpoint=endpoint,
                        latency_ms=latency_ms,
                        timestamp=datetime.utcnow(),
                        success=response.status < 400,
                        region=region,
                        connection_type=connection_type
                    )
        
        except asyncio.TimeoutError:
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            return LatencyMeasurement(
                provider_name=provider_name,
                endpoint=endpoint,
                latency_ms=latency_ms,
                timestamp=datetime.utcnow(),
                success=False,
                error_message="Timeout"
            )
        
        except Exception as e:
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            return LatencyMeasurement(
                provider_name=provider_name,
                endpoint=endpoint,
                latency_ms=latency_ms,
                timestamp=datetime.utcnow(),
                success=False,
                error_message=str(e)
            )
    
    def _determine_region(self, headers: Dict[str, str], endpoint: str) -> Optional[str]:
        """Determine the region from response headers or endpoint"""
        # Check common region headers
        region_headers = [
            'x-amzn-region',
            'x-aws-region',
            'x-goog-region',
            'x-azure-region',
            'x-datacenter-region'
        ]
        
        for header in region_headers:
            if header in headers:
                region_code = headers[header]
                return self.region_mapping.get(region_code, region_code)
        
        # Fallback to endpoint-based region detection
        if 'us-east' in endpoint or 'us-west' in endpoint:
            return 'North America'
        elif 'eu-' in endpoint or 'europe' in endpoint:
            return 'Europe'
        elif 'ap-' in endpoint or 'asia' in endpoint:
            return 'Asia Pacific'
        
        return None
    
    def _detect_connection_type(self, headers: Dict[str, str]) -> str:
        """Detect connection type from response headers"""
        # Check for CDN headers
        cdn_headers = [
            'x-cache',
            'x-served-by',
            'x-cache-status',
            'cf-ray',  # Cloudflare
            'x-amz-cf-id',  # AWS CloudFront
            'x-azure-ref'  # Azure CDN
        ]
        
        for header in cdn_headers:
            if header in headers:
                return 'cdn'
        
        # Check for proxy headers
        proxy_headers = [
            'via',
            'x-forwarded-for',
            'x-real-ip',
            'x-proxy-cache'
        ]
        
        for header in proxy_headers:
            if header in headers:
                return 'proxy'
        
        return 'direct'
    
    async def _process_measurement(self, measurement: LatencyMeasurement):
        """Process a latency measurement and update statistics"""
        provider_name = measurement.provider_name
        
        # Add to measurements history
        self.measurements[provider_name].append(measurement)
        
        # Update statistics
        await self._update_statistics(provider_name)
    
    async def _update_statistics(self, provider_name: str):
        """Update latency statistics for a provider"""
        if provider_name not in self.measurements:
            return
        
        measurements = list(self.measurements[provider_name])
        if not measurements:
            return
        
        # Filter recent successful measurements (last 24 hours)
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_measurements = [
            m for m in measurements 
            if m.timestamp >= recent_cutoff and m.success
        ]
        
        if not recent_measurements:
            return
        
        # Calculate statistics
        latencies = [m.latency_ms for m in recent_measurements]
        
        avg_latency = statistics.mean(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        
        # Calculate percentiles
        sorted_latencies = sorted(latencies)
        n = len(sorted_latencies)
        
        p50_latency = sorted_latencies[int(0.5 * n)]
        p95_latency = sorted_latencies[int(0.95 * n)]
        p99_latency = sorted_latencies[int(0.99 * n)]
        
        # Calculate jitter (standard deviation)
        jitter = statistics.stdev(latencies) if len(latencies) > 1 else 0.0
        
        # Calculate success rate
        total_measurements = len([m for m in measurements if m.timestamp >= recent_cutoff])
        success_rate = len(recent_measurements) / total_measurements if total_measurements > 0 else 0.0
        
        # Determine primary region
        regions = [m.region for m in recent_measurements if m.region]
        primary_region = statistics.mode(regions) if regions else None
        
        # Update statistics
        self.latency_stats[provider_name] = LatencyStats(
            provider_name=provider_name,
            avg_latency_ms=avg_latency,
            min_latency_ms=min_latency,
            max_latency_ms=max_latency,
            p50_latency_ms=p50_latency,
            p95_latency_ms=p95_latency,
            p99_latency_ms=p99_latency,
            success_rate=success_rate,
            measurement_count=len(recent_measurements),
            last_measurement=max(m.timestamp for m in recent_measurements),
            region=primary_region,
            jitter_ms=jitter
        )
    
    async def measure_provider_latency(self, provider_name: str, endpoint: str) -> Optional[LatencyMeasurement]:
        """Measure latency to a specific provider endpoint on-demand"""
        measurement = await self._measure_endpoint_latency(provider_name, endpoint)
        if measurement:
            await self._process_measurement(measurement)
        return measurement
    
    def get_provider_latency_stats(self, provider_name: str) -> Optional[LatencyStats]:
        """Get latency statistics for a provider"""
        return self.latency_stats.get(provider_name)
    
    def get_all_latency_stats(self) -> Dict[str, LatencyStats]:
        """Get latency statistics for all providers"""
        return self.latency_stats.copy()
    
    def get_fastest_providers(self, limit: int = 5) -> List[Tuple[str, float]]:
        """Get the fastest providers by average latency"""
        provider_latencies = [
            (name, stats.avg_latency_ms)
            for name, stats in self.latency_stats.items()
            if stats.success_rate > 0.5  # Only include providers with >50% success rate
        ]
        
        # Sort by latency (ascending)
        provider_latencies.sort(key=lambda x: x[1])
        
        return provider_latencies[:limit]
    
    def get_providers_by_region(self, region: str) -> List[str]:
        """Get providers that primarily serve from a specific region"""
        return [
            name for name, stats in self.latency_stats.items()
            if stats.region == region
        ]
    
    def get_latency_analytics(self) -> Dict[str, Any]:
        """Get comprehensive latency analytics"""
        current_time = datetime.utcnow()
        
        # Calculate overall statistics
        total_measurements = sum(len(measurements) for measurements in self.measurements.values())
        active_providers = len([stats for stats in self.latency_stats.values() if stats.success_rate > 0.5])
        
        # Calculate region distribution
        region_distribution = defaultdict(int)
        for stats in self.latency_stats.values():
            if stats.region:
                region_distribution[stats.region] += 1
        
        # Calculate connection type distribution
        connection_types = defaultdict(int)
        for measurements in self.measurements.values():
            for measurement in list(measurements)[-100:]:  # Recent measurements
                connection_types[measurement.connection_type] += 1
        
        # Calculate performance trends
        performance_trends = {}
        for provider_name, measurements in self.measurements.items():
            recent_measurements = [
                m for m in measurements 
                if m.timestamp >= current_time - timedelta(hours=1) and m.success
            ]
            
            if len(recent_measurements) >= 2:
                recent_latencies = [m.latency_ms for m in recent_measurements]
                avg_recent = statistics.mean(recent_latencies)
                
                # Compare with overall average
                overall_avg = self.latency_stats[provider_name].avg_latency_ms
                trend = "improving" if avg_recent < overall_avg * 0.9 else "degrading" if avg_recent > overall_avg * 1.1 else "stable"
                
                performance_trends[provider_name] = {
                    'trend': trend,
                    'recent_avg': avg_recent,
                    'overall_avg': overall_avg,
                    'change_percent': ((avg_recent - overall_avg) / overall_avg) * 100
                }
        
        return {
            'monitoring_active': self.monitoring_active,
            'total_measurements': total_measurements,
            'active_providers': active_providers,
            'measurement_interval': self.measurement_interval,
            'region_distribution': dict(region_distribution),
            'connection_type_distribution': dict(connection_types),
            'performance_trends': performance_trends,
            'fastest_providers': self.get_fastest_providers(),
            'provider_stats': {
                name: stats.to_dict() 
                for name, stats in self.latency_stats.items()
            },
            'last_updated': current_time.isoformat()
        }
    
    def export_measurements(self, provider_name: Optional[str] = None, 
                          hours: int = 24) -> Dict[str, Any]:
        """Export latency measurements"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        export_data = {
            'export_timestamp': datetime.utcnow().isoformat(),
            'time_range_hours': hours,
            'measurements': {}
        }
        
        providers_to_export = [provider_name] if provider_name else self.measurements.keys()
        
        for provider in providers_to_export:
            if provider in self.measurements:
                recent_measurements = [
                    m.to_dict() for m in self.measurements[provider]
                    if m.timestamp >= cutoff_time
                ]
                
                export_data['measurements'][provider] = {
                    'count': len(recent_measurements),
                    'data': recent_measurements
                }
        
        return export_data


# Global latency monitor instance
latency_monitor = LatencyMonitor()