"""Add adoption confirmation and handover tables

Revision ID: e7ca5268b4cb
Revises: cbdaecbf7f8c
Create Date: 2025-11-08 15:56:10.137238

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7ca5268b4cb'
down_revision: Union[str, Sequence[str], None] = 'cbdaecbf7f8c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create adoption_confirmations table
    op.create_table(
        'adoption_confirmations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('application_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('approval_notes', sa.Text(), nullable=True),
        sa.Column('conditions', sa.Text(), nullable=True),
        sa.Column('requirements_met', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['adoption_applications.id']),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    op.create_index('ix_adoption_confirmations_id', 'adoption_confirmations', ['id'])
    op.create_index('ix_adoption_confirmations_application_id', 'adoption_confirmations', ['application_id'], unique=True)
    
    # Create handover_schedules table
    op.create_table(
        'handover_schedules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('confirmation_id', sa.Integer(), nullable=False),
        sa.Column('handover_date', sa.Date(), nullable=False),
        sa.Column('handover_time', sa.Time(), nullable=True),
        sa.Column('location', sa.String(255), nullable=False),
        sa.Column('contact_person', sa.String(100), nullable=True),
        sa.Column('contact_phone', sa.String(20), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='scheduled'),
        sa.Column('items_checklist', sa.Text(), nullable=True),
        sa.Column('special_instructions', sa.Text(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('completed_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['confirmation_id'], ['adoption_confirmations.id']),
        sa.PrimaryKeyConstraint('id'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    op.create_index('ix_handover_schedules_id', 'handover_schedules', ['id'])
    op.create_index('ix_handover_schedules_confirmation_id', 'handover_schedules', ['confirmation_id'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_handover_schedules_confirmation_id', table_name='handover_schedules')
    op.drop_index('ix_handover_schedules_id', table_name='handover_schedules')
    op.drop_table('handover_schedules')
    
    op.drop_index('ix_adoption_confirmations_application_id', table_name='adoption_confirmations')
    op.drop_index('ix_adoption_confirmations_id', table_name='adoption_confirmations')
    op.drop_table('adoption_confirmations')
