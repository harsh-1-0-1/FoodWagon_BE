"""Add is_active to categories

Revision ID: 5f9b3c7e8d1a
Revises: 22b1821dc1d0
Create Date: 2026-01-08 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f9b3c7e8d1a'
down_revision: Union[str, Sequence[str], None] = '22b1821dc1d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('categories', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))


def downgrade() -> None:
    op.drop_column('categories', 'is_active')
