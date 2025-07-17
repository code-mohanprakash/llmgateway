"""add_organizations_table

Revision ID: 6bdcb5be9459
Revises: 239e7c75bb96
Create Date: 2025-07-17 20:52:27.326796

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6bdcb5be9459'
down_revision: Union[str, None] = '239e7c75bb96'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create organizations table
    op.create_table('organizations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), unique=True, nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('website', sa.String(255)),
        sa.Column('plan_type', sa.String(20), default='FREE', nullable=False),
        sa.Column('stripe_customer_id', sa.String(255), unique=True),
        sa.Column('stripe_subscription_id', sa.String(255)),
        sa.Column('monthly_request_limit', sa.Integer, default=1000),
        sa.Column('monthly_token_limit', sa.Integer, default=50000),
        sa.Column('features', sa.JSON, default=dict),
        sa.Column('settings', sa.JSON, default=dict),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('is_deleted', sa.Boolean, server_default=sa.text('0'), nullable=False),
        sa.Column('deleted_at', sa.DateTime, nullable=True)
    )


def downgrade() -> None:
    op.drop_table('organizations')
