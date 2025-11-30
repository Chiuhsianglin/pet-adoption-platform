"""add_pet_age_years_months_to_chat_pet_cards

Revision ID: 37f4fcc517ec
Revises: 253e7eb0c4cb
Create Date: 2025-11-17 11:53:00.630331

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '37f4fcc517ec'
down_revision: Union[str, Sequence[str], None] = '253e7eb0c4cb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add pet_age_years and pet_age_months columns to chat_pet_cards
    op.add_column('chat_pet_cards', sa.Column('pet_age_years', sa.Integer(), nullable=True, comment='年齡-年份（快照）'))
    op.add_column('chat_pet_cards', sa.Column('pet_age_months', sa.Integer(), nullable=True, comment='年齡-月份（快照）'))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove pet_age_years and pet_age_months columns from chat_pet_cards
    op.drop_column('chat_pet_cards', 'pet_age_months')
    op.drop_column('chat_pet_cards', 'pet_age_years')
