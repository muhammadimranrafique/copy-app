"""add_partially_paid_to_orderstatus_enum

Revision ID: c2d19bbaa79d
Revises: 3f5d6e78901a
Create Date: 2025-12-02 21:32:32.827499

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c2d19bbaa79d'
down_revision: Union[str, None] = '3f5d6e78901a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add 'Partially Paid' to the orderstatus enum
    # PostgreSQL requires special handling for adding enum values
    op.execute("ALTER TYPE orderstatus ADD VALUE IF NOT EXISTS 'Partially Paid'")


def downgrade() -> None:
    # Note: PostgreSQL does not support removing enum values directly
    # This would require recreating the enum type, which is complex
    # For now, we'll leave the enum value in place on downgrade
    pass
