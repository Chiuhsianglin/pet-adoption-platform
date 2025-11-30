"""merge_heads

Revision ID: 73a2e819b925
Revises: a11df5e5bec9, f4e8c9d3a2b1
Create Date: 2025-11-16 18:53:38.346770

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '73a2e819b925'
down_revision: Union[str, Sequence[str], None] = ('a11df5e5bec9', 'f4e8c9d3a2b1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
