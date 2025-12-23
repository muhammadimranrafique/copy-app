"""Create order_items table

Revision ID: f2g3h4i5j6k7
Revises: e1f2g3h4i5j6
Create Date: 2025-12-23 14:06:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'f2g3h4i5j6k7'
down_revision: Union[str, None] = 'e1f2g3h4i5j6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create order_items table
    op.create_table('order_items',
        sa.Column('id', postgresql.UUID(), nullable=False),
        sa.Column('order_id', postgresql.UUID(), nullable=False),
        sa.Column('item_description', sa.String(length=500), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('pages', sa.Integer(), nullable=True),
        sa.Column('paper', sa.String(length=200), nullable=True),
        sa.Column('unit_price', sa.Float(), nullable=False),
        sa.Column('total_price', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Migrate existing orders to have one order_item each
    # This ensures backward compatibility
    op.execute("""
        INSERT INTO order_items (id, order_id, item_description, quantity, pages, paper, unit_price, total_price, created_at)
        SELECT 
            gen_random_uuid(),
            id,
            COALESCE(details, 'Product / Service Order'),
            1,
            pages,
            paper,
            total_amount,
            total_amount,
            created_at
        FROM orders
    """)


def downgrade() -> None:
    # Drop order_items table
    op.drop_table('order_items')
