"""add_pet_history_table

Revision ID: bfeee84d13dd
Revises: 06212cf91465
Create Date: 2025-11-06 23:02:52.895134

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision: str = 'bfeee84d13dd'
down_revision: Union[str, Sequence[str], None] = '06212cf91465'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 創建 pet_history 表
    op.create_table(
        'pet_history',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('pet_id', sa.Integer(), nullable=False),
        sa.Column('changed_by', sa.Integer(), nullable=False),
        sa.Column('change_type', sa.String(length=50), nullable=False),
        sa.Column('old_status', sa.Enum('available', 'pending', 'adopted', 'unavailable', name='petstatus'), nullable=True),
        sa.Column('new_status', sa.Enum('available', 'pending', 'adopted', 'unavailable', name='petstatus'), nullable=True),
        sa.Column('field_name', sa.String(length=100), nullable=True),
        sa.Column('old_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('extra_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['pet_id'], ['pets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['changed_by'], ['users.id'], ondelete='RESTRICT'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    
    # 創建索引
    op.create_index('ix_pet_history_pet_id', 'pet_history', ['pet_id'])
    op.create_index('ix_pet_history_changed_by', 'pet_history', ['changed_by'])
    op.create_index('ix_pet_history_change_type', 'pet_history', ['change_type'])
    op.create_index('ix_pet_history_created_at', 'pet_history', ['created_at'])


def downgrade() -> None:
    """Downgrade schema."""
    # 刪除索引
    op.drop_index('ix_pet_history_created_at', table_name='pet_history')
    op.drop_index('ix_pet_history_change_type', table_name='pet_history')
    op.drop_index('ix_pet_history_changed_by', table_name='pet_history')
    op.drop_index('ix_pet_history_pet_id', table_name='pet_history')
    
    # 刪除表
    op.drop_table('pet_history')
