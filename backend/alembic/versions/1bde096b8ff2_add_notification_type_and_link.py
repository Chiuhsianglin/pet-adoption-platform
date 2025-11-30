"""add_notification_type_and_link

Revision ID: 1bde096b8ff2
Revises: f2ca674574f8
Create Date: 2025-11-16 20:23:50.290082

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1bde096b8ff2'
down_revision: Union[str, Sequence[str], None] = 'f2ca674574f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add notification_type enum column
    op.execute("""
        ALTER TABLE notifications 
        ADD COLUMN notification_type VARCHAR(50) NULL
    """)
    
    # Add link column
    op.add_column('notifications', sa.Column('link', sa.String(500), nullable=True))
    
    # Create index on notification_type
    op.create_index(op.f('ix_notifications_notification_type'), 'notifications', ['notification_type'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_notifications_notification_type'), table_name='notifications')
    op.drop_column('notifications', 'link')
    op.drop_column('notifications', 'notification_type')
