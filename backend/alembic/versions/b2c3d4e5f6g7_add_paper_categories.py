"""Add PAPER, PAPER_1, PAPER_2, PAPER_3 to ExpenseCategory enum

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2025-12-10 23:29:04.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6g7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new paper category values to the expensecategory enum
    # Using IF NOT EXISTS to make migration idempotent
    op.execute("ALTER TYPE expensecategory ADD VALUE IF NOT EXISTS 'PAPER'")
    op.execute("ALTER TYPE expensecategory ADD VALUE IF NOT EXISTS 'PAPER_1'")
    op.execute("ALTER TYPE expensecategory ADD VALUE IF NOT EXISTS 'PAPER_2'")
    op.execute("ALTER TYPE expensecategory ADD VALUE IF NOT EXISTS 'PAPER_3'")


def downgrade() -> None:
    # Note: PostgreSQL does not support removing enum values
    # This is a one-way migration for safety
    pass
