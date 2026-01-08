"""Add inventory history and stock to category

Revision ID: 8a7b6c5d4e3f
Revises: 5f9b3c7e8d1a
Create Date: 2026-01-08 17:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a7b6c5d4e3f'
down_revision: Union[str, Sequence[str], None] = '5f9b3c7e8d1a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add stock to categories
    op.add_column('categories', sa.Column('stock', sa.Integer(), nullable=False, server_default='0'))
    
    # Create inventory_history table
    op.create_table('inventory_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=20), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('previous_stock', sa.Integer(), nullable=False),
        sa.Column('new_stock', sa.Integer(), nullable=False),
        sa.Column('performed_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.ForeignKeyConstraint(['performed_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inventory_history_category_id'), 'inventory_history', ['category_id'], unique=False)
    op.create_index(op.f('ix_inventory_history_id'), 'inventory_history', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_inventory_history_id'), table_name='inventory_history')
    op.drop_index(op.f('ix_inventory_history_category_id'), table_name='inventory_history')
    op.drop_table('inventory_history')
    op.drop_column('categories', 'stock')
