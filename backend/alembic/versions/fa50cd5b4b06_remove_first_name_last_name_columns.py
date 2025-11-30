"""remove_first_name_last_name_columns

Revision ID: fa50cd5b4b06
Revises: 623743c6733f
Create Date: 2025-11-08 20:56:28.308347

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fa50cd5b4b06'
down_revision: Union[str, Sequence[str], None] = '623743c6733f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Remove first_name and last_name columns from users table
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'last_name')


def downgrade() -> None:
    """Downgrade schema."""
    # Add back first_name and last_name columns if needed
    op.add_column('users', sa.Column('first_name', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('last_name', sa.String(100), nullable=True))
