"""Add missing payment_method and reference_number columns to expenses table

Revision ID: b1c2d3e4f5g6
Revises: a252b5dd7f7e
Create Date: 2025-11-03 00:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b1c2d3e4f5g6'
down_revision: Union[str, None] = '989b9ea69916'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add missing columns to expenses table
    op.add_column('expenses', sa.Column('payment_method', sa.String(), nullable=True))
    op.add_column('expenses', sa.Column('reference_number', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove the added columns
    op.drop_column('expenses', 'reference_number')
    op.drop_column('expenses', 'payment_method')