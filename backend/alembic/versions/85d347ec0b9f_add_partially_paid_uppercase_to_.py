"""add_partially_paid_uppercase_to_orderstatus

Revision ID: 85d347ec0b9f
Revises: c2d19bbaa79d
Create Date: 2025-12-02 21:39:49.932905

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '85d347ec0b9f'
down_revision: Union[str, None] = 'c2d19bbaa79d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add 'PARTIALLY_PAID' to the orderstatus enum (matching the existing uppercase format)
    op.execute("ALTER TYPE orderstatus ADD VALUE IF NOT EXISTS 'PARTIALLY_PAID'")


def downgrade() -> None:
    pass
