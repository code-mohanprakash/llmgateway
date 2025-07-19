"""
Monitoring and alerting models for enterprise infrastructure
"""
from sqlalchemy import Column, String, Text, Integer, JSON, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from models.base import BaseModel


class SystemHealth(BaseModel):
    """System health monitoring data"""
    __tablename__ = "system_health"

    # Health metrics
    cpu_usage = Column(Float, nullable=False)  # CPU usage percentage
    memory_usage = Column(Float, nullable=False)  # Memory usage percentage
    disk_usage = Column(Float, nullable=False)  # Disk usage percentage
    network_latency = Column(Float, nullable=False)  # Network latency in ms
    response_time = Column(Float, nullable=False)  # Average API response time
    
    # System status
    status = Column(String(20), nullable=False)  # healthy, warning, critical
    uptime_seconds = Column(Integer, nullable=False)  # System uptime
    
    # Additional metrics
    active_connections = Column(Integer, default=0)
    error_rate = Column(Float, default=0.0)  # Error rate percentage
    throughput = Column(Float, default=0.0)  # Requests per second
    
    # Timestamp
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=True)
    organization = relationship("Organization")


class PerformanceMetric(BaseModel):
    """Performance metrics tracking"""
    __tablename__ = "performance_metrics"

    # Metric identification
    metric_name = Column(String(100), nullable=False)  # e.g., 'api_response_time'
    metric_type = Column(String(50), nullable=False)  # gauge, counter, histogram
    
    # Metric values
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)  # ms, %, count, etc.
    
    # Context
    endpoint = Column(String(200))  # API endpoint
    method = Column(String(10))  # HTTP method
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=True)
    
    # Timestamp
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User")
    organization = relationship("Organization")


class Alert(BaseModel):
    """Alert system for monitoring"""
    __tablename__ = "alerts"

    # Alert identification
    alert_type = Column(String(50), nullable=False)  # system, performance, security
    severity = Column(String(20), nullable=False)  # info, warning, critical, emergency
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    # Alert status
    status = Column(String(20), default='active')  # active, acknowledged, resolved
    acknowledged_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    
    # Alert metadata
    source = Column(String(100), nullable=False)  # system component
    metric_name = Column(String(100))  # related metric
    threshold_value = Column(Float)  # threshold that triggered alert
    current_value = Column(Float)  # current value
    
    # Notification
    notification_sent = Column(Boolean, default=False)
    notification_channels = Column(JSON, default=list)  # email, slack, webhook
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=True)
    organization = relationship("Organization")
    acknowledged_by_user = relationship("User")


class SLAMetric(BaseModel):
    """SLA compliance tracking"""
    __tablename__ = "sla_metrics"

    # SLA identification
    sla_name = Column(String(100), nullable=False)  # e.g., 'api_uptime'
    sla_target = Column(Float, nullable=False)  # target percentage (99.99)
    sla_period = Column(String(20), nullable=False)  # daily, weekly, monthly
    
    # Current performance
    current_value = Column(Float, nullable=False)  # current performance
    compliance_percentage = Column(Float, nullable=False)  # compliance percentage
    
    # Status
    status = Column(String(20), nullable=False)  # compliant, at_risk, non_compliant
    
    # Timestamp
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=True)
    organization = relationship("Organization")


class Incident(BaseModel):
    """Incident management"""
    __tablename__ = "incidents"

    # Incident identification
    incident_type = Column(String(50), nullable=False)  # outage, performance, security
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    # Incident status
    status = Column(String(20), default='open')  # open, investigating, resolved, closed
    priority = Column(String(20), nullable=False)  # low, medium, high, urgent
    
    # Incident details
    affected_services = Column(JSON, default=list)  # List of affected services
    impact_level = Column(String(20), nullable=False)  # minimal, moderate, significant, severe
    
    # Resolution
    root_cause = Column(Text)
    resolution = Column(Text)
    resolved_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    
    # Timestamps
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=True)
    organization = relationship("Organization")
    resolved_by_user = relationship("User")


class MonitoringConfig(BaseModel):
    """Monitoring configuration"""
    __tablename__ = "monitoring_config"

    # Configuration
    config_name = Column(String(100), nullable=False, unique=True)
    config_type = Column(String(50), nullable=False)  # alert, sla, performance
    
    # Alert thresholds
    cpu_warning_threshold = Column(Float, default=80.0)
    cpu_critical_threshold = Column(Float, default=95.0)
    memory_warning_threshold = Column(Float, default=80.0)
    memory_critical_threshold = Column(Float, default=95.0)
    response_time_warning_threshold = Column(Float, default=1000.0)  # ms
    response_time_critical_threshold = Column(Float, default=5000.0)  # ms
    
    # SLA targets
    uptime_target = Column(Float, default=99.99)
    response_time_target = Column(Float, default=100.0)  # ms
    
    # Notification settings
    email_notifications = Column(Boolean, default=True)
    slack_notifications = Column(Boolean, default=False)
    webhook_notifications = Column(Boolean, default=False)
    notification_recipients = Column(JSON, default=list)
    
    # Timestamp
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=True)
    organization = relationship("Organization") 