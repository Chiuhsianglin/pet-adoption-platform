"""remove_address_fields_keep_only_address_line1

Revision ID: 8dc579ab472d
Revises: 73a2e819b925
Create Date: 2025-11-16 18:53:56.190718

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8dc579ab472d'
down_revision: Union[str, Sequence[str], None] = '73a2e819b925'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 移除不需要的地址欄位，只保留 address_line1
    op.drop_column('users', 'address_line2')
    op.drop_column('users', 'city')
    op.drop_column('users', 'state')
    op.drop_column('users', 'postal_code')
    op.drop_column('users', 'country')


def downgrade() -> None:
    """Downgrade schema."""
    # 恢復移除的欄位
    op.add_column('users', sa.Column('address_line2', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('city', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('state', sa.String(length=100), nullable=True))
    op.add_column('users', sa.Column('postal_code', sa.String(length=20), nullable=True))
    op.add_column('users', sa.Column('country', sa.String(length=100), nullable=True))
