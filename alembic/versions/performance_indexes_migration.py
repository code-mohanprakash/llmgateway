"""Add performance indexes for critical queries

Revision ID: perf_indexes_001
Revises: enterprise_features_migration
Create Date: 2024-07-19 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'perf_indexes_001'
down_revision = 'enterprise_features_migration'
branch_labels = None
depends_on = None

def upgrade():
    """Add performance indexes"""
    
    # API Keys performance indexes
    op.create_index('idx_api_keys_user_id', 'api_keys', ['user_id'])
    op.create_index('idx_api_keys_organization_id', 'api_keys', ['organization_id'])
    op.create_index('idx_api_keys_last_used', 'api_keys', ['last_used_at'])
    
    # User Roles performance indexes
    op.create_index('idx_user_roles_composite', 'user_roles', ['user_id', 'role_id'])
    op.create_index('idx_user_roles_user_id', 'user_roles', ['user_id'])
    
    # Audit Logs performance indexes (critical for large datasets)
    op.create_index('idx_audit_logs_composite', 'audit_logs', ['organization_id', 'created_at', 'action'])
    op.create_index('idx_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('idx_audit_logs_created_at', 'audit_logs', ['created_at'])
    
    # Organizations performance indexes
    op.create_index('idx_organizations_created_by', 'organizations', ['created_by_id'])
    
    # Usage Records performance indexes
    op.create_index('idx_usage_records_organization', 'usage_records', ['organization_id', 'created_at'])
    op.create_index('idx_usage_records_user', 'usage_records', ['user_id', 'created_at'])
    
    # Workflow Executions performance indexes
    op.create_index('idx_workflow_executions_org', 'workflow_executions', ['organization_id', 'created_at'])
    op.create_index('idx_workflow_executions_status', 'workflow_executions', ['status'])
    
    # Monitoring Metrics performance indexes
    op.create_index('idx_monitoring_metrics_org_time', 'monitoring_metrics', ['organization_id', 'timestamp'])
    op.create_index('idx_monitoring_metrics_metric_type', 'monitoring_metrics', ['metric_type', 'timestamp'])

def downgrade():
    """Remove performance indexes"""
    
    # Drop API Keys indexes
    op.drop_index('idx_api_keys_user_id', 'api_keys')
    op.drop_index('idx_api_keys_organization_id', 'api_keys')
    op.drop_index('idx_api_keys_last_used', 'api_keys')
    
    # Drop User Roles indexes
    op.drop_index('idx_user_roles_composite', 'user_roles')
    op.drop_index('idx_user_roles_user_id', 'user_roles')
    
    # Drop Audit Logs indexes
    op.drop_index('idx_audit_logs_composite', 'audit_logs')
    op.drop_index('idx_audit_logs_user_id', 'audit_logs')
    op.drop_index('idx_audit_logs_created_at', 'audit_logs')
    
    # Drop Organizations indexes
    op.drop_index('idx_organizations_created_by', 'organizations')
    
    # Drop Usage Records indexes
    op.drop_index('idx_usage_records_organization', 'usage_records')
    op.drop_index('idx_usage_records_user', 'usage_records')
    
    # Drop Workflow Executions indexes
    op.drop_index('idx_workflow_executions_org', 'workflow_executions')
    op.drop_index('idx_workflow_executions_status', 'workflow_executions')
    
    # Drop Monitoring Metrics indexes
    op.drop_index('idx_monitoring_metrics_org_time', 'monitoring_metrics')
    op.drop_index('idx_monitoring_metrics_metric_type', 'monitoring_metrics')