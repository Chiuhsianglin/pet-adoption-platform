"""Add document_requests table

Revision ID: cbdaecbf7f8c
Revises: 54f82e98c924
Create Date: 2025-11-08 15:34:29.649171

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cbdaecbf7f8c'
down_revision: Union[str, Sequence[str], None] = '54f82e98c924'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'document_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('application_id', sa.Integer(), nullable=False),
        sa.Column('requester_id', sa.Integer(), nullable=False),
        sa.Column('requested_documents', sa.JSON(), nullable=False),
        sa.Column('request_reason', sa.Text(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('response_note', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('submitted_at', sa.DateTime(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['application_id'], ['adoption_applications.id'], name='fk_document_requests_application_id'),
        sa.ForeignKeyConstraint(['requester_id'], ['users.id'], name='fk_document_requests_requester_id'),
        sa.PrimaryKeyConstraint('id'),
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci'
    )
    op.create_index('ix_document_requests_id', 'document_requests', ['id'])
    op.create_index('ix_document_requests_application_id', 'document_requests', ['application_id'])
    op.create_index('ix_document_requests_requester_id', 'document_requests', ['requester_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_document_requests_requester_id', table_name='document_requests')
    op.drop_index('ix_document_requests_application_id', table_name='document_requests')
    op.drop_index('ix_document_requests_id', table_name='document_requests')
    op.drop_table('document_requests')
