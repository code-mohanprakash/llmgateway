"""Enterprise Features Migration

Add RBAC, audit logging, cost centers, and workflow management tables
"""

# revision identifiers, used by Alembic.
revision = 'enterprise_features_001'
down_revision = 'ad3f04c48711'  # Update this to the latest migration
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Create permissions table
    op.create_table('permissions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('description', sa.Text),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('conditions', postgresql.JSONB),
        sa.Column('created_at', sa.String, nullable=False),
        sa.Column('updated_at', sa.String, nullable=False)
    )

    # Create roles table
    op.create_table('roles',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('is_system_role', sa.Boolean, default=False),
        sa.Column('permissions', postgresql.JSONB, nullable=False),
        sa.Column('parent_role_id', sa.String(36)),
        sa.Column('created_at', sa.String, nullable=False),
        sa.Column('updated_at', sa.String, nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['parent_role_id'], ['roles.id'])
    )

    # Create role_permissions table
    op.create_table('role_permissions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('role_id', sa.String(36), nullable=False),
        sa.Column('permission_id', sa.String(36), nullable=False),
        sa.Column('created_at', sa.String, nullable=False),
        sa.Column('updated_at', sa.String, nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id']),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'])
    )

    # Create user_roles table
    op.create_table('user_roles',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('role_id', sa.String(36), nullable=False),
        sa.Column('assigned_by', sa.String(36), nullable=False),
        sa.Column('expires_at', sa.DateTime),
        sa.Column('created_at', sa.String, nullable=False),
        sa.Column('updated_at', sa.String, nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id']),
        sa.ForeignKeyConstraint(['assigned_by'], ['users.id']),
        sa.UniqueConstraint('user_id', 'role_id')
    )

    # Create audit_logs table
    op.create_table('audit_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36)),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('resource_id', sa.String(255)),
        sa.Column('old_values', postgresql.JSONB),
        sa.Column('new_values', postgresql.JSONB),
        sa.Column('ip_address', postgresql.INET),
        sa.Column('user_agent', sa.Text),
        sa.Column('session_id', sa.String(255)),
        sa.Column('success', sa.Boolean, default=True),
        sa.Column('error_message', sa.Text),
        sa.Column('additional_metadata', postgresql.JSONB),
        sa.Column('created_at', sa.String, nullable=False),
        sa.Column('updated_at', sa.String, nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )

    # Create cost_centers table
    op.create_table('cost_centers',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('budget_limit', sa.Integer),
        sa.Column('manager_id', sa.String(36)),
        sa.Column('created_at', sa.String, nullable=False),
        sa.Column('updated_at', sa.String, nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['manager_id'], ['users.id']),
        sa.UniqueConstraint('organization_id', 'code')
    )

    # Create usage_allocations table
    op.create_table('usage_allocations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('usage_record_id', sa.String(36), nullable=False),
        sa.Column('cost_center_id', sa.String(36), nullable=False),
        sa.Column('department', sa.String(100)),
        sa.Column('project_code', sa.String(50)),
        sa.Column('allocation_percentage', sa.Integer, default=100),
        sa.Column('allocated_cost', sa.Integer),
        sa.Column('created_at', sa.String, nullable=False),
        sa.Column('updated_at', sa.String, nullable=False),
        sa.ForeignKeyConstraint(['usage_record_id'], ['usage_records.id']),
        sa.ForeignKeyConstraint(['cost_center_id'], ['cost_centers.id'])
    )

    # Create workflows table
    op.create_table('workflows',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('definition', postgresql.JSONB, nullable=False),
        sa.Column('version', sa.Integer, default=1),
        sa.Column('status', sa.String(20), default='draft'),
        sa.Column('created_by', sa.String(36), nullable=False),
        sa.Column('created_at', sa.String, nullable=False),
        sa.Column('updated_at', sa.String, nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'])
    )

    # Create workflow_executions table
    op.create_table('workflow_executions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('workflow_id', sa.String(36), nullable=False),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('input_data', postgresql.JSONB),
        sa.Column('output_data', postgresql.JSONB),
        sa.Column('status', sa.String(20), default='running'),
        sa.Column('started_at', sa.DateTime, default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime),
        sa.Column('error_message', sa.Text),
        sa.Column('execution_time_ms', sa.Integer),
        sa.Column('total_cost', sa.Integer),
        sa.Column('created_at', sa.String, nullable=False),
        sa.Column('updated_at', sa.String, nullable=False),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflows.id']),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'])
    )

    # Create ab_tests table
    op.create_table('ab_tests',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('test_type', sa.String(50), nullable=False),
        sa.Column('variants', postgresql.JSONB, nullable=False),
        sa.Column('traffic_split', postgresql.JSONB, nullable=False),
        sa.Column('duration_days', sa.Integer, nullable=False),
        sa.Column('success_metrics', postgresql.JSONB, nullable=False),
        sa.Column('statistical_significance', sa.Float, default=0.05),
        sa.Column('status', sa.String(20), default='active'),
        sa.Column('created_by', sa.String(36), nullable=False),
        sa.Column('created_at', sa.String, nullable=False),
        sa.Column('updated_at', sa.String, nullable=False),
        sa.Column('expires_at', sa.DateTime, nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'])
    )

    # Create ab_test_executions table
    op.create_table('ab_test_executions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('test_id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('variant', sa.String(10), nullable=False),
        sa.Column('input_data', postgresql.JSONB),
        sa.Column('executed_at', sa.DateTime, default=sa.func.now()),
        sa.Column('created_at', sa.String, nullable=False),
        sa.Column('updated_at', sa.String, nullable=False),
        sa.ForeignKeyConstraint(['test_id'], ['ab_tests.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )

    # Create ab_test_results table
    op.create_table('ab_test_results',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('test_id', sa.String(36), nullable=False),
        sa.Column('variant', sa.String(10), nullable=False),
        sa.Column('metrics', postgresql.JSONB),
        sa.Column('success', sa.Boolean, default=True),
        sa.Column('recorded_at', sa.DateTime, default=sa.func.now()),
        sa.Column('created_at', sa.String, nullable=False),
        sa.Column('updated_at', sa.String, nullable=False),
        sa.ForeignKeyConstraint(['test_id'], ['ab_tests.id'])
    )

    # Create indexes for performance
    op.create_index('idx_audit_logs_org_time', 'audit_logs', ['organization_id', 'created_at'])
    op.create_index('idx_audit_logs_user_time', 'audit_logs', ['user_id', 'created_at'])
    op.create_index('idx_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('idx_audit_logs_resource', 'audit_logs', ['resource_type', 'resource_id'])
    
    op.create_index('idx_workflow_executions_workflow', 'workflow_executions', ['workflow_id'])
    op.create_index('idx_workflow_executions_status', 'workflow_executions', ['status'])
    op.create_index('idx_workflow_executions_org', 'workflow_executions', ['organization_id'])
    
    op.create_index('idx_ab_tests_org', 'ab_tests', ['organization_id'])
    op.create_index('idx_ab_tests_status', 'ab_tests', ['status'])
    op.create_index('idx_ab_test_executions_test', 'ab_test_executions', ['test_id'])
    op.create_index('idx_ab_test_results_test', 'ab_test_results', ['test_id'])
    op.create_index('idx_ab_test_results_variant', 'ab_test_results', ['variant'])

    # Insert system permissions
    system_permissions = [
        # User management
        ('user.create', 'Create users', 'user', 'create'),
        ('user.read', 'Read user information', 'user', 'read'),
        ('user.update', 'Update user information', 'user', 'update'),
        ('user.delete', 'Delete users', 'user', 'delete'),
        
        # API Key management
        ('api_key.create', 'Create API keys', 'api_key', 'create'),
        ('api_key.read', 'Read API key information', 'api_key', 'read'),
        ('api_key.update', 'Update API keys', 'api_key', 'update'),
        ('api_key.delete', 'Delete API keys', 'api_key', 'delete'),
        
        # Organization management
        ('organization.read', 'Read organization information', 'organization', 'read'),
        ('organization.update', 'Update organization settings', 'organization', 'update'),
        
        # Usage and analytics
        ('usage.read', 'Read usage analytics', 'usage', 'read'),
        ('analytics.read', 'Read analytics data', 'analytics', 'read'),
        
        # Billing management
        ('billing.read', 'Read billing information', 'billing', 'read'),
        ('billing.update', 'Update billing settings', 'billing', 'update'),
        
        # Workflow management
        ('workflow.create', 'Create workflows', 'workflow', 'create'),
        ('workflow.read', 'Read workflow information', 'workflow', 'read'),
        ('workflow.update', 'Update workflows', 'workflow', 'update'),
        ('workflow.delete', 'Delete workflows', 'workflow', 'delete'),
        ('workflow.execute', 'Execute workflows', 'workflow', 'execute'),
        
        # Cost center management
        ('cost_center.create', 'Create cost centers', 'cost_center', 'create'),
        ('cost_center.read', 'Read cost center information', 'cost_center', 'read'),
        ('cost_center.update', 'Update cost centers', 'cost_center', 'update'),
        ('cost_center.delete', 'Delete cost centers', 'cost_center', 'delete'),
        
        # Role management
        ('role.create', 'Create roles', 'role', 'create'),
        ('role.read', 'Read role information', 'role', 'read'),
        ('role.update', 'Update roles', 'role', 'update'),
        ('role.delete', 'Delete roles', 'role', 'delete'),
        ('role.assign', 'Assign roles to users', 'role', 'assign'),
        
        # Audit logs
        ('audit_log.read', 'Read audit logs', 'audit_log', 'read'),
        
        # LLM API access
        ('llm.generate', 'Generate text using LLM', 'llm', 'generate'),
        ('llm.models.read', 'Read available models', 'llm', 'read_models'),
        
        # A/B Testing
        ('ab_testing.create', 'Create A/B tests', 'ab_testing', 'create'),
        ('ab_testing.read', 'Read A/B test information', 'ab_testing', 'read'),
        ('ab_testing.update', 'Update A/B tests', 'ab_testing', 'update'),
        ('ab_testing.delete', 'Delete A/B tests', 'ab_testing', 'delete'),
        ('ab_testing.execute', 'Execute A/B tests', 'ab_testing', 'execute'),
        
        # SSO
        ('sso.configure', 'Configure SSO providers', 'sso', 'configure'),
        ('sso.read', 'Read SSO configuration', 'sso', 'read'),
        
        # MFA
        ('mfa.setup', 'Setup MFA for users', 'mfa', 'setup'),
        ('mfa.verify', 'Verify MFA codes', 'mfa', 'verify'),
    ]

    for perm_name, perm_desc, resource_type, action in system_permissions:
        op.execute(f"""
            INSERT INTO permissions (id, name, description, resource_type, action, created_at, updated_at)
            VALUES (gen_random_uuid(), '{perm_name}', '{perm_desc}', '{resource_type}', '{action}', 
                   to_char(now(), 'YYYY-MM-DD"T"HH24:MI:SS.US"Z"'), 
                   to_char(now(), 'YYYY-MM-DD"T"HH24:MI:SS.US"Z"'))
        """)


def downgrade():
    # Drop tables in reverse order
    op.drop_table('ab_test_results')
    op.drop_table('ab_test_executions')
    op.drop_table('ab_tests')
    op.drop_table('workflow_executions')
    op.drop_table('workflows')
    op.drop_table('usage_allocations')
    op.drop_table('cost_centers')
    op.drop_table('audit_logs')
    op.drop_table('user_roles')
    op.drop_table('role_permissions')
    op.drop_table('roles')
    op.drop_table('permissions') 