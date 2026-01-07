"""add google auth fields to users

Revision ID: a9def0bf1582
Revises: f9921323b53a
Create Date: 2026-01-07 12:55:26.911145
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a9def0bf1582"
down_revision = "f9921323b53a"
branch_labels = None
depends_on = None


def upgrade():
    # SQLite-safe batch migration
    with op.batch_alter_table("users") as batch_op:

        # 1️⃣ Make hashed_password nullable
        batch_op.alter_column(
            "hashed_password",
            existing_type=sa.String(length=255),
            nullable=True,
        )

        # 2️⃣ Add firebase_uid
        batch_op.add_column(
            sa.Column("firebase_uid", sa.String(length=128), nullable=True)
        )
        batch_op.create_index(
            "ix_users_firebase_uid",
            ["firebase_uid"],
            unique=True,
        )

        # 3️⃣ Add auth_provider
        batch_op.add_column(
            sa.Column(
                "auth_provider",
                sa.String(length=20),
                nullable=False,
                server_default="password",
            )
        )

        # 4️⃣ Add is_verified
        batch_op.add_column(
            sa.Column(
                "is_verified",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )

    # ✅ Remove server defaults after data migration
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column("auth_provider", server_default=None)
        batch_op.alter_column("is_verified", server_default=None)


def downgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("is_verified")
        batch_op.drop_column("auth_provider")
        batch_op.drop_index("ix_users_firebase_uid")
        batch_op.drop_column("firebase_uid")

        batch_op.alter_column(
            "hashed_password",
            existing_type=sa.String(length=255),
            nullable=False,
        )
