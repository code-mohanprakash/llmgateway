"""merge heads for unified migration

Revision ID: 239e7c75bb96
Revises: 0d839d8237a7, enterprise_features_001
Create Date: 2025-07-17 00:26:29.902429

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '239e7c75bb96'
down_revision: Union[str, None] = ('0d839d8237a7', 'enterprise_features_001')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
