#!/usr/bin/env python3
"""
Initialize RBAC system with default roles and permissions
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db, async_engine
from models.rbac import Role, Permission, UserRole, AuditLog
from models.user import User, Organization, UserRole as UserRoleEnum
from sqlalchemy import select
from datetime import datetime

# Default permissions for the system
DEFAULT_PERMISSIONS = [
    # User management
    {"name": "user.read", "description": "Read user information", "resource_type": "user", "action": "read"},
    {"name": "user.create", "description": "Create new users", "resource_type": "user", "action": "create"},
    {"name": "user.update", "description": "Update user information", "resource_type": "user", "action": "update"},
    {"name": "user.delete", "description": "Delete users", "resource_type": "user", "action": "delete"},
    
    # API Key management
    {"name": "api_key.read", "description": "Read API keys", "resource_type": "api_key", "action": "read"},
    {"name": "api_key.create", "description": "Create API keys", "resource_type": "api_key", "action": "create"},
    {"name": "api_key.update", "description": "Update API keys", "resource_type": "api_key", "action": "update"},
    {"name": "api_key.delete", "description": "Delete API keys", "resource_type": "api_key", "action": "delete"},
    
    # Organization management
    {"name": "organization.read", "description": "Read organization information", "resource_type": "organization", "action": "read"},
    {"name": "organization.update", "description": "Update organization settings", "resource_type": "organization", "action": "update"},
    
    # Analytics and dashboard
    {"name": "analytics.read", "description": "Read analytics data", "resource_type": "analytics", "action": "read"},
    {"name": "analytics.executive", "description": "Access executive dashboard", "resource_type": "analytics", "action": "executive"},
    
    # Usage tracking
    {"name": "usage.read", "description": "Read usage data", "resource_type": "usage", "action": "read"},
    
    # Billing
    {"name": "billing.read", "description": "Read billing information", "resource_type": "billing", "action": "read"},
    {"name": "billing.update", "description": "Update billing settings", "resource_type": "billing", "action": "update"},
    
    # LLM operations
    {"name": "llm.generate", "description": "Generate text with LLM", "resource_type": "llm", "action": "generate"},
    {"name": "llm.models.read", "description": "Read available models", "resource_type": "llm", "action": "models.read"},
    
    # Role management
    {"name": "role.read", "description": "Read roles", "resource_type": "role", "action": "read"},
    {"name": "role.create", "description": "Create roles", "resource_type": "role", "action": "create"},
    {"name": "role.update", "description": "Update roles", "resource_type": "role", "action": "update"},
    {"name": "role.delete", "description": "Delete roles", "resource_type": "role", "action": "delete"},
    {"name": "role.assign", "description": "Assign roles to users", "resource_type": "role", "action": "assign"},
    
    # Audit logging
    {"name": "audit_log.read", "description": "Read audit logs", "resource_type": "audit_log", "action": "read"},
    
    # Admin operations
    {"name": "admin.stats.read", "description": "Read admin statistics", "resource_type": "admin", "action": "stats.read"},
    {"name": "admin.users.read", "description": "Read admin user list", "resource_type": "admin", "action": "users.read"},
    {"name": "admin.users.update", "description": "Update admin user settings", "resource_type": "admin", "action": "users.update"},
    {"name": "admin.users.delete", "description": "Delete admin users", "resource_type": "admin", "action": "users.delete"},
    
    # A/B Testing
    {"name": "ab_testing.read", "description": "Read A/B tests", "resource_type": "ab_testing", "action": "read"},
    {"name": "ab_testing.create", "description": "Create A/B tests", "resource_type": "ab_testing", "action": "create"},
    {"name": "ab_testing.update", "description": "Update A/B tests", "resource_type": "ab_testing", "action": "update"},
    {"name": "ab_testing.delete", "description": "Delete A/B tests", "resource_type": "ab_testing", "action": "delete"},
    
    # Cost center management
    {"name": "cost_center.read", "description": "Read cost centers", "resource_type": "cost_center", "action": "read"},
    {"name": "cost_center.create", "description": "Create cost centers", "resource_type": "cost_center", "action": "create"},
    {"name": "cost_center.update", "description": "Update cost centers", "resource_type": "cost_center", "action": "update"},
    {"name": "cost_center.delete", "description": "Delete cost centers", "resource_type": "cost_center", "action": "delete"},
    
    # Advanced Routing (Phase 1)
    {"name": "llm.routing.read", "description": "Read routing statistics", "resource_type": "llm", "action": "routing.read"},
    {"name": "llm.routing.manage", "description": "Manage routing settings", "resource_type": "llm", "action": "routing.manage"},
    {"name": "llm.load_balancer.read", "description": "Read load balancer stats", "resource_type": "llm", "action": "load_balancer.read"},
    {"name": "llm.predictive_routing.read", "description": "Read predictive routing analytics", "resource_type": "llm", "action": "predictive_routing.read"},
    {"name": "llm.weight_management.read", "description": "Read weight management stats", "resource_type": "llm", "action": "weight_management.read"},
    {"name": "llm.weight_management.manage", "description": "Manage weight settings", "resource_type": "llm", "action": "weight_management.manage"},
    {"name": "llm.geo_routing.read", "description": "Read geographic routing stats", "resource_type": "llm", "action": "geo_routing.read"},
    {"name": "llm.geo_routing.manage", "description": "Manage geographic routing", "resource_type": "llm", "action": "geo_routing.manage"},
    
    # Orchestration (Phase 3)
    {"name": "orchestration_read", "description": "Read orchestration dashboard", "resource_type": "orchestration", "action": "read"},
    {"name": "workflow.create", "description": "Create workflows", "resource_type": "workflow", "action": "create"},
    {"name": "workflow.read", "description": "Read workflows", "resource_type": "workflow", "action": "read"},
    {"name": "workflow.execute", "description": "Execute workflows", "resource_type": "workflow", "action": "execute"},
    {"name": "ab_test_create", "description": "Create A/B tests", "resource_type": "ab_test", "action": "create"},
    {"name": "ab_test_read", "description": "Read A/B tests", "resource_type": "ab_test", "action": "read"},
    {"name": "ab_test_manage", "description": "Manage A/B tests", "resource_type": "ab_test", "action": "manage"},
    {"name": "benchmark_create", "description": "Create benchmarks", "resource_type": "benchmark", "action": "create"},
    {"name": "benchmark_read", "description": "Read benchmarks", "resource_type": "benchmark", "action": "read"},
    {"name": "benchmark_execute", "description": "Execute benchmarks", "resource_type": "benchmark", "action": "execute"},
    
    # Monitoring (Phase 5)
    {"name": "monitoring.read", "description": "Read monitoring data", "resource_type": "monitoring", "action": "read"},
    {"name": "monitoring.write", "description": "Write monitoring data", "resource_type": "monitoring", "action": "write"},
    {"name": "monitoring.alert.acknowledge", "description": "Acknowledge alerts", "resource_type": "monitoring", "action": "alert.acknowledge"},
    {"name": "monitoring.alert.resolve", "description": "Resolve alerts", "resource_type": "monitoring", "action": "alert.resolve"},
    {"name": "monitoring.incident.create", "description": "Create incidents", "resource_type": "monitoring", "action": "incident.create"},
    {"name": "monitoring.incident.update", "description": "Update incidents", "resource_type": "monitoring", "action": "incident.update"},
    {"name": "monitoring.config.read", "description": "Read monitoring configuration", "resource_type": "monitoring", "action": "config.read"},
    {"name": "monitoring.config.update", "description": "Update monitoring configuration", "resource_type": "monitoring", "action": "config.update"},
]

# Default roles with their permissions
DEFAULT_ROLES = [
    {
        "name": "Owner",
        "description": "Full access to all features",
        "is_system_role": True,
        "permissions": [
            "user.read", "user.create", "user.update", "user.delete",
            "api_key.read", "api_key.create", "api_key.update", "api_key.delete",
            "organization.read", "organization.update",
            "analytics.read", "analytics.executive",
            "usage.read",
            "billing.read", "billing.update",
            "llm.generate", "llm.models.read",
            "role.read", "role.create", "role.update", "role.delete", "role.assign",
            "audit_log.read",
            "admin.stats.read", "admin.users.read", "admin.users.update", "admin.users.delete",
            "ab_testing.read", "ab_testing.create", "ab_testing.update", "ab_testing.delete",
            "cost_center.read", "cost_center.create", "cost_center.update", "cost_center.delete",
            "llm.routing.read", "llm.routing.manage", "llm.load_balancer.read", 
            "llm.predictive_routing.read", "llm.weight_management.read", "llm.weight_management.manage",
            "llm.geo_routing.read", "llm.geo_routing.manage",
            "orchestration_read", "workflow.create", "workflow.read", "workflow.execute",
            "ab_test_create", "ab_test_read", "ab_test_manage",
            "benchmark_create", "benchmark_read", "benchmark_execute",
            "monitoring.read", "monitoring.write", "monitoring.alert.acknowledge", "monitoring.alert.resolve",
            "monitoring.incident.create", "monitoring.incident.update", "monitoring.config.read", "monitoring.config.update"
        ]
    },
    {
        "name": "Admin",
        "description": "Manage team and settings",
        "is_system_role": True,
        "permissions": [
            "user.read", "user.create", "user.update",
            "api_key.read", "api_key.create", "api_key.update", "api_key.delete",
            "organization.read",
            "analytics.read", "analytics.executive",
            "usage.read",
            "billing.read",
            "llm.generate", "llm.models.read",
            "role.read", "role.assign",
            "audit_log.read",
            "admin.users.read", "admin.users.update",
            "ab_testing.read", "ab_testing.create", "ab_testing.update",
            "cost_center.read", "cost_center.create", "cost_center.update",
            "llm.routing.read", "llm.load_balancer.read", "llm.predictive_routing.read", 
            "llm.weight_management.read", "llm.geo_routing.read",
            "orchestration_read", "workflow.create", "workflow.read", "workflow.execute",
            "ab_test_create", "ab_test_read", "ab_test_manage",
            "benchmark_create", "benchmark_read", "benchmark_execute",
            "monitoring.read", "monitoring.write", "monitoring.alert.acknowledge", "monitoring.alert.resolve",
            "monitoring.incident.create", "monitoring.incident.update", "monitoring.config.read", "monitoring.config.update"
        ]
    },
    {
        "name": "Member",
        "description": "Use API and view analytics",
        "is_system_role": True,
        "permissions": [
            "user.read",
            "api_key.read", "api_key.create", "api_key.update", "api_key.delete",
            "organization.read",
            "analytics.read",
            "usage.read",
            "billing.read",
            "llm.generate", "llm.models.read",
            "ab_testing.read"
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
            "analytics.read",
            "usage.read",
            "billing.read",
            "llm.models.read"
        ]
    }
]

async def init_permissions(db: AsyncSession):
    """Initialize permissions in the database"""
    print("Creating permissions...")
    
    for perm_data in DEFAULT_PERMISSIONS:
        # Check if permission already exists
        result = await db.execute(
            select(Permission).where(Permission.name == perm_data["name"])
        )
        existing_perm = result.scalar_one_or_none()
        
        if not existing_perm:
            permission = Permission(
                name=perm_data["name"],
                description=perm_data["description"],
                resource_type=perm_data["resource_type"],
                action=perm_data["action"]
            )
            db.add(permission)
            print(f"  Created permission: {perm_data['name']}")
        else:
            print(f"  Permission already exists: {perm_data['name']}")
    
    await db.commit()
    print("Permissions initialized successfully!")

async def init_roles(db: AsyncSession):
    """Initialize roles in the database"""
    print("Creating roles...")
    
    # Get all organizations
    result = await db.execute(select(Organization))
    organizations = result.scalars().all()
    
    for org in organizations:
        print(f"  Initializing roles for organization: {org.name}")
        
        for role_data in DEFAULT_ROLES:
            # Check if role already exists for this organization
            result = await db.execute(
                select(Role).where(
                    Role.name == role_data["name"],
                    Role.organization_id == org.id
                )
            )
            existing_role = result.scalar_one_or_none()
            
            if not existing_role:
                role = Role(
                    name=role_data["name"],
                    description=role_data["description"],
                    organization_id=org.id,
                    is_system_role=role_data["is_system_role"],
                    permissions=role_data["permissions"]
                )
                db.add(role)
                print(f"    Created role: {role_data['name']}")
            else:
                print(f"    Role already exists: {role_data['name']}")
    
    await db.commit()
    print("Roles initialized successfully!")

async def assign_default_roles(db: AsyncSession):
    """Assign default roles to existing users"""
    print("Assigning default roles to users...")
    
    # Get all users
    result = await db.execute(select(User))
    users = result.scalars().all()
    
    for user in users:
        # Determine default role based on current role
        if user.role == UserRoleEnum.OWNER:
            role_name = "Owner"
        elif user.role == UserRoleEnum.ADMIN:
            role_name = "Admin"
        elif user.role == UserRoleEnum.MEMBER:
            role_name = "Member"
        else:
            role_name = "Viewer"
        
        # Get the role
        role_result = await db.execute(
            select(Role).where(
                Role.name == role_name,
                Role.organization_id == user.organization_id
            )
        )
        role = role_result.scalar_one_or_none()
        
        if role:
            # Check if user already has this role
            user_role_result = await db.execute(
                select(UserRole).where(
                    UserRole.user_id == user.id,
                    UserRole.role_id == role.id
                )
            )
            existing_user_role = user_role_result.scalar_one_or_none()
            
            if not existing_user_role:
                user_role = UserRole(
                    user_id=user.id,
                    role_id=role.id,
                    assigned_by=user.id,  # Self-assigned for initialization
                    expires_at=None
                )
                db.add(user_role)
                print(f"  Assigned {role_name} role to {user.email}")
            else:
                print(f"  User {user.email} already has {role_name} role")
    
    await db.commit()
    print("Default roles assigned successfully!")

async def main():
    """Main initialization function"""
    print("🚀 Initializing RBAC System...")
    
    async with AsyncSession(async_engine) as db:
        try:
            await init_permissions(db)
            await init_roles(db)
            await assign_default_roles(db)
            print("✅ RBAC system initialized successfully!")
        except Exception as e:
            print(f"❌ Error initializing RBAC: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(main()) 