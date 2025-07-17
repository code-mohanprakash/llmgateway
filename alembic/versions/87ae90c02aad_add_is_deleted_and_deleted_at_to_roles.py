"""add_is_deleted_and_deleted_at_to_roles

Revision ID: 87ae90c02aad
Revises: 6bdcb5be9459
Create Date: 2025-07-17 20:56:10.444741

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '87ae90c02aad'
down_revision: Union[str, None] = '6bdcb5be9459'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('roles', sa.Column('is_deleted', sa.Boolean, server_default=sa.text('0'), nullable=False))
    op.add_column('roles', sa.Column('deleted_at', sa.DateTime, nullable=True))


def downgrade() -> None:
    op.drop_column('roles', 'is_deleted')
    op.drop_column('roles', 'deleted_at')
