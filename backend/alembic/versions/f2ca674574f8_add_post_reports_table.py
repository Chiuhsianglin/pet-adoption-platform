"""add_post_reports_table

Revision ID: f2ca674574f8
Revises: 8dc579ab472d
Create Date: 2025-11-16 20:21:08.078212

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f2ca674574f8'
down_revision: Union[str, Sequence[str], None] = '8dc579ab472d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'post_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('reporter_id', sa.Integer(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['post_id'], ['community_posts.id'], ),
        sa.ForeignKeyConstraint(['reporter_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_post_reports_id'), 'post_reports', ['id'], unique=False)
    op.create_index(op.f('ix_post_reports_post_id'), 'post_reports', ['post_id'], unique=False)
    op.create_index(op.f('ix_post_reports_reporter_id'), 'post_reports', ['reporter_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_post_reports_reporter_id'), table_name='post_reports')
    op.drop_index(op.f('ix_post_reports_post_id'), table_name='post_reports')
    op.drop_index(op.f('ix_post_reports_id'), table_name='post_reports')
    op.drop_table('post_reports')
