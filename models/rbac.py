"""
Role-Based Access Control (RBAC) models for enterprise security
"""
from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, Text, JSON, DateTime, Index, Float
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, INET
from datetime import datetime
from models.base import BaseModel


class Role(BaseModel):
    """Role model for RBAC system"""
    __tablename__ = "roles"

    name = Column(String(100), nullable=False)
    description = Column(Text)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    is_system_role = Column(Boolean, default=False)
    permissions = Column(JSON, nullable=False)  # Stored as JSON for flexibility
    
    # Role hierarchy
    parent_role_id = Column(String(36), ForeignKey("roles.id"), nullable=True)
    
    # Relationships
    organization = relationship("Organization")
    parent_role = relationship("Role", remote_side="Role.id")
    child_roles = relationship("Role")
    user_roles = relationship("UserRole", back_populates="role")


class Permission(BaseModel):
    """Permission model for granular access control"""
    __tablename__ = "permissions"

    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    resource_type = Column(String(50), nullable=False)  # e.g., 'api_key', 'organization', 'user'
    action = Column(String(50), nullable=False)  # e.g., 'create', 'read', 'update', 'delete'
    conditions = Column(JSON)  # Additional conditions for the permission
    
    # Relationships
    role_permissions = relationship("RolePermission", back_populates="permission")


class RolePermission(BaseModel):
    """Many-to-many relationship between roles and permissions"""
    __tablename__ = "role_permissions"

    role_id = Column(String(36), ForeignKey("roles.id"), nullable=False)
    permission_id = Column(String(36), ForeignKey("permissions.id"), nullable=False)
    
    # Relationships
    role = relationship("Role")
    permission = relationship("Permission", back_populates="role_permissions")


class UserRole(BaseModel):
    """User role assignments"""
    __tablename__ = "user_roles"

    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    role_id = Column(String(36), ForeignKey("roles.id"), nullable=False)
    assigned_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User")
    role = relationship("Role", back_populates="user_roles")
    assigned_by_user = relationship("User", foreign_keys=[assigned_by])


class AuditLog(BaseModel):
    """Comprehensive audit logging for compliance"""
    __tablename__ = "audit_logs"

    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)  # Null for system actions
    action = Column(String(100), nullable=False)  # e.g., 'user.login', 'api_key.create'
    resource_type = Column(String(50), nullable=False)  # e.g., 'user', 'api_key', 'organization'
    resource_id = Column(String(255), nullable=True)  # ID of the affected resource
    
    # Change tracking
    old_values = Column(JSON)  # Previous state
    new_values = Column(JSON)  # New state
    
    # Request context
    ip_address = Column(INET)
    user_agent = Column(Text)
    session_id = Column(String(255))
    
    # Success/failure tracking
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    # Additional metadata
    additional_metadata = Column(JSON)  # Additional context
    
    # Relationships
    organization = relationship("Organization")
    user = relationship("User")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_audit_logs_org_time', 'organization_id', 'created_at'),
        Index('idx_audit_logs_user_time', 'user_id', 'created_at'),
        Index('idx_audit_logs_action', 'action'),
        Index('idx_audit_logs_resource', 'resource_type', 'resource_id'),
    )


class CostCenter(BaseModel):
    """Cost centers for enterprise billing and allocation"""
    __tablename__ = "cost_centers"

    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=False)
    description = Column(Text)
    budget_limit = Column(Integer)  # Budget in cents
    manager_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    organization = relationship("Organization")
    manager = relationship("User")
    usage_allocations = relationship("UsageAllocation", back_populates="cost_center")


class UsageAllocation(BaseModel):
    """Usage allocation to cost centers for enterprise billing"""
    __tablename__ = "usage_allocations"

    usage_record_id = Column(String(36), ForeignKey("usage_records.id"), nullable=False)
    cost_center_id = Column(String(36), ForeignKey("cost_centers.id"), nullable=False)
    department = Column(String(100))
    project_code = Column(String(50))
    allocation_percentage = Column(Integer, default=100)  # Percentage allocated to this cost center
    allocated_cost = Column(Integer)  # Cost in cents
    
    # Relationships
    usage_record = relationship("UsageRecord")
    cost_center = relationship("CostCenter", back_populates="usage_allocations")


class Workflow(BaseModel):
    """Multi-step workflow definitions"""
    __tablename__ = "workflows"

    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    definition = Column(JSON, nullable=False)  # Workflow definition
    version = Column(Integer, default=1)
    status = Column(String(20), default='draft')  # draft, active, archived
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    organization = relationship("Organization")
    created_by_user = relationship("User")
    executions = relationship("WorkflowExecution", back_populates="workflow")


class WorkflowExecution(BaseModel):
    """Workflow execution tracking"""
    __tablename__ = "workflow_executions"

    workflow_id = Column(String(36), ForeignKey("workflows.id"), nullable=False)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    input_data = Column(JSON)
    output_data = Column(JSON)
    status = Column(String(20), default='running')  # running, completed, failed, cancelled
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    execution_time_ms = Column(Integer)
    total_cost = Column(Integer)  # Cost in cents
    
    # Relationships
    workflow = relationship("Workflow", back_populates="executions")
    organization = relationship("Organization")


class ABTest(BaseModel):
    """A/B testing framework for model and provider comparison"""
    __tablename__ = "ab_tests"

    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    test_type = Column(String(50), nullable=False)  # model_comparison, provider_comparison, etc.
    variants = Column(JSON, nullable=False)  # Test variants configuration
    traffic_split = Column(JSON, nullable=False)  # Traffic distribution
    duration_days = Column(Integer, nullable=False)
    success_metrics = Column(JSON, nullable=False)  # List of metrics to track
    statistical_significance = Column(Float, default=0.05)
    status = Column(String(20), default='draft')  # draft, active, stopped, completed
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    
    # Relationships
    organization = relationship("Organization")
    created_by_user = relationship("User")
    executions = relationship("ABTestExecution", back_populates="test")
    results = relationship("ABTestResult", back_populates="test")


class ABTestExecution(BaseModel):
    """A/B test execution tracking"""
    __tablename__ = "ab_test_executions"

    test_id = Column(String(36), ForeignKey("ab_tests.id"), nullable=False)
    user_id = Column(String(255), nullable=False)  # User identifier for consistent assignment
    variant = Column(String(50), nullable=False)  # Which variant was assigned
    input_data = Column(JSON)  # Request input
    executed_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    test = relationship("ABTest", back_populates="executions")


class ABTestResult(BaseModel):
    """A/B test results collection"""
    __tablename__ = "ab_test_results"

    test_id = Column(String(36), ForeignKey("ab_tests.id"), nullable=False)
    variant = Column(String(50), nullable=False)
    metrics = Column(JSON, nullable=False)  # Collected metrics
    success = Column(Boolean, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    test = relationship("ABTest", back_populates="results")


# System permissions for initialization
SYSTEM_PERMISSIONS = [
    # User management
    {"name": "user.create", "description": "Create users", "resource_type": "user", "action": "create"},
    {"name": "user.read", "description": "Read user information", "resource_type": "user", "action": "read"},
    {"name": "user.update", "description": "Update user information", "resource_type": "user", "action": "update"},
    {"name": "user.delete", "description": "Delete users", "resource_type": "user", "action": "delete"},
    
    # API Key management
    {"name": "api_key.create", "description": "Create API keys", "resource_type": "api_key", "action": "create"},
    {"name": "api_key.read", "description": "Read API key information", "resource_type": "api_key", "action": "read"},
    {"name": "api_key.update", "description": "Update API keys", "resource_type": "api_key", "action": "update"},
    {"name": "api_key.delete", "description": "Delete API keys", "resource_type": "api_key", "action": "delete"},
    
    # Organization management
    {"name": "organization.read", "description": "Read organization information", "resource_type": "organization", "action": "read"},
    {"name": "organization.update", "description": "Update organization settings", "resource_type": "organization", "action": "update"},
    
    # Usage and analytics
    {"name": "usage.read", "description": "Read usage analytics", "resource_type": "usage", "action": "read"},
    {"name": "analytics.read", "description": "Read analytics data", "resource_type": "analytics", "action": "read"},
    
    # Billing management
    {"name": "billing.read", "description": "Read billing information", "resource_type": "billing", "action": "read"},
    {"name": "billing.update", "description": "Update billing settings", "resource_type": "billing", "action": "update"},
    
    # Workflow management
    {"name": "workflow.create", "description": "Create workflows", "resource_type": "workflow", "action": "create"},
    {"name": "workflow.read", "description": "Read workflow information", "resource_type": "workflow", "action": "read"},
    {"name": "workflow.update", "description": "Update workflows", "resource_type": "workflow", "action": "update"},
    {"name": "workflow.delete", "description": "Delete workflows", "resource_type": "workflow", "action": "delete"},
    {"name": "workflow.execute", "description": "Execute workflows", "resource_type": "workflow", "action": "execute"},
    
    # Cost center management
    {"name": "cost_center.create", "description": "Create cost centers", "resource_type": "cost_center", "action": "create"},
    {"name": "cost_center.read", "description": "Read cost center information", "resource_type": "cost_center", "action": "read"},
    {"name": "cost_center.update", "description": "Update cost centers", "resource_type": "cost_center", "action": "update"},
    {"name": "cost_center.delete", "description": "Delete cost centers", "resource_type": "cost_center", "action": "delete"},
    
    # Role management
    {"name": "role.create", "description": "Create roles", "resource_type": "role", "action": "create"},
    {"name": "role.read", "description": "Read role information", "resource_type": "role", "action": "read"},
    {"name": "role.update", "description": "Update roles", "resource_type": "role", "action": "update"},
    {"name": "role.delete", "description": "Delete roles", "resource_type": "role", "action": "delete"},
    {"name": "role.assign", "description": "Assign roles to users", "resource_type": "role", "action": "assign"},
    
    # Audit logs
    {"name": "audit_log.read", "description": "Read audit logs", "resource_type": "audit_log", "action": "read"},
    
    # LLM API access
    {"name": "llm.generate", "description": "Generate text using LLM", "resource_type": "llm", "action": "generate"},
    {"name": "llm.models.read", "description": "Read available models", "resource_type": "llm", "action": "read_models"},
    
    # A/B Testing
    {"name": "ab_testing.create", "description": "Create A/B tests", "resource_type": "ab_testing", "action": "create"},
    {"name": "ab_testing.read", "description": "Read A/B test information", "resource_type": "ab_testing", "action": "read"},
    {"name": "ab_testing.update", "description": "Update A/B tests", "resource_type": "ab_testing", "action": "update"},
    {"name": "ab_testing.delete", "description": "Delete A/B tests", "resource_type": "ab_testing", "action": "delete"},
    {"name": "ab_testing.execute", "description": "Execute A/B tests", "resource_type": "ab_testing", "action": "execute"},
    
    # SSO
    {"name": "sso.configure", "description": "Configure SSO providers", "resource_type": "sso", "action": "configure"},
    {"name": "sso.read", "description": "Read SSO configuration", "resource_type": "sso", "action": "read"},
    
    # MFA
    {"name": "mfa.setup", "description": "Setup MFA for users", "resource_type": "mfa", "action": "setup"},
    {"name": "mfa.verify", "description": "Verify MFA codes", "resource_type": "mfa", "action": "verify"},
]

# System roles for initialization
SYSTEM_ROLES = [
    {
        "name": "Owner",
        "description": "Full access to all features",
        "is_system_role": True,
        "permissions": ["*"]  # All permissions
    },
    {
        "name": "Admin",
        "description": "Administrative access to most features",
        "is_system_role": True,
        "permissions": [
            "user.create", "user.read", "user.update", "user.delete",
            "api_key.create", "api_key.read", "api_key.update", "api_key.delete",
            "organization.read", "organization.update",
            "usage.read", "analytics.read",
            "billing.read", "billing.update",
            "workflow.create", "workflow.read", "workflow.update", "workflow.delete", "workflow.execute",
            "cost_center.create", "cost_center.read", "cost_center.update", "cost_center.delete",
            "role.create", "role.read", "role.update", "role.delete", "role.assign",
            "audit_log.read",
            "llm.generate", "llm.models.read"
        ]
    },
    {
        "name": "Member",
        "description": "Standard user access",
        "is_system_role": True,
        "permissions": [
            "user.read", "user.update",
            "api_key.create", "api_key.read", "api_key.update", "api_key.delete",
            "organization.read",
            "usage.read", "analytics.read",
            "billing.read",
            "workflow.read", "workflow.execute",
            "cost_center.read",
            "llm.generate", "llm.models.read"
        ]
    },
    {
        "name": "Viewer",
        "description": "Read-only access",
        "is_system_role": True,
        "permissions": [
            "user.read",
            "api_key.read",
            "organization.read",
            "usage.read", "analytics.read",
            "billing.read",
            "workflow.read",
            "cost_center.read",
            "llm.models.read"
        ]
    }
]