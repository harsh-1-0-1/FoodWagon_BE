"""Fix timestamp defaults

Revision ID: 22b1821dc1d0
Revises: 7657533a6158
Create Date: 2026-01-08 14:23:16.979716
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "22b1821dc1d0"
down_revision: Union[str, Sequence[str], None] = "7657533a6158"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # PRODUCTS
    op.alter_column(
        "products",
        "created_at",
        server_default=sa.text("NOW()"),
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
    )
    op.alter_column(
        "products",
        "updated_at",
        server_default=sa.text("NOW()"),
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
    )

    # Repeat for other tables if they use TimestampMixin
    # Example:
    # op.alter_column("restaurants", "created_at", server_default=sa.text("NOW()"), ...)
    # op.alter_column("restaurants", "updated_at", server_default=sa.text("NOW()"), ...)


def downgrade() -> None:
    # PRODUCTS
    op.alter_column(
        "products",
        "created_at",
        server_default=None,
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
    )
    op.alter_column(
        "products",
        "updated_at",
        server_default=None,
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
    )
