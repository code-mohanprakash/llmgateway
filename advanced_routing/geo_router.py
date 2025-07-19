"""
Geographic Routing System
Implements intelligent provider selection based on geographic location and latency
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict
import json
import yaml
from pathlib import Path
import ipaddress
import socket
try:
    import geoip2.database
    import geoip2.errors
    GEOIP2_AVAILABLE = True
except ImportError:
    geoip2 = None
    GEOIP2_AVAILABLE = False

from .latency_monitor import LatencyMonitor, LatencyStats
from providers.base import GenerationRequest

logger = logging.getLogger(__name__)


@dataclass
class GeoLocation:
    """Geographic location information"""
    country: str
    region: str
    city: str
    latitude: float
    longitude: float
    timezone: str
    continent: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'country': self.country,
            'region': self.region,
            'city': self.city,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'timezone': self.timezone,
            'continent': self.continent
        }


@dataclass
class GeoRoutingRule:
    """Geographic routing rule"""
    rule_id: str
    name: str
    description: str
    conditions: Dict[str, Any]
    actions: Dict[str, Any]
    priority: int
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'rule_id': self.rule_id,
            'name': self.name,
            'description': self.description,
            'conditions': self.conditions,
            'actions': self.actions,
            'priority': self.priority,
            'enabled': self.enabled,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class GeoRoutingDecision:
    """Geographic routing decision"""
    client_location: GeoLocation
    selected_providers: List[str]
    routing_reason: str
    confidence_score: float
    latency_considerations: Dict[str, float]
    rules_applied: List[str]
    fallback_used: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'client_location': self.client_location.to_dict(),
            'selected_providers': self.selected_providers,
            'routing_reason': self.routing_reason,
            'confidence_score': self.confidence_score,
            'latency_considerations': self.latency_considerations,
            'rules_applied': self.rules_applied,
            'fallback_used': self.fallback_used
        }


class GeoRouter:
    """
    Advanced geographic routing system with latency-based provider selection
    
    Features:
    - Geographic location detection from IP addresses
    - Latency-based provider selection
    - Region-based provider preferences
    - Custom routing rules
    - Fallback routing strategies
    - Performance analytics
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/geo_config.yaml"
        self.latency_monitor: Optional[LatencyMonitor] = None
        self.routing_rules: List[GeoRoutingRule] = []
        self.provider_regions: Dict[str, List[str]] = {}
        self.region_preferences: Dict[str, List[str]] = {}
        self.geoip_database: Optional[geoip2.database.Reader] = None
        
        # Default region mappings
        self.default_provider_regions = {
            'openai': ['North America', 'Europe', 'Asia Pacific'],
            'anthropic': ['North America', 'Europe'],
            'google': ['North America', 'Europe', 'Asia Pacific'],
            'groq': ['North America', 'Europe']
        }
        
        # Default region preferences (provider priority by region)
        self.default_region_preferences = {
            'North America': ['openai', 'anthropic', 'groq', 'google'],
            'Europe': ['openai', 'google', 'anthropic', 'groq'],
            'Asia Pacific': ['google', 'openai', 'anthropic', 'groq'],
            'South America': ['openai', 'google', 'anthropic', 'groq'],
            'Africa': ['google', 'openai', 'anthropic', 'groq'],
            'Oceania': ['google', 'openai', 'anthropic', 'groq']
        }
        
        # Routing configuration
        self.config = {
            'max_latency_threshold_ms': 5000,
            'latency_weight': 0.4,
            'region_preference_weight': 0.3,
            'performance_weight': 0.2,
            'availability_weight': 0.1,
            'fallback_enabled': True,
            'max_providers_per_request': 3,
            'confidence_threshold': 0.6
        }
        
        # Load configuration
        self._load_configuration()
        
        # Initialize GeoIP database
        self._initialize_geoip()
    
    def _load_configuration(self):
        """Load geographic routing configuration"""
        try:
            config_file = Path(self.config_path)
            if config_file.exists():
                with open(config_file, 'r') as f:
                    loaded_config = yaml.safe_load(f)
                    
                    # Update configuration
                    self.config.update(loaded_config.get('routing', {}))
                    
                    # Load provider regions
                    self.provider_regions = loaded_config.get('provider_regions', self.default_provider_regions)
                    
                    # Load region preferences
                    self.region_preferences = loaded_config.get('region_preferences', self.default_region_preferences)
                    
                    # Load routing rules
                    rules_data = loaded_config.get('routing_rules', [])
                    self.routing_rules = []
                    for rule_data in rules_data:
                        rule = GeoRoutingRule(
                            rule_id=rule_data['rule_id'],
                            name=rule_data['name'],
                            description=rule_data['description'],
                            conditions=rule_data['conditions'],
                            actions=rule_data['actions'],
                            priority=rule_data['priority'],
                            enabled=rule_data.get('enabled', True)
                        )
                        self.routing_rules.append(rule)
                    
                    # Sort rules by priority
                    self.routing_rules.sort(key=lambda x: x.priority)
                    
                    logger.info(f"Loaded geo routing configuration from {config_file}")
            else:
                logger.info("No geo routing configuration file found, using defaults")
                self.provider_regions = self.default_provider_regions
                self.region_preferences = self.default_region_preferences
                self._create_default_rules()
                
        except Exception as e:
            logger.error(f"Error loading geo routing configuration: {str(e)}")
            self.provider_regions = self.default_provider_regions
            self.region_preferences = self.default_region_preferences
            self._create_default_rules()
    
    def _initialize_geoip(self):
        """Initialize GeoIP database"""
        try:
            if not GEOIP2_AVAILABLE:
                logger.warning("GeoIP2 library not available. Geographic routing will use fallback methods.")
                self.geoip_database = None
                return
            
            # Try to find GeoIP database file
            possible_paths = [
                "/usr/local/share/GeoIP/GeoLite2-City.mmdb",
                "/opt/GeoIP/GeoLite2-City.mmdb",
                "data/GeoLite2-City.mmdb",
                "GeoLite2-City.mmdb"
            ]
            
            for path in possible_paths:
                if Path(path).exists():
                    self.geoip_database = geoip2.database.Reader(path)
                    logger.info(f"GeoIP database loaded from {path}")
                    break
            
            if not self.geoip_database:
                logger.warning("GeoIP database not found. Geographic routing will use fallback methods.")
                
        except Exception as e:
            logger.error(f"Error initializing GeoIP database: {str(e)}")
            self.geoip_database = None
    
    def _create_default_rules(self):
        """Create default routing rules"""
        self.routing_rules = [
            GeoRoutingRule(
                rule_id="low_latency_priority",
                name="Low Latency Priority",
                description="Prioritize providers with lowest latency",
                conditions={"latency_threshold_ms": 1000},
                actions={"strategy": "latency_optimized"},
                priority=1
            ),
            GeoRoutingRule(
                rule_id="regional_preference",
                name="Regional Preference",
                description="Prefer providers in the same region",
                conditions={"region_match": True},
                actions={"strategy": "region_preferred"},
                priority=2
            ),
            GeoRoutingRule(
                rule_id="fallback_global",
                name="Global Fallback",
                description="Use all available providers as fallback",
                conditions={"fallback": True},
                actions={"strategy": "global_fallback"},
                priority=10
            )
        ]
    
    def set_latency_monitor(self, latency_monitor: LatencyMonitor):
        """Set the latency monitor instance"""
        self.latency_monitor = latency_monitor
    
    def detect_client_location(self, ip_address: str) -> Optional[GeoLocation]:
        """Detect client location from IP address"""
        try:
            if not self.geoip_database:
                return self._fallback_location_detection(ip_address)
            
            # Parse IP address
            ip = ipaddress.ip_address(ip_address)
            
            # Skip private/local IP addresses
            if ip.is_private or ip.is_loopback:
                return self._get_default_location()
            
            # Query GeoIP database
            response = self.geoip_database.city(ip_address)
            
            return GeoLocation(
                country=response.country.name or "Unknown",
                region=response.subdivisions.most_specific.name or "Unknown",
                city=response.city.name or "Unknown",
                latitude=float(response.location.latitude or 0.0),
                longitude=float(response.location.longitude or 0.0),
                timezone=response.location.time_zone or "UTC",
                continent=response.continent.name or "Unknown"
            )
            
        except Exception as e:
            if GEOIP2_AVAILABLE and "AddressNotFoundError" in str(type(e)):
                logger.warning(f"IP address {ip_address} not found in GeoIP database")
            else:
                logger.error(f"Error detecting location for IP {ip_address}: {str(e)}")
            return self._fallback_location_detection(ip_address)
    
    def _fallback_location_detection(self, ip_address: str) -> Optional[GeoLocation]:
        """Fallback location detection using IP range analysis"""
        try:
            ip = ipaddress.ip_address(ip_address)
            
            # Simple IP range-based location detection
            if ip.is_private or ip.is_loopback:
                return self._get_default_location()
            
            # Basic continent detection based on IP ranges
            # This is a simplified approach - in production, use a proper GeoIP database
            ip_int = int(ip)
            
            # North America (rough approximation)
            if (ip_int >= int(ipaddress.ip_address('8.0.0.0')) and 
                ip_int <= int(ipaddress.ip_address('24.255.255.255'))):
                return GeoLocation(
                    country="United States",
                    region="North America",
                    city="Unknown",
                    latitude=39.0,
                    longitude=-77.0,
                    timezone="UTC-5",
                    continent="North America"
                )
            
            # Europe (rough approximation)
            elif (ip_int >= int(ipaddress.ip_address('80.0.0.0')) and 
                  ip_int <= int(ipaddress.ip_address('95.255.255.255'))):
                return GeoLocation(
                    country="Unknown",
                    region="Europe",
                    city="Unknown",
                    latitude=50.0,
                    longitude=10.0,
                    timezone="UTC+1",
                    continent="Europe"
                )
            
            # Default to North America
            return self._get_default_location()
            
        except Exception as e:
            logger.error(f"Error in fallback location detection: {str(e)}")
            return self._get_default_location()
    
    def _get_default_location(self) -> GeoLocation:
        """Get default location (North America)"""
        return GeoLocation(
            country="United States",
            region="North America",
            city="Unknown",
            latitude=39.0,
            longitude=-77.0,
            timezone="UTC-5",
            continent="North America"
        )
    
    async def route_request(self, request: GenerationRequest, 
                          client_ip: str, 
                          available_providers: List[str]) -> GeoRoutingDecision:
        """Route request based on geographic location and latency"""
        
        # Detect client location
        client_location = self.detect_client_location(client_ip)
        if not client_location:
            client_location = self._get_default_location()
        
        # Get latency statistics
        latency_stats = {}
        if self.latency_monitor:
            latency_stats = self.latency_monitor.get_all_latency_stats()
        
        # Apply routing rules
        selected_providers = []
        routing_reason = "No suitable providers found"
        confidence_score = 0.0
        rules_applied = []
        fallback_used = False
        
        # Try each routing rule in priority order
        for rule in self.routing_rules:
            if not rule.enabled:
                continue
            
            result = await self._apply_routing_rule(
                rule, client_location, available_providers, latency_stats
            )
            
            if result['providers']:
                selected_providers = result['providers']
                routing_reason = result['reason']
                confidence_score = result['confidence']
                rules_applied.append(rule.rule_id)
                
                # Check if this is a fallback rule
                if rule.rule_id == "fallback_global":
                    fallback_used = True
                
                break
        
        # If no providers selected, use fallback
        if not selected_providers:
            selected_providers = available_providers[:self.config['max_providers_per_request']]
            routing_reason = "Fallback to all available providers"
            confidence_score = 0.3
            fallback_used = True
        
        # Calculate latency considerations
        latency_considerations = {}
        for provider in selected_providers:
            if provider in latency_stats:
                latency_considerations[provider] = latency_stats[provider].avg_latency_ms
            else:
                latency_considerations[provider] = 0.0  # Unknown latency
        
        return GeoRoutingDecision(
            client_location=client_location,
            selected_providers=selected_providers,
            routing_reason=routing_reason,
            confidence_score=confidence_score,
            latency_considerations=latency_considerations,
            rules_applied=rules_applied,
            fallback_used=fallback_used
        )
    
    async def _apply_routing_rule(self, rule: GeoRoutingRule, 
                                client_location: GeoLocation,
                                available_providers: List[str],
                                latency_stats: Dict[str, LatencyStats]) -> Dict[str, Any]:
        """Apply a specific routing rule"""
        
        conditions = rule.conditions
        actions = rule.actions
        strategy = actions.get('strategy', 'default')
        
        # Check conditions
        if not self._check_rule_conditions(conditions, client_location, latency_stats):
            return {'providers': [], 'reason': 'Conditions not met', 'confidence': 0.0}
        
        # Apply strategy
        if strategy == 'latency_optimized':
            return await self._apply_latency_optimized_strategy(
                available_providers, latency_stats, client_location
            )
        elif strategy == 'region_preferred':
            return await self._apply_region_preferred_strategy(
                available_providers, client_location, latency_stats
            )
        elif strategy == 'global_fallback':
            return await self._apply_global_fallback_strategy(available_providers)
        else:
            return {'providers': [], 'reason': 'Unknown strategy', 'confidence': 0.0}
    
    def _check_rule_conditions(self, conditions: Dict[str, Any], 
                              client_location: GeoLocation,
                              latency_stats: Dict[str, LatencyStats]) -> bool:
        """Check if routing rule conditions are met"""
        
        # Check latency threshold
        if 'latency_threshold_ms' in conditions:
            threshold = conditions['latency_threshold_ms']
            has_low_latency_provider = any(
                stats.avg_latency_ms <= threshold 
                for stats in latency_stats.values()
            )
            if not has_low_latency_provider:
                return False
        
        # Check region match
        if 'region_match' in conditions and conditions['region_match']:
            client_region = client_location.continent
            has_regional_provider = any(
                client_region in self.provider_regions.get(provider, [])
                for provider in self.provider_regions.keys()
            )
            if not has_regional_provider:
                return False
        
        # Fallback condition always passes
        if 'fallback' in conditions:
            return True
        
        return True
    
    async def _apply_latency_optimized_strategy(self, available_providers: List[str],
                                              latency_stats: Dict[str, LatencyStats],
                                              client_location: GeoLocation) -> Dict[str, Any]:
        """Apply latency-optimized routing strategy"""
        
        # Score providers by latency
        provider_scores = []
        
        for provider in available_providers:
            if provider in latency_stats:
                stats = latency_stats[provider]
                # Lower latency = higher score
                latency_score = max(0, 1.0 - (stats.avg_latency_ms / 10000))
                availability_score = stats.success_rate
                
                # Combined score
                score = (latency_score * 0.7) + (availability_score * 0.3)
                provider_scores.append((provider, score))
            else:
                # Unknown latency, assign medium score
                provider_scores.append((provider, 0.5))
        
        # Sort by score (descending)
        provider_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Select top providers
        selected_providers = [
            provider for provider, score in provider_scores[:self.config['max_providers_per_request']]
        ]
        
        # Calculate confidence
        if provider_scores:
            confidence = min(1.0, provider_scores[0][1] + 0.2)
        else:
            confidence = 0.3
        
        return {
            'providers': selected_providers,
            'reason': 'Latency-optimized routing',
            'confidence': confidence
        }
    
    async def _apply_region_preferred_strategy(self, available_providers: List[str],
                                             client_location: GeoLocation,
                                             latency_stats: Dict[str, LatencyStats]) -> Dict[str, Any]:
        """Apply region-preferred routing strategy"""
        
        client_region = client_location.continent
        
        # Get regional preferences
        regional_preferences = self.region_preferences.get(client_region, [])
        
        # Score providers by region preference and latency
        provider_scores = []
        
        for provider in available_providers:
            score = 0.0
            
            # Region preference score
            if provider in regional_preferences:
                preference_index = regional_preferences.index(provider)
                region_score = 1.0 - (preference_index / len(regional_preferences))
            else:
                region_score = 0.3  # Default score for non-regional providers
            
            # Latency score
            if provider in latency_stats:
                stats = latency_stats[provider]
                latency_score = max(0, 1.0 - (stats.avg_latency_ms / 10000))
                availability_score = stats.success_rate
            else:
                latency_score = 0.5
                availability_score = 0.8
            
            # Combined score
            score = (
                region_score * self.config['region_preference_weight'] +
                latency_score * self.config['latency_weight'] +
                availability_score * self.config['availability_weight']
            )
            
            provider_scores.append((provider, score))
        
        # Sort by score (descending)
        provider_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Select top providers
        selected_providers = [
            provider for provider, score in provider_scores[:self.config['max_providers_per_request']]
        ]
        
        # Calculate confidence
        if provider_scores:
            confidence = min(1.0, provider_scores[0][1] + 0.1)
        else:
            confidence = 0.4
        
        return {
            'providers': selected_providers,
            'reason': f'Region-preferred routing for {client_region}',
            'confidence': confidence
        }
    
    async def _apply_global_fallback_strategy(self, available_providers: List[str]) -> Dict[str, Any]:
        """Apply global fallback strategy"""
        
        # Use all available providers, limited by max_providers_per_request
        selected_providers = available_providers[:self.config['max_providers_per_request']]
        
        return {
            'providers': selected_providers,
            'reason': 'Global fallback routing',
            'confidence': 0.3
        }
    
    def add_routing_rule(self, rule: GeoRoutingRule):
        """Add a new routing rule"""
        self.routing_rules.append(rule)
        self.routing_rules.sort(key=lambda x: x.priority)
        logger.info(f"Added routing rule: {rule.name}")
    
    def remove_routing_rule(self, rule_id: str):
        """Remove a routing rule"""
        self.routing_rules = [rule for rule in self.routing_rules if rule.rule_id != rule_id]
        logger.info(f"Removed routing rule: {rule_id}")
    
    def update_provider_regions(self, provider_regions: Dict[str, List[str]]):
        """Update provider region mappings"""
        self.provider_regions.update(provider_regions)
        logger.info("Updated provider region mappings")
    
    def get_geo_routing_analytics(self) -> Dict[str, Any]:
        """Get comprehensive geo routing analytics"""
        
        return {
            'configuration': self.config.copy(),
            'provider_regions': self.provider_regions.copy(),
            'region_preferences': self.region_preferences.copy(),
            'routing_rules': [rule.to_dict() for rule in self.routing_rules],
            'geoip_available': self.geoip_database is not None,
            'latency_monitor_active': self.latency_monitor is not None and self.latency_monitor.monitoring_active,
            'total_routing_rules': len(self.routing_rules),
            'enabled_routing_rules': len([rule for rule in self.routing_rules if rule.enabled])
        }
    
    def save_configuration(self):
        """Save current configuration to file"""
        try:
            config_data = {
                'routing': self.config,
                'provider_regions': self.provider_regions,
                'region_preferences': self.region_preferences,
                'routing_rules': [rule.to_dict() for rule in self.routing_rules]
            }
            
            # Ensure config directory exists
            config_file = Path(self.config_path)
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w') as f:
                yaml.dump(config_data, f, indent=2)
            
            logger.info(f"Saved geo routing configuration to {config_file}")
            
        except Exception as e:
            logger.error(f"Error saving geo routing configuration: {str(e)}")


# Global geo router instance
geo_router = GeoRouter()