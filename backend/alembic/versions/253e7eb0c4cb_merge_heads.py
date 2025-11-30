"""merge_heads

Revision ID: 253e7eb0c4cb
Revises: 1bde096b8ff2, performance_indexes
Create Date: 2025-11-17 11:52:21.834084

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '253e7eb0c4cb'
down_revision: Union[str, Sequence[str], None] = ('1bde096b8ff2', 'performance_indexes')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
