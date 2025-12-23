"""add order_category to expenses

Revision ID: g3h4i5j6k7l8
Revises: f2g3h4i5j6k7
Create Date: 2024-12-23 15:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision = 'g3h4i5j6k7l8'
down_revision = 'f2g3h4i5j6k7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add order_category column to expenses table
    op.add_column('expenses', sa.Column('order_category', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove order_category column from expenses table
    op.drop_column('expenses', 'order_category')
