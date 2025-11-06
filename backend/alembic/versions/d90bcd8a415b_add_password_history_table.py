"""Add password history table

Revision ID: d90bcd8a415b
Revises: d96ce37d5ca1
Create Date: 2025-11-06 16:51:06.553658

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd90bcd8a415b'
down_revision: Union[str, Sequence[str], None] = 'd96ce37d5ca1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create password_history table
    op.create_table('password_history',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_password_history_id'), 'password_history', ['id'], unique=False)
    op.create_index(op.f('ix_password_history_user_id'), 'password_history', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_password_history_user_id'), table_name='password_history')
    op.drop_index(op.f('ix_password_history_id'), table_name='password_history')
    op.drop_table('password_history')
