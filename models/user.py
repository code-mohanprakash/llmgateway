"""
User and organization models for multi-tenancy
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, Text, JSON, Enum, Numeric, DateTime
from sqlalchemy.orm import relationship
import enum
from models.base import BaseModel


class UserRole(enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class PlanType(enum.Enum):
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class Organization(BaseModel):
    """Organization model for multi-tenancy"""
    __tablename__ = "organizations"

    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    website = Column(String(255))
    
    # Billing information
    plan_type = Column(Enum(PlanType), default=PlanType.FREE, nullable=False)
    stripe_customer_id = Column(String(255), unique=True)
    stripe_subscription_id = Column(String(255))
    
    # Usage limits
    monthly_request_limit = Column(Integer, default=1000)
    monthly_token_limit = Column(Integer, default=50000)
    
    # Features
    features = Column(JSON, default=dict)
    
    # Settings
    settings = Column(JSON, default=dict)
    
    # Relationships
    users = relationship("User", back_populates="organization")
    api_keys = relationship("APIKey", back_populates="organization")
    usage_records = relationship("UsageRecord", back_populates="organization")


class User(BaseModel):
    """User model"""
    __tablename__ = "users"

    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Organization relationship
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.MEMBER, nullable=False)
    
    # Profile
    avatar_url = Column(String(500))
    timezone = Column(String(50), default="UTC")
    preferences = Column(JSON, default=dict)
    
    # Login tracking
    last_login_at = Column(DateTime, nullable=True)
    
    # Password reset
    reset_token = Column(String(100), nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    
    # Email verification
    verification_token = Column(String(100), nullable=True)
    verification_token_expires = Column(DateTime, nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="users")
    api_keys = relationship("APIKey", back_populates="user")
    user_roles = relationship("UserRole", foreign_keys="UserRole.user_id", back_populates="user")


class APIKey(BaseModel):
    """API Key model for authentication"""
    __tablename__ = "api_keys"

    name = Column(String(255), nullable=False)
    key_hash = Column(String(255), unique=True, nullable=False)
    key_prefix = Column(String(20), nullable=False)  # For display purposes
    
    # Permissions
    is_active = Column(Boolean, default=True)
    scopes = Column(JSON, default=list)  # List of allowed scopes
    
    # Rate limiting
    rate_limit_per_minute = Column(Integer, default=60)
    rate_limit_per_hour = Column(Integer, default=1000)
    rate_limit_per_day = Column(Integer, default=10000)
    
    # Usage tracking
    last_used_at = Column(DateTime, nullable=True)
    usage_count = Column(Integer, default=0)
    
    # Relationships
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    
    user = relationship("User", back_populates="api_keys")
    organization = relationship("Organization", back_populates="api_keys")


class UsageRecord(BaseModel):
    """Usage tracking for billing and analytics"""
    __tablename__ = "usage_records"

    # Request information
    request_id = Column(String(255), unique=True, nullable=False)
    api_key_id = Column(String(36), ForeignKey("api_keys.id"), nullable=False)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    
    # Model information
    provider = Column(String(100), nullable=False)
    model_id = Column(String(255), nullable=False)
    model_alias = Column(String(100))
    
    # Usage metrics
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    
    # Cost information
    cost_usd = Column(Numeric(10, 6), default=0)
    markup_usd = Column(Numeric(10, 6), default=0)
    
    # Performance metrics
    response_time_ms = Column(Integer)
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    # Request metadata
    user_agent = Column(String(500))
    ip_address = Column(String(45))
    task_type = Column(String(100))
    complexity = Column(String(50))
    
    # Relationships
    organization = relationship("Organization", back_populates="usage_records")


class BillingRecord(BaseModel):
    """Billing records for invoicing"""
    __tablename__ = "billing_records"

    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    
    # Billing period
    billing_period_start = Column(String, nullable=False)
    billing_period_end = Column(String, nullable=False)
    
    # Usage summary
    total_requests = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    total_cost_usd = Column(Numeric(10, 2), default=0)
    
    # Stripe information
    stripe_invoice_id = Column(String(255))
    stripe_payment_intent_id = Column(String(255))
    
    # Status
    status = Column(String(50), default="pending")  # pending, paid, failed
    paid_at = Column(String)
    
    # Relationships
    organization = relationship("Organization")