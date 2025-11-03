"""add_is_active_to_products

Revision ID: 445c80d4983e
Revises: b1c2d3e4f5g6
Create Date: 2025-11-03 09:56:20.306525

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '445c80d4983e'
down_revision: Union[str, None] = 'b1c2d3e4f5g6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('products', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))


def downgrade() -> None:
    op.drop_column('products', 'is_active')
