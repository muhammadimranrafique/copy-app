"""Add details column to orders table

Revision ID: d4e5f6a7b8c9
Revises: 3f5d6e78901a
Create Date: 2025-12-10 23:01:45.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = '3f5d6e78901a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add details column to orders table
    # TEXT type for multi-line content, nullable for backward compatibility
    op.add_column('orders', sa.Column('details', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove details column from orders table
    op.drop_column('orders', 'details')
