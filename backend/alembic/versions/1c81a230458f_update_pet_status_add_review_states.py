"""update_pet_status_add_review_states

Revision ID: 1c81a230458f
Revises: bfeee84d13dd
Create Date: 2025-11-06 23:13:31.697733

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1c81a230458f'
down_revision: Union[str, Sequence[str], None] = 'bfeee84d13dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 在 MySQL 中修改 ENUM 需要使用 ALTER TABLE MODIFY
    op.execute("""
        ALTER TABLE pets 
        MODIFY COLUMN status ENUM(
            'draft',
            'pending_review', 
            'available',
            'pending',
            'adopted',
            'unavailable',
            'rejected'
        ) NOT NULL DEFAULT 'draft'
    """)
    
    # 更新 pet_history 表的 old_status 和 new_status ENUM
    op.execute("""
        ALTER TABLE pet_history
        MODIFY COLUMN old_status ENUM(
            'draft',
            'pending_review',
            'available',
            'pending',
            'adopted',
            'unavailable',
            'rejected'
        )
    """)
    
    op.execute("""
        ALTER TABLE pet_history
        MODIFY COLUMN new_status ENUM(
            'draft',
            'pending_review',
            'available',
            'pending',
            'adopted',
            'unavailable',
            'rejected'
        )
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # 回退到原始的四個狀態
    op.execute("""
        ALTER TABLE pets 
        MODIFY COLUMN status ENUM(
            'available',
            'pending',
            'adopted',
            'unavailable'
        ) NOT NULL DEFAULT 'available'
    """)
    
    op.execute("""
        ALTER TABLE pet_history
        MODIFY COLUMN old_status ENUM(
            'available',
            'pending',
            'adopted',
            'unavailable'
        )
    """)
    
    op.execute("""
        ALTER TABLE pet_history
        MODIFY COLUMN new_status ENUM(
            'available',
            'pending',
            'adopted',
            'unavailable'
        )
    """)
