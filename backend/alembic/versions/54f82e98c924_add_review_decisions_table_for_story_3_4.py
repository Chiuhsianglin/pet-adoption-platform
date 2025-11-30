"""Add review_decisions table for Story 3.4

Revision ID: 54f82e98c924
Revises: ff0f13767798
Create Date: 2025-11-08 14:48:52.464660

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '54f82e98c924'
down_revision: Union[str, Sequence[str], None] = 'ff0f13767798'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create review_decisions table
    op.create_table(
        'review_decisions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('application_id', sa.Integer(), nullable=False),
        sa.Column('reviewer_id', sa.Integer(), nullable=False),
        sa.Column('decision', sa.String(length=20), nullable=False),
        sa.Column('decision_reason', sa.Text(), nullable=True),
        sa.Column('recommendations', sa.Text(), nullable=True),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('conditions', sa.JSON(), nullable=True),
        sa.Column('review_started', sa.DateTime(), nullable=True),
        sa.Column('review_completed', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('time_spent_minutes', sa.Integer(), nullable=True),
        sa.Column('is_final', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['application_id'], ['adoption_applications.id'], name='fk_review_decisions_application_id'),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'], name='fk_review_decisions_reviewer_id'),
        sa.Index('ix_review_decisions_application_id', 'application_id'),
        sa.Index('ix_review_decisions_reviewer_id', 'reviewer_id'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('review_decisions')
