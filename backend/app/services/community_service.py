"""
Community Service
社群功能業務邏輯層（貼文、留言、按讚）
"""
from typing import Optional, List, Dict, Any
from math import ceil

from app.repositories.community import (
    CommunityRepository,
    CommentRepository,
    PostLikeRepository,
    PhotoRepository
)
from app.models.community import CommunityPost, PostComment, PostTypeEnum
from app.exceptions import (
    PostNotFoundError,
    CommentNotFoundError,
    PermissionDeniedError,
    ValidationError
)


class CommunityService:
    """社群功能業務邏輯"""
    
    def __init__(
        self,
        post_repo: CommunityRepository,
        comment_repo: CommentRepository,
        post_like_repo: PostLikeRepository,
        photo_repo: PhotoRepository
    ):
        self.post_repo = post_repo
        self.comment_repo = comment_repo
        self.post_like_repo = post_like_repo
        self.photo_repo = photo_repo
    
    # ========== 貼文相關 ==========
    
    async def create_post(
        self,
        user_id: int,
        content: str,
        post_type: PostTypeEnum,
        photo_keys: Optional[List[str]] = None
    ) -> CommunityPost:
        """創建貼文"""
        if not content or len(content.strip()) == 0:
            raise ValidationError("貼文內容不能為空")
        
        # 創建貼文
        post = CommunityPost(
            user_id=user_id,
            content=content,
            post_type=post_type,
            is_deleted=False
        )
        post = await self.post_repo.create(post)
        
        # 如果有照片，創建照片記錄
        if photo_keys:
            await self.photo_repo.create_photos(post.id, photo_keys)
        
        return await self.post_repo.get_post_with_relations(post.id)
    
    async def get_post(self, post_id: int) -> CommunityPost:
        """獲取貼文詳情"""
        post = await self.post_repo.get_post_with_relations(post_id)
        if not post:
            raise PostNotFoundError(f"貼文 ID {post_id} 不存在")
        return post
    
    async def list_posts(
        self,
        post_type: Optional[PostTypeEnum] = None,
        page: int = 1,
        limit: int = 20
    ) -> Dict[str, Any]:
        """列出貼文（分頁）"""
        skip = (page - 1) * limit
        posts = await self.post_repo.get_posts(post_type, skip, limit)
        
        # 計算總數（這裡簡化處理，實際應該添加 count 方法）
        total = len(posts) + skip if len(posts) == limit else skip + len(posts)
        total_pages = ceil(total / limit) if limit > 0 else 1
        
        return {
            "results": posts,
            "page": page,
            "page_size": limit,
            "total": total,
            "total_pages": total_pages
        }
    
    async def get_user_posts(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> List[CommunityPost]:
        """獲取用戶的貼文"""
        return await self.post_repo.get_user_posts(user_id, skip, limit)
    
    async def update_post(
        self,
        post_id: int,
        user_id: int,
        content: str,
        post_type: Optional[str] = None
    ) -> CommunityPost:
        """更新貼文內容和類型"""
        post = await self.post_repo.get_by_id(post_id)
        if not post:
            raise PostNotFoundError(f"貼文 ID {post_id} 不存在")
        
        if post.user_id != user_id:
            raise PermissionDeniedError("只能編輯自己的貼文")
        
        if not content or len(content.strip()) == 0:
            raise ValidationError("貼文內容不能為空")
        
        # 準備更新數據
        update_data = {"content": content}
        if post_type is not None:
            update_data["post_type"] = post_type
        
        return await self.post_repo.update_by_id(post_id, **update_data)
    
    async def delete_post(
        self,
        post_id: int,
        user_id: int
    ) -> bool:
        """刪除貼文（軟刪除）"""
        return await self.post_repo.soft_delete_post(post_id, user_id)
    
    # ========== 留言相關 ==========
    
    async def create_comment(
        self,
        post_id: int,
        user_id: int,
        content: str
    ) -> PostComment:
        """創建留言"""
        # 驗證貼文存在
        post = await self.post_repo.get_by_id(post_id)
        if not post:
            raise PostNotFoundError(f"貼文 ID {post_id} 不存在")
        
        if not content or len(content.strip()) == 0:
            raise ValidationError("留言內容不能為空")
        
        comment = PostComment(
            post_id=post_id,
            user_id=user_id,
            content=content,
            is_deleted=False
        )
        
        created_comment = await self.comment_repo.create(comment)
        # 重新查詢以獲取關聯數據
        return await self.comment_repo.get_comment_with_relations(created_comment.id)
    
    async def get_post_comments(
        self,
        post_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[PostComment]:
        """獲取貼文的留言"""
        return await self.comment_repo.get_post_comments(post_id, skip, limit)
    
    async def delete_comment(
        self,
        comment_id: int,
        user_id: int
    ) -> bool:
        """刪除留言（軟刪除）"""
        return await self.comment_repo.soft_delete_comment(comment_id, user_id)
    
    # ========== 按讚相關 ==========
    
    async def like_post(
        self,
        post_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """按讚貼文"""
        # 驗證貼文存在
        post = await self.post_repo.get_by_id(post_id)
        if not post:
            raise PostNotFoundError(f"貼文 ID {post_id} 不存在")
        
        await self.post_like_repo.like_post(post_id, user_id)
        like_count = await self.post_like_repo.count_post_likes(post_id)
        
        return {
            "post_id": post_id,
            "liked": True,
            "like_count": like_count
        }
    
    async def unlike_post(
        self,
        post_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """取消按讚貼文"""
        success = await self.post_like_repo.unlike_post(post_id, user_id)
        like_count = await self.post_like_repo.count_post_likes(post_id)
        
        return {
            "post_id": post_id,
            "liked": False,
            "like_count": like_count
        }
    
    # ========== 統計相關 ==========
    
    async def get_post_stats(self, post_id: int) -> Dict[str, int]:
        """獲取貼文統計資料"""
        like_count = await self.post_like_repo.count_post_likes(post_id)
        comment_count = await self.comment_repo.count_post_comments(post_id)
        
        return {
            "likes": like_count,
            "comments": comment_count
        }
    
    async def is_post_liked_by_user(self, post_id: int, user_id: int) -> bool:
        """檢查用戶是否已按讚貼文"""
        return await self.post_like_repo.is_liked_by_user(post_id, user_id)
    
    async def get_user_stats(self, user_id: int) -> Dict[str, int]:
        """獲取用戶在社群的統計"""
        post_count = await self.post_repo.count_user_posts(user_id)
        
        return {
            "posts": post_count
        }
