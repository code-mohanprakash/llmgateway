"""
Budget Manager - Phase 2.2: Budget Management System
Manages organization budgets, tracking, alerts, and throttling.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

logger = logging.getLogger(__name__)


class BudgetPeriod(Enum):
    """Budget period types."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class BudgetStatus(Enum):
    """Budget status types."""
    ACTIVE = "active"
    WARNING = "warning"
    EXCEEDED = "exceeded"
    PAUSED = "paused"


class AlertType(Enum):
    """Budget alert types."""
    THRESHOLD_WARNING = "threshold_warning"
    BUDGET_EXCEEDED = "budget_exceeded"
    PROJECTION_ALERT = "projection_alert"
    THROTTLING_ENABLED = "throttling_enabled"


@dataclass
class BudgetConfig:
    """Budget configuration for an organization."""
    organization_id: str
    total_budget: float
    period: BudgetPeriod
    start_date: datetime
    end_date: datetime
    alert_thresholds: List[float]  # Percentage thresholds (e.g., [75, 90, 95])
    auto_throttle: bool
    throttle_threshold: float  # Percentage at which to start throttling
    model_allocations: Dict[str, float]  # model_id -> budget allocation
    provider_allocations: Dict[str, float]  # provider -> budget allocation
    created_at: datetime
    updated_at: datetime


@dataclass
class BudgetUsage:
    """Budget usage tracking."""
    organization_id: str
    period_start: datetime
    period_end: datetime
    total_spent: float
    total_budget: float
    usage_percentage: float
    model_usage: Dict[str, float]  # model_id -> spent amount
    provider_usage: Dict[str, float]  # provider -> spent amount
    request_count: int
    token_count: int
    status: BudgetStatus
    last_updated: datetime


@dataclass
class BudgetAlert:
    """Budget alert information."""
    alert_id: str
    organization_id: str
    alert_type: AlertType
    threshold_percentage: float
    current_usage: float
    budget_amount: float
    message: str
    triggered_at: datetime
    acknowledged: bool = False


@dataclass
class BudgetProjection:
    """Budget projection based on current usage."""
    organization_id: str
    current_usage: float
    projected_usage: float
    projected_overage: float
    days_remaining: int
    burn_rate: float  # Spending per day
    projected_end_date: datetime
    confidence: float  # 0.0 to 1.0


class BudgetManager:
    """
    Advanced budget management with tracking, alerts, and projections.
    
    Chain of thought:
    1. Track spending across models and providers
    2. Calculate usage against budget allocations
    3. Generate alerts at configurable thresholds
    4. Project future spending based on current trends
    5. Support throttling when budget limits approached
    """
    
    def __init__(self, db_session: AsyncSession):
        """Initialize budget manager with database session."""
        self.logger = logging.getLogger(__name__)
        self.db = db_session
        
        # In-memory cache for active budgets
        self.budget_cache: Dict[str, BudgetConfig] = {}
        self.usage_cache: Dict[str, BudgetUsage] = {}
        
        # Alert tracking
        self.pending_alerts: List[BudgetAlert] = []
        
        # Projection settings
        self.projection_window_days = 7  # Use last 7 days for projection
        self.min_data_points = 3  # Minimum data points for reliable projection
        
        self.logger.info("BudgetManager initialized")
    
    async def create_budget(self, config: BudgetConfig) -> bool:
        """
        Create a new budget configuration.
        
        Args:
            config: Budget configuration object
            
        Returns:
            True if budget created successfully
        """
        try:
            # Validate budget configuration
            if not self._validate_budget_config(config):
                raise ValueError("Invalid budget configuration")
            
            # Store in database (implementation depends on your ORM)
            await self._store_budget_config(config)
            
            # Update cache
            self.budget_cache[config.organization_id] = config
            
            # Initialize usage tracking
            usage = BudgetUsage(
                organization_id=config.organization_id,
                period_start=config.start_date,
                period_end=config.end_date,
                total_spent=0.0,
                total_budget=config.total_budget,
                usage_percentage=0.0,
                model_usage={},
                provider_usage={},
                request_count=0,
                token_count=0,
                status=BudgetStatus.ACTIVE,
                last_updated=datetime.now()
            )
            
            self.usage_cache[config.organization_id] = usage
            
            self.logger.info(f"Created budget for organization {config.organization_id}: ${config.total_budget}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating budget for {config.organization_id}: {str(e)}")
            return False
    
    async def update_budget(self, organization_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update budget configuration.
        
        Args:
            organization_id: Organization identifier
            updates: Dictionary of fields to update
            
        Returns:
            True if budget updated successfully
        """
        try:
            if organization_id not in self.budget_cache:
                await self._load_budget_config(organization_id)
            
            if organization_id not in self.budget_cache:
                raise ValueError(f"Budget not found for organization {organization_id}")
            
            config = self.budget_cache[organization_id]
            
            # Update fields
            for field, value in updates.items():
                if hasattr(config, field):
                    setattr(config, field, value)
            
            config.updated_at = datetime.now()
            
            # Validate updated configuration
            if not self._validate_budget_config(config):
                raise ValueError("Invalid budget configuration after update")
            
            # Store in database
            await self._store_budget_config(config)
            
            self.logger.info(f"Updated budget for organization {organization_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating budget for {organization_id}: {str(e)}")
            return False
    
    async def record_usage(
        self,
        organization_id: str,
        cost: float,
        model_id: str,
        provider: str,
        tokens: int
    ) -> bool:
        """
        Record usage against budget.
        
        Args:
            organization_id: Organization identifier
            cost: Cost of the request
            model_id: Model used
            provider: Provider used
            tokens: Number of tokens used
            
        Returns:
            True if usage recorded successfully
        """
        try:
            # Load budget and usage if not cached
            if organization_id not in self.budget_cache:
                await self._load_budget_config(organization_id)
            
            if organization_id not in self.usage_cache:
                await self._load_usage_data(organization_id)
            
            if organization_id not in self.budget_cache:
                self.logger.warning(f"No budget found for organization {organization_id}")
                return False
            
            usage = self.usage_cache[organization_id]
            
            # Update usage
            usage.total_spent += cost
            usage.request_count += 1
            usage.token_count += tokens
            usage.last_updated = datetime.now()
            
            # Update model usage
            if model_id not in usage.model_usage:
                usage.model_usage[model_id] = 0.0
            usage.model_usage[model_id] += cost
            
            # Update provider usage
            if provider not in usage.provider_usage:
                usage.provider_usage[provider] = 0.0
            usage.provider_usage[provider] += cost
            
            # Calculate usage percentage
            usage.usage_percentage = (usage.total_spent / usage.total_budget) * 100
            
            # Update status
            usage.status = self._calculate_budget_status(usage)
            
            # Store in database
            await self._store_usage_data(usage)
            
            # Check for alerts
            await self._check_budget_alerts(organization_id, usage)
            
            self.logger.debug(f"Recorded usage for {organization_id}: ${cost:.6f}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error recording usage for {organization_id}: {str(e)}")
            return False
    
    async def get_budget_status(self, organization_id: str) -> Optional[BudgetUsage]:
        """
        Get current budget status.
        
        Args:
            organization_id: Organization identifier
            
        Returns:
            BudgetUsage object with current status
        """
        try:
            if organization_id not in self.usage_cache:
                await self._load_usage_data(organization_id)
            
            return self.usage_cache.get(organization_id)
            
        except Exception as e:
            self.logger.error(f"Error getting budget status for {organization_id}: {str(e)}")
            return None
    
    async def get_budget_projection(self, organization_id: str) -> Optional[BudgetProjection]:
        """
        Get budget projection based on current usage trends.
        
        Args:
            organization_id: Organization identifier
            
        Returns:
            BudgetProjection object with forecast
        """
        try:
            usage = await self.get_budget_status(organization_id)
            if not usage:
                return None
            
            # Get historical usage data
            historical_data = await self._get_historical_usage(organization_id)
            
            if len(historical_data) < self.min_data_points:
                self.logger.warning(f"Insufficient data for projection: {len(historical_data)} points")
                return None
            
            # Calculate burn rate
            burn_rate = self._calculate_burn_rate(historical_data)
            
            # Calculate remaining days in period
            days_remaining = (usage.period_end - datetime.now()).days
            
            # Project future usage
            projected_usage = usage.total_spent + (burn_rate * days_remaining)
            projected_overage = max(0, projected_usage - usage.total_budget)
            
            # Calculate confidence based on data consistency
            confidence = self._calculate_projection_confidence(historical_data)
            
            # Calculate projected end date (when budget will be exhausted)
            remaining_budget = usage.total_budget - usage.total_spent
            if burn_rate > 0:
                days_to_exhaustion = remaining_budget / burn_rate
                projected_end_date = datetime.now() + timedelta(days=days_to_exhaustion)
            else:
                projected_end_date = usage.period_end
            
            projection = BudgetProjection(
                organization_id=organization_id,
                current_usage=usage.total_spent,
                projected_usage=projected_usage,
                projected_overage=projected_overage,
                days_remaining=days_remaining,
                burn_rate=burn_rate,
                projected_end_date=projected_end_date,
                confidence=confidence
            )
            
            # Generate projection alert if needed
            if projected_overage > 0 and confidence > 0.7:
                await self._generate_projection_alert(organization_id, projection)
            
            return projection
            
        except Exception as e:
            self.logger.error(f"Error calculating budget projection for {organization_id}: {str(e)}")
            return None
    
    async def check_budget_allowance(self, organization_id: str, estimated_cost: float) -> Dict[str, Any]:
        """
        Check if request is within budget allowance.
        
        Args:
            organization_id: Organization identifier
            estimated_cost: Estimated cost of the request
            
        Returns:
            Dictionary with allowance status and throttling info
        """
        try:
            usage = await self.get_budget_status(organization_id)
            if not usage:
                return {"allowed": True, "reason": "no_budget_configured"}
            
            config = self.budget_cache.get(organization_id)
            if not config:
                return {"allowed": True, "reason": "no_config_found"}
            
            # Calculate potential new usage
            potential_usage = usage.total_spent + estimated_cost
            potential_percentage = (potential_usage / usage.total_budget) * 100
            
            # Check if budget would be exceeded
            if potential_percentage > 100:
                return {
                    "allowed": False,
                    "reason": "budget_exceeded",
                    "current_usage": usage.usage_percentage,
                    "potential_usage": potential_percentage,
                    "remaining_budget": usage.total_budget - usage.total_spent
                }
            
            # Check throttling threshold
            if config.auto_throttle and potential_percentage > config.throttle_threshold:
                return {
                    "allowed": False,
                    "reason": "throttling_enabled",
                    "current_usage": usage.usage_percentage,
                    "potential_usage": potential_percentage,
                    "throttle_threshold": config.throttle_threshold
                }
            
            return {
                "allowed": True,
                "current_usage": usage.usage_percentage,
                "potential_usage": potential_percentage,
                "remaining_budget": usage.total_budget - usage.total_spent
            }
            
        except Exception as e:
            self.logger.error(f"Error checking budget allowance for {organization_id}: {str(e)}")
            return {"allowed": True, "reason": "error_occurred"}
    
    async def get_pending_alerts(self, organization_id: str) -> List[BudgetAlert]:
        """Get pending budget alerts for organization."""
        return [alert for alert in self.pending_alerts if alert.organization_id == organization_id]
    
    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge a budget alert."""
        for alert in self.pending_alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                return True
        return False
    
    def _validate_budget_config(self, config: BudgetConfig) -> bool:
        """Validate budget configuration."""
        if config.total_budget <= 0:
            return False
        
        if config.end_date <= config.start_date:
            return False
        
        if not config.alert_thresholds or any(t <= 0 or t > 100 for t in config.alert_thresholds):
            return False
        
        if config.throttle_threshold <= 0 or config.throttle_threshold > 100:
            return False
        
        return True
    
    def _calculate_budget_status(self, usage: BudgetUsage) -> BudgetStatus:
        """Calculate budget status based on usage."""
        if usage.usage_percentage >= 100:
            return BudgetStatus.EXCEEDED
        elif usage.usage_percentage >= 90:
            return BudgetStatus.WARNING
        else:
            return BudgetStatus.ACTIVE
    
    def _calculate_burn_rate(self, historical_data: List[Tuple[datetime, float]]) -> float:
        """Calculate daily burn rate from historical data."""
        if len(historical_data) < 2:
            return 0.0
        
        # Sort by date
        historical_data.sort(key=lambda x: x[0])
        
        # Calculate daily spending
        daily_spending = []
        for i in range(1, len(historical_data)):
            days_diff = (historical_data[i][0] - historical_data[i-1][0]).days
            if days_diff > 0:
                cost_diff = historical_data[i][1] - historical_data[i-1][1]
                daily_rate = cost_diff / days_diff
                daily_spending.append(daily_rate)
        
        # Return average daily spending
        return sum(daily_spending) / len(daily_spending) if daily_spending else 0.0
    
    def _calculate_projection_confidence(self, historical_data: List[Tuple[datetime, float]]) -> float:
        """Calculate confidence level for projections."""
        if len(historical_data) < 3:
            return 0.5
        
        # Calculate variance in spending patterns
        daily_rates = []
        for i in range(1, len(historical_data)):
            days_diff = (historical_data[i][0] - historical_data[i-1][0]).days
            if days_diff > 0:
                cost_diff = historical_data[i][1] - historical_data[i-1][1]
                daily_rate = cost_diff / days_diff
                daily_rates.append(daily_rate)
        
        if len(daily_rates) < 2:
            return 0.5
        
        # Calculate coefficient of variation
        mean_rate = sum(daily_rates) / len(daily_rates)
        variance = sum((rate - mean_rate) ** 2 for rate in daily_rates) / len(daily_rates)
        std_dev = variance ** 0.5
        
        if mean_rate == 0:
            return 0.5
        
        cv = std_dev / mean_rate
        
        # Convert to confidence (lower variation = higher confidence)
        confidence = max(0.3, min(0.95, 1.0 - cv))
        
        return confidence
    
    async def _check_budget_alerts(self, organization_id: str, usage: BudgetUsage):
        """Check and generate budget alerts."""
        config = self.budget_cache.get(organization_id)
        if not config:
            return
        
        # Check threshold alerts
        for threshold in config.alert_thresholds:
            if usage.usage_percentage >= threshold:
                alert_id = f"{organization_id}_{threshold}_{datetime.now().strftime('%Y%m%d')}"
                
                # Check if alert already exists
                existing_alert = any(
                    alert.alert_id == alert_id for alert in self.pending_alerts
                )
                
                if not existing_alert:
                    alert = BudgetAlert(
                        alert_id=alert_id,
                        organization_id=organization_id,
                        alert_type=AlertType.THRESHOLD_WARNING,
                        threshold_percentage=threshold,
                        current_usage=usage.total_spent,
                        budget_amount=usage.total_budget,
                        message=f"Budget usage has reached {threshold}% ({usage.usage_percentage:.1f}%)",
                        triggered_at=datetime.now()
                    )
                    
                    self.pending_alerts.append(alert)
                    self.logger.warning(f"Budget alert triggered for {organization_id}: {alert.message}")
        
        # Check budget exceeded alert
        if usage.usage_percentage >= 100:
            alert_id = f"{organization_id}_exceeded_{datetime.now().strftime('%Y%m%d')}"
            
            existing_alert = any(
                alert.alert_id == alert_id for alert in self.pending_alerts
            )
            
            if not existing_alert:
                alert = BudgetAlert(
                    alert_id=alert_id,
                    organization_id=organization_id,
                    alert_type=AlertType.BUDGET_EXCEEDED,
                    threshold_percentage=100,
                    current_usage=usage.total_spent,
                    budget_amount=usage.total_budget,
                    message=f"Budget has been exceeded: ${usage.total_spent:.2f} of ${usage.total_budget:.2f}",
                    triggered_at=datetime.now()
                )
                
                self.pending_alerts.append(alert)
                self.logger.error(f"Budget exceeded alert for {organization_id}: {alert.message}")
    
    async def _generate_projection_alert(self, organization_id: str, projection: BudgetProjection):
        """Generate projection-based alert."""
        if projection.projected_overage <= 0:
            return
        
        alert_id = f"{organization_id}_projection_{datetime.now().strftime('%Y%m%d')}"
        
        existing_alert = any(
            alert.alert_id == alert_id for alert in self.pending_alerts
        )
        
        if not existing_alert:
            alert = BudgetAlert(
                alert_id=alert_id,
                organization_id=organization_id,
                alert_type=AlertType.PROJECTION_ALERT,
                threshold_percentage=100,
                current_usage=projection.current_usage,
                budget_amount=projection.projected_usage,
                message=f"Projected to exceed budget by ${projection.projected_overage:.2f} (confidence: {projection.confidence:.1%})",
                triggered_at=datetime.now()
            )
            
            self.pending_alerts.append(alert)
            self.logger.warning(f"Projection alert for {organization_id}: {alert.message}")
    
    async def _store_budget_config(self, config: BudgetConfig):
        """Store budget configuration in database."""
        # Implementation depends on your database schema
        pass
    
    async def _store_usage_data(self, usage: BudgetUsage):
        """Store usage data in database."""
        # Implementation depends on your database schema
        pass
    
    async def _load_budget_config(self, organization_id: str):
        """Load budget configuration from database."""
        # Implementation depends on your database schema
        pass
    
    async def _load_usage_data(self, organization_id: str):
        """Load usage data from database."""
        # Implementation depends on your database schema
        pass
    
    async def _get_historical_usage(self, organization_id: str) -> List[Tuple[datetime, float]]:
        """Get historical usage data for projections."""
        # Implementation depends on your database schema
        # Return list of (date, cumulative_cost) tuples
        return []
    
    def get_budget_stats(self) -> Dict[str, Any]:
        """Get budget manager statistics."""
        return {
            "active_budgets": len(self.budget_cache),
            "pending_alerts": len(self.pending_alerts),
            "total_organizations": len(self.usage_cache),
            "alert_types": {
                alert_type.value: len([
                    alert for alert in self.pending_alerts 
                    if alert.alert_type == alert_type
                ])
                for alert_type in AlertType
            }
        }