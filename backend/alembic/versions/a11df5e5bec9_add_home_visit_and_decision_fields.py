"""add_home_visit_and_decision_fields

Revision ID: a11df5e5bec9
Revises: ccec3edb08fa
Create Date: 2025-11-13 20:06:36.580526

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a11df5e5bec9'
down_revision: Union[str, Sequence[str], None] = 'ccec3edb08fa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
