"""add_monitoring_tables

Revision ID: monitoring_tables_001
Revises: fd124c72f000
Create Date: 2025-07-19 02:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision: str = 'monitoring_tables_001'
down_revision: Union[str, None] = 'fd124c72f000'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    
    # Create system_health table
    op.create_table('system_health',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('cpu_usage', sa.Float(), nullable=False),
        sa.Column('memory_usage', sa.Float(), nullable=False),
        sa.Column('disk_usage', sa.Float(), nullable=False),
        sa.Column('network_latency', sa.Float(), nullable=False),
        sa.Column('response_time', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('uptime_seconds', sa.Integer(), nullable=False),
        sa.Column('active_connections', sa.Integer(), nullable=True),
        sa.Column('error_rate', sa.Float(), nullable=True),
        sa.Column('throughput', sa.Float(), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create performance_metrics table
    op.create_table('performance_metrics',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('metric_name', sa.String(length=100), nullable=False),
        sa.Column('metric_type', sa.String(length=50), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(length=20), nullable=False),
        sa.Column('endpoint', sa.String(length=200), nullable=True),
        sa.Column('method', sa.String(length=10), nullable=True),
        sa.Column('user_id', sa.String(length=36), nullable=True),
        sa.Column('organization_id', sa.String(length=36), nullable=True),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create alerts table
    op.create_table('alerts',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('alert_type', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('acknowledged_by', sa.String(length=36), nullable=True),
        sa.Column('acknowledged_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=False),
        sa.Column('metric_name', sa.String(length=100), nullable=True),
        sa.Column('threshold_value', sa.Float(), nullable=True),
        sa.Column('current_value', sa.Float(), nullable=True),
        sa.Column('notification_sent', sa.Boolean(), nullable=True),
        sa.Column('notification_channels', sqlite.JSON(), nullable=True),
        sa.Column('organization_id', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['acknowledged_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create sla_metrics table
    op.create_table('sla_metrics',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('sla_name', sa.String(length=100), nullable=False),
        sa.Column('sla_target', sa.Float(), nullable=False),
        sa.Column('sla_period', sa.String(length=20), nullable=False),
        sa.Column('current_value', sa.Float(), nullable=False),
        sa.Column('compliance_percentage', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('period_start', sa.DateTime(), nullable=False),
        sa.Column('period_end', sa.DateTime(), nullable=False),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create incidents table
    op.create_table('incidents',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('incident_type', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=False),
        sa.Column('affected_services', sqlite.JSON(), nullable=True),
        sa.Column('impact_level', sa.String(length=20), nullable=False),
        sa.Column('root_cause', sa.Text(), nullable=True),
        sa.Column('resolution', sa.Text(), nullable=True),
        sa.Column('resolved_by', sa.String(length=36), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('detected_at', sa.DateTime(), nullable=False),
        sa.Column('organization_id', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['resolved_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create monitoring_config table
    op.create_table('monitoring_config',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('config_name', sa.String(length=100), nullable=False),
        sa.Column('config_type', sa.String(length=50), nullable=False),
        sa.Column('cpu_warning_threshold', sa.Float(), nullable=True),
        sa.Column('cpu_critical_threshold', sa.Float(), nullable=True),
        sa.Column('memory_warning_threshold', sa.Float(), nullable=True),
        sa.Column('memory_critical_threshold', sa.Float(), nullable=True),
        sa.Column('response_time_warning_threshold', sa.Float(), nullable=True),
        sa.Column('response_time_critical_threshold', sa.Float(), nullable=True),
        sa.Column('uptime_target', sa.Float(), nullable=True),
        sa.Column('response_time_target', sa.Float(), nullable=True),
        sa.Column('email_notifications', sa.Boolean(), nullable=True),
        sa.Column('slack_notifications', sa.Boolean(), nullable=True),
        sa.Column('webhook_notifications', sa.Boolean(), nullable=True),
        sa.Column('notification_recipients', sqlite.JSON(), nullable=True),
        sa.Column('organization_id', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('config_name')
    )
    
    # Create indexes for performance
    op.create_index('idx_system_health_org_time', 'system_health', ['organization_id', 'recorded_at'], unique=False)
    op.create_index('idx_performance_metrics_org_time', 'performance_metrics', ['organization_id', 'recorded_at'], unique=False)
    op.create_index('idx_alerts_org_status', 'alerts', ['organization_id', 'status'], unique=False)
    op.create_index('idx_incidents_org_status', 'incidents', ['organization_id', 'status'], unique=False)
    
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    
    # Drop indexes
    op.drop_index('idx_incidents_org_status', table_name='incidents')
    op.drop_index('idx_alerts_org_status', table_name='alerts')
    op.drop_index('idx_performance_metrics_org_time', table_name='performance_metrics')
    op.drop_index('idx_system_health_org_time', table_name='system_health')
    
    # Drop tables
    op.drop_table('monitoring_config')
    op.drop_table('incidents')
    op.drop_table('sla_metrics')
    op.drop_table('alerts')
    op.drop_table('performance_metrics')
    op.drop_table('system_health')
    
    # ### end Alembic commands ### 