"""add server defaults to users timestamps

Revision ID: de21a233f1bb
Revises: eb17e5f6836f
Create Date: 2026-01-08
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "de21a233f1bb"
down_revision = "eb17e5f6836f"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "users",
        "created_at",
        server_default=sa.func.now(),
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
    )

    op.alter_column(
        "users",
        "updated_at",
        server_default=sa.func.now(),
        existing_type=sa.DateTime(timezone=True),
        nullable=False,
    )


def downgrade():
    op.alter_column("users", "created_at", server_default=None)
    op.alter_column("users", "updated_at", server_default=None)
