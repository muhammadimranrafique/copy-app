"""Add PRINTING_1, PRINTING_2, PRINTING_3 to ExpenseCategory enum

Revision ID: a1b2c3d4e5f6
Revises: ff2b23db3ca0
Create Date: 2025-12-10 23:21:21.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'ff2b23db3ca0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new printing category values to the expensecategory enum
    # Using IF NOT EXISTS to make migration idempotent
    op.execute("ALTER TYPE expensecategory ADD VALUE IF NOT EXISTS 'PRINTING_1'")
    op.execute("ALTER TYPE expensecategory ADD VALUE IF NOT EXISTS 'PRINTING_2'")
    op.execute("ALTER TYPE expensecategory ADD VALUE IF NOT EXISTS 'PRINTING_3'")


def downgrade() -> None:
    # Note: PostgreSQL does not support removing enum values
    # This is a one-way migration for safety
    # Existing expenses with these categories will remain valid
    pass
