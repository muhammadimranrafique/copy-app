"""Add order_category column to orders table

Revision ID: c3d4e5f6g7h8
Revises: b2c3d4e5f6g7
Create Date: 2025-12-10 23:56:06.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6g7h8'
down_revision: Union[str, None] = 'b2c3d4e5f6g7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add order_category column to orders table
    # VARCHAR type, nullable for backward compatibility
    # Default value for new orders is "Standard Order"
    op.add_column('orders', sa.Column('order_category', sa.String(), nullable=True, server_default='Standard Order'))


def downgrade() -> None:
    # Remove order_category column from orders table
    op.drop_column('orders', 'order_category')
