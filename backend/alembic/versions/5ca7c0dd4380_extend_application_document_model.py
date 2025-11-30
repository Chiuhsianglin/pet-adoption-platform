"""extend_application_document_model

Revision ID: 5ca7c0dd4380
Revises: 4853a5452c14
Create Date: 2025-11-08 12:59:12.127792

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5ca7c0dd4380'
down_revision: Union[str, Sequence[str], None] = '4853a5452c14'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add new columns to application_documents table
    op.add_column('application_documents', sa.Column('file_hash', sa.String(64), nullable=True))
    op.add_column('application_documents', sa.Column('security_scan_status', sa.String(50), server_default='pending', nullable=False))
    op.add_column('application_documents', sa.Column('scan_result', sa.Text(), nullable=True))
    op.add_column('application_documents', sa.Column('is_safe', sa.Boolean(), server_default=sa.text('1'), nullable=False))
    op.add_column('application_documents', sa.Column('version', sa.Integer(), server_default=sa.text('1'), nullable=False))
    op.add_column('application_documents', sa.Column('is_current_version', sa.Boolean(), server_default=sa.text('1'), nullable=False))
    op.add_column('application_documents', sa.Column('replaced_by_id', sa.Integer(), nullable=True))
    op.add_column('application_documents', sa.Column('description', sa.Text(), nullable=True))
    
    # Add foreign key for replaced_by_id
    op.create_foreign_key(
        'fk_application_documents_replaced_by',
        'application_documents',
        'application_documents',
        ['replaced_by_id'],
        ['id']
    )
    
    # Create indexes for better query performance
    op.create_index('ix_application_documents_document_type', 'application_documents', ['document_type'])
    op.create_index('ix_application_documents_is_current_version', 'application_documents', ['is_current_version'])
    op.create_index('ix_application_documents_file_hash', 'application_documents', ['file_hash'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('ix_application_documents_file_hash', 'application_documents')
    op.drop_index('ix_application_documents_is_current_version', 'application_documents')
    op.drop_index('ix_application_documents_document_type', 'application_documents')
    
    # Drop foreign key
    op.drop_constraint('fk_application_documents_replaced_by', 'application_documents', type_='foreignkey')
    
    # Drop columns
    op.drop_column('application_documents', 'description')
    op.drop_column('application_documents', 'replaced_by_id')
    op.drop_column('application_documents', 'is_current_version')
    op.drop_column('application_documents', 'version')
    op.drop_column('application_documents', 'is_safe')
    op.drop_column('application_documents', 'scan_result')
    op.drop_column('application_documents', 'security_scan_status')
    op.drop_column('application_documents', 'file_hash')
