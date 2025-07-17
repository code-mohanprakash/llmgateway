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
        sa.Column('conditions', sa.JSON),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('is_deleted', sa.Boolean, server_default=sa.text('0'), nullable=False),
        sa.Column('deleted_at', sa.DateTime, nullable=True)
    )

    # Create roles table
    op.create_table('roles',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('is_system_role', sa.Boolean, default=False),
        sa.Column('permissions', sa.JSON, nullable=False),
        sa.Column('parent_role_id', sa.String(36)),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['parent_role_id'], ['roles.id'])
    )

    # Create role_permissions table
    op.create_table('role_permissions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('role_id', sa.String(36), nullable=False),
        sa.Column('permission_id', sa.String(36), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
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
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
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
        sa.Column('old_values', sa.JSON),
        sa.Column('new_values', sa.JSON),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.Text),
        sa.Column('session_id', sa.String(255)),
        sa.Column('success', sa.Boolean, default=True),
        sa.Column('error_message', sa.Text),
        sa.Column('metadata', sa.JSON),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
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
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
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
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['usage_record_id'], ['usage_records.id']),
        sa.ForeignKeyConstraint(['cost_center_id'], ['cost_centers.id'])
    )

    # Create workflows table
    op.create_table('workflows',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('definition', sa.JSON, nullable=False),
        sa.Column('version', sa.Integer, default=1),
        sa.Column('status', sa.String(20), default='draft'),
        sa.Column('created_by', sa.String(36), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'])
    )

    # Create workflow_executions table
    op.create_table('workflow_executions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('workflow_id', sa.String(36), nullable=False),
        sa.Column('organization_id', sa.String(36), nullable=False),
        sa.Column('input_data', sa.JSON),
        sa.Column('output_data', sa.JSON),
        sa.Column('status', sa.String(20), default='running'),
        sa.Column('started_at', sa.DateTime, default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime),
        sa.Column('error_message', sa.Text),
        sa.Column('execution_time_ms', sa.Integer),
        sa.Column('total_cost', sa.Integer),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
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
        sa.Column('variants', sa.JSON, nullable=False),
        sa.Column('traffic_split', sa.JSON, nullable=False),
        sa.Column('duration_days', sa.Integer, nullable=False),
        sa.Column('success_metrics', sa.JSON, nullable=False),
        sa.Column('statistical_significance', sa.Float, default=0.05),
        sa.Column('status', sa.String(20), default='active'),
        sa.Column('created_by', sa.String(36), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
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
        sa.Column('input_data', sa.JSON),
        sa.Column('executed_at', sa.DateTime, default=sa.func.now()),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['test_id'], ['ab_tests.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'])
    )

    # Create ab_test_results table
    op.create_table('ab_test_results',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('test_id', sa.String(36), nullable=False),
        sa.Column('variant', sa.String(10), nullable=False),
        sa.Column('metrics', sa.JSON),
        sa.Column('success', sa.Boolean, default=True),
        sa.Column('recorded_at', sa.DateTime, default=sa.func.now()),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
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

    # Remove the for loop that inserts system_permissions using op.execute
    # Do not insert default permissions in the migration; use a Python script after migration.


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