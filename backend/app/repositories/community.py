"""
Community Repository
社群功能資料存取層（貼文、留言、按讚）
"""
from typing import Optional, List
from sqlalchemy import select, and_, func, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.community import (
    CommunityPost, PostPhoto, PostComment, PostLike, PostTypeEnum
)


class CommunityRepository(BaseRepository[CommunityPost]):
    """社群貼文 Repository"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, CommunityPost)
    
    async def get_post_with_relations(self, post_id: int) -> Optional[CommunityPost]:
        """獲取貼文（包含完整關聯）"""
        result = await self.db.execute(
            select(CommunityPost)
            .options(
                selectinload(CommunityPost.user),
                selectinload(CommunityPost.photos),
                selectinload(CommunityPost.comments).selectinload(PostComment.user),
                selectinload(CommunityPost.likes)
            )
            .where(
                and_(
                    CommunityPost.id == post_id,
                    CommunityPost.is_deleted == False
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_posts(
        self,
        post_type: Optional[PostTypeEnum] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[CommunityPost]:
        """獲取貼文列表"""
        query = (
            select(CommunityPost)
            .options(
                selectinload(CommunityPost.user),
                selectinload(CommunityPost.photos),
                selectinload(CommunityPost.comments),
                selectinload(CommunityPost.likes)
            )
            .where(CommunityPost.is_deleted == False)
        )
        
        if post_type:
            query = query.where(CommunityPost.post_type == post_type)
        
        query = query.order_by(desc(CommunityPost.created_at)).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_user_posts(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[CommunityPost]:
        """獲取用戶的貼文"""
        result = await self.db.execute(
            select(CommunityPost)
            .options(selectinload(CommunityPost.photos))
            .where(
                and_(
                    CommunityPost.user_id == user_id,
                    CommunityPost.is_deleted == False
                )
            )
            .order_by(desc(CommunityPost.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def soft_delete_post(self, post_id: int, user_id: int) -> bool:
        """軟刪除貼文"""
        post = await self.get_by_id(post_id)
        if not post or post.user_id != user_id:
            return False
        
        post.is_deleted = True
        await self.db.commit()
        return True
    
    async def count_user_posts(self, user_id: int) -> int:
        """計算用戶的貼文數量"""
        result = await self.db.execute(
            select(func.count())
            .select_from(CommunityPost)
            .where(
                and_(
                    CommunityPost.user_id == user_id,
                    CommunityPost.is_deleted == False
                )
            )
        )
        return result.scalar()


class CommentRepository(BaseRepository[PostComment]):
    """留言 Repository"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, PostComment)
    
    async def get_comment_with_relations(self, comment_id: int) -> Optional[PostComment]:
        """獲取帶關聯的留言"""
        result = await self.db.execute(
            select(PostComment)
            .options(
                selectinload(PostComment.user)
            )
            .where(PostComment.id == comment_id)
        )
        return result.scalar_one_or_none()
    
    async def get_post_comments(
        self,
        post_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[PostComment]:
        """獲取貼文的留言"""
        result = await self.db.execute(
            select(PostComment)
            .options(
                selectinload(PostComment.user)
            )
            .where(
                and_(
                    PostComment.post_id == post_id,
                    PostComment.is_deleted == False
                )
            )
            .order_by(PostComment.created_at.desc())  # 最新的在前
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def soft_delete_comment(self, comment_id: int, user_id: int) -> bool:
        """軟刪除留言"""
        comment = await self.get_by_id(comment_id)
        if not comment or comment.user_id != user_id:
            return False
        
        comment.is_deleted = True
        await self.db.commit()
        return True
    
    async def count_post_comments(self, post_id: int) -> int:
        """計算貼文的留言數量"""
        result = await self.db.execute(
            select(func.count())
            .select_from(PostComment)
            .where(
                and_(
                    PostComment.post_id == post_id,
                    PostComment.is_deleted == False
                )
            )
        )
        return result.scalar()


class PostLikeRepository(BaseRepository[PostLike]):
    """貼文按讚 Repository"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, PostLike)
    
    async def like_post(self, post_id: int, user_id: int) -> PostLike:
        """按讚貼文（如果已存在則返回現有記錄）"""
        # 檢查是否已按讚
        result = await self.db.execute(
            select(PostLike).where(
                and_(
                    PostLike.post_id == post_id,
                    PostLike.user_id == user_id
                )
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            return existing
        
        # 創建新按讚
        like = PostLike(post_id=post_id, user_id=user_id)
        return await self.create(like)
    
    async def unlike_post(self, post_id: int, user_id: int) -> bool:
        """取消按讚"""
        result = await self.db.execute(
            select(PostLike).where(
                and_(
                    PostLike.post_id == post_id,
                    PostLike.user_id == user_id
                )
            )
        )
        like = result.scalar_one_or_none()
        
        if not like:
            return False
        
        await self.delete(like)
        return True
    
    async def is_liked_by_user(self, post_id: int, user_id: int) -> bool:
        """檢查用戶是否已按讚"""
        result = await self.db.execute(
            select(func.count())
            .select_from(PostLike)
            .where(
                and_(
                    PostLike.post_id == post_id,
                    PostLike.user_id == user_id
                )
            )
        )
        return result.scalar() > 0
    
    async def count_post_likes(self, post_id: int) -> int:
        """計算貼文的按讚數"""
        result = await self.db.execute(
            select(func.count())
            .select_from(PostLike)
            .where(PostLike.post_id == post_id)
        )
        return result.scalar()


class PhotoRepository(BaseRepository[PostPhoto]):
    """貼文照片 Repository"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, PostPhoto)
    
    async def create_photos(self, post_id: int, photo_keys: List[str]) -> List[PostPhoto]:
        """批量創建貼文照片"""
        photos = []
        for order, file_key in enumerate(photo_keys):
            photo = PostPhoto(
                post_id=post_id,
                file_key=file_key,
                display_order=order
            )
            self.db.add(photo)
            photos.append(photo)
        
        await self.db.commit()
        return photos
    
    async def get_post_photos(self, post_id: int) -> List[PostPhoto]:
        """獲取貼文的所有照片"""
        result = await self.db.execute(
            select(PostPhoto)
            .where(PostPhoto.post_id == post_id)
            .order_by(PostPhoto.display_order)
        )
        return result.scalars().all()
