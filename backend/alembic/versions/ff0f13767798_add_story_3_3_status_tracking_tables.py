"""Add Story 3.3 status tracking tables

Revision ID: ff0f13767798
Revises: 5ca7c0dd4380
Create Date: 2025-11-08 14:30:32.821936

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff0f13767798'
down_revision: Union[str, Sequence[str], None] = '5ca7c0dd4380'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create status_transitions table
    op.create_table(
        'status_transitions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('from_status', sa.String(length=50), nullable=False),
        sa.Column('to_status', sa.String(length=50), nullable=False),
        sa.Column('condition_type', sa.String(length=100), nullable=True),
        sa.Column('is_auto', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('requires_approval', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('allowed_roles', sa.JSON(), nullable=True),
        sa.Column('estimated_duration_hours', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_status_transitions_from_status', 'from_status'),
        sa.Index('ix_status_transitions_to_status', 'to_status'),
    )

    # Create application_timeline table
    op.create_table(
        'application_timeline',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('application_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('previous_status', sa.String(length=50), nullable=True),
        sa.Column('changed_by', sa.Integer(), nullable=True),
        sa.Column('change_reason', sa.Text(), nullable=True),
        sa.Column('auto_generated', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('estimated_completion', sa.DateTime(), nullable=True),
        sa.Column('extra_data', sa.JSON(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['application_id'], ['adoption_applications.id'], name='fk_application_timeline_application_id'),
        sa.ForeignKeyConstraint(['changed_by'], ['users.id'], name='fk_application_timeline_changed_by'),
        sa.Index('ix_application_timeline_application_id', 'application_id'),
        sa.Index('ix_application_timeline_status', 'status'),
        sa.Index('ix_application_timeline_created_at', 'created_at'),
    )

    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('application_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('user_role', sa.String(length=50), nullable=True),
        sa.Column('old_values', sa.JSON(), nullable=True),
        sa.Column('new_values', sa.JSON(), nullable=True),
        sa.Column('changes_summary', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['application_id'], ['adoption_applications.id'], name='fk_audit_logs_application_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_audit_logs_user_id'),
        sa.Index('ix_audit_logs_application_id', 'application_id'),
        sa.Index('ix_audit_logs_action', 'action'),
        sa.Index('ix_audit_logs_entity_type', 'entity_type'),
        sa.Index('ix_audit_logs_created_at', 'created_at'),
    )

    # Create review_comments table
    op.create_table(
        'review_comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('application_id', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=False),
        sa.Column('comment_type', sa.String(length=50), nullable=False, server_default='general'),
        sa.Column('reviewer_id', sa.Integer(), nullable=False),
        sa.Column('is_internal', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('is_required_action', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('is_resolved', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('resolved_by', sa.Integer(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolution_comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['application_id'], ['adoption_applications.id'], name='fk_review_comments_application_id'),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'], name='fk_review_comments_reviewer_id'),
        sa.ForeignKeyConstraint(['resolved_by'], ['users.id'], name='fk_review_comments_resolved_by'),
        sa.Index('ix_review_comments_application_id', 'application_id'),
        sa.Index('ix_review_comments_is_resolved', 'is_resolved'),
        sa.Index('ix_review_comments_created_at', 'created_at'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('review_comments')
    op.drop_table('audit_logs')
    op.drop_table('application_timeline')
    op.drop_table('status_transitions')
