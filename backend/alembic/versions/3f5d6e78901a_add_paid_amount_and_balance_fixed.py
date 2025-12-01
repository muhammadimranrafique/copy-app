"""Add paid_amount and balance to orders - FIXED

Revision ID: 3f5d6e78901a
Revises: 5b02fbe7d939
Create Date: 2025-11-30 14:52:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f5d6e78901a'
down_revision: Union[str, None] = '5b02fbe7d939'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add paid_amount and balance columns to orders table
    op.add_column('orders', sa.Column('paid_amount', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('orders', sa.Column('balance', sa.Float(), nullable=False, server_default='0.0'))


def downgrade() -> None:
    # Remove paid_amount and balance columns from orders table
    op.drop_column('orders', 'balance')
    op.drop_column('orders', 'paid_amount')
