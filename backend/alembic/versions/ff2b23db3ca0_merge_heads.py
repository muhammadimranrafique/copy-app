"""merge heads

Revision ID: ff2b23db3ca0
Revises: 85d347ec0b9f, d4e5f6a7b8c9
Create Date: 2025-12-10 23:05:51.265115

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff2b23db3ca0'
down_revision: Union[str, None] = ('85d347ec0b9f', 'd4e5f6a7b8c9')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
