"""add_performance_indexes

Revision ID: performance_indexes
Revises: 
Create Date: 2025-11-16

添加性能优化索引：
- adoption_applications.status
- adoption_applications.created_at  
- community_posts.created_at
- community_posts.is_deleted
- post_likes.post_id
- post_comments.post_id
- pets.status
- pets.shelter_id
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'performance_indexes'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 添加索引到 adoption_applications 表
    op.create_index(
        'idx_adoption_applications_status',
        'adoption_applications',
        ['status'],
        unique=False
    )
    op.create_index(
        'idx_adoption_applications_created_at',
        'adoption_applications',
        ['created_at'],
        unique=False
    )
    op.create_index(
        'idx_adoption_applications_pet_status',
        'adoption_applications',
        ['pet_id', 'status'],
        unique=False
    )
    
    # 添加索引到 community_posts 表
    op.create_index(
        'idx_community_posts_created_at',
        'community_posts',
        ['created_at'],
        unique=False
    )
    op.create_index(
        'idx_community_posts_is_deleted',
        'community_posts',
        ['is_deleted'],
        unique=False
    )
    op.create_index(
        'idx_community_posts_user_deleted',
        'community_posts',
        ['user_id', 'is_deleted'],
        unique=False
    )
    
    # 添加索引到 post_likes 表
    op.create_index(
        'idx_post_likes_post_id',
        'post_likes',
        ['post_id'],
        unique=False
    )
    op.create_index(
        'idx_post_likes_user_post',
        'post_likes',
        ['user_id', 'post_id'],
        unique=False
    )
    
    # 添加索引到 post_comments 表
    op.create_index(
        'idx_post_comments_post_id',
        'post_comments',
        ['post_id'],
        unique=False
    )
    op.create_index(
        'idx_post_comments_post_deleted',
        'post_comments',
        ['post_id', 'is_deleted'],
        unique=False
    )
    
    # 添加索引到 pets 表（如果还没有的话）
    op.create_index(
        'idx_pets_status',
        'pets',
        ['status'],
        unique=False
    )
    op.create_index(
        'idx_pets_shelter_id',
        'pets',
        ['shelter_id'],
        unique=False
    )
    
    # 添加索引到 notifications 表
    op.create_index(
        'idx_notifications_user_created',
        'notifications',
        ['user_id', 'created_at'],
        unique=False
    )
    op.create_index(
        'idx_notifications_user_read',
        'notifications',
        ['user_id', 'is_read'],
        unique=False
    )


def downgrade() -> None:
    # 删除所有添加的索引
    op.drop_index('idx_notifications_user_read', table_name='notifications')
    op.drop_index('idx_notifications_user_created', table_name='notifications')
    op.drop_index('idx_pets_shelter_id', table_name='pets')
    op.drop_index('idx_pets_status', table_name='pets')
    op.drop_index('idx_post_comments_post_deleted', table_name='post_comments')
    op.drop_index('idx_post_comments_post_id', table_name='post_comments')
    op.drop_index('idx_post_likes_user_post', table_name='post_likes')
    op.drop_index('idx_post_likes_post_id', table_name='post_likes')
    op.drop_index('idx_community_posts_user_deleted', table_name='community_posts')
    op.drop_index('idx_community_posts_is_deleted', table_name='community_posts')
    op.drop_index('idx_community_posts_created_at', table_name='community_posts')
    op.drop_index('idx_adoption_applications_pet_status', table_name='adoption_applications')
    op.drop_index('idx_adoption_applications_created_at', table_name='adoption_applications')
    op.drop_index('idx_adoption_applications_status', table_name='adoption_applications')
