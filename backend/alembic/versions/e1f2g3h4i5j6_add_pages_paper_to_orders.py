"""Add pages and paper columns to orders table

Revision ID: e1f2g3h4i5j6
Revises: c3d4e5f6g7h8
Create Date: 2025-12-23 13:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1f2g3h4i5j6'
down_revision: Union[str, None] = 'c3d4e5f6g7h8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add pages column to orders table (integer, nullable for backward compatibility)
    op.add_column('orders', sa.Column('pages', sa.Integer(), nullable=True))
    
    # Add paper column to orders table (string, nullable for backward compatibility)
    op.add_column('orders', sa.Column('paper', sa.String(length=200), nullable=True))


def downgrade() -> None:
    # Remove pages and paper columns from orders table
    op.drop_column('orders', 'paper')
    op.drop_column('orders', 'pages')
