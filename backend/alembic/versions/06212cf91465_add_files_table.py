"""add_files_table

Revision ID: 06212cf91465
Revises: d90bcd8a415b
Create Date: 2025-11-06 21:04:42.510858

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '06212cf91465'
down_revision: Union[str, Sequence[str], None] = 'd90bcd8a415b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'files',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False, comment='存儲的檔案名稱'),
        sa.Column('original_filename', sa.String(255), nullable=False, comment='原始檔案名稱'),
        sa.Column('file_size', sa.BigInteger(), nullable=False, comment='檔案大小 (bytes)'),
        sa.Column('mime_type', sa.String(100), nullable=False, comment='MIME 類型'),
        sa.Column('file_hash', sa.String(64), nullable=False, comment='SHA-256 hash'),
        sa.Column('storage_path', sa.String(500), nullable=False, comment='S3 儲存路徑'),
        sa.Column('category', sa.Enum('pet_photo', 'document', 'avatar', name='filecategory'), nullable=False, comment='檔案類別'),
        sa.Column('related_id', sa.Integer(), nullable=True, comment='關聯 ID (pet_id, user_id 等)'),
        sa.Column('uploaded_by', sa.Integer(), nullable=False, comment='上傳者 user_id'),
        sa.Column('is_public', sa.Boolean(), nullable=False, default=False, comment='是否公開'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, default=False, comment='軟刪除標記'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'), comment='創建時間'),
        sa.Column('deleted_at', sa.DateTime(), nullable=True, comment='刪除時間'),
        
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ondelete='CASCADE'),
        
        comment='檔案儲存記錄表'
    )
    
    # Create indexes
    op.create_index('ix_files_category_related', 'files', ['category', 'related_id'])
    op.create_index('ix_files_uploaded_by', 'files', ['uploaded_by'])
    op.create_index('ix_files_file_hash', 'files', ['file_hash'])
    op.create_index('ix_files_is_deleted', 'files', ['is_deleted'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_files_is_deleted', table_name='files')
    op.drop_index('ix_files_file_hash', table_name='files')
    op.drop_index('ix_files_uploaded_by', table_name='files')
    op.drop_index('ix_files_category_related', table_name='files')
    op.drop_table('files')
    
    # Drop enum type
    op.execute('DROP TYPE IF EXISTS filecategory')
