"""
Community Schemas
社群功能的 Pydantic schemas
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from enum import Enum


class PostTypeEnum(str, Enum):
    """貼文類型"""
    question = "question"
    share = "share"


# ===== Photo Schemas =====
class PostPhotoBase(BaseModel):
    """貼文照片基礎 schema"""
    file_key: str
    display_order: int = 0


class PostPhotoResponse(PostPhotoBase):
    """貼文照片回應 schema"""
    id: int
    post_id: int
    photo_url: str  # presigned URL
    created_at: datetime

    class Config:
        from_attributes = True


# ===== Post Schemas =====
class PostCreate(BaseModel):
    """建立貼文 schema"""
    post_type: PostTypeEnum
    content: str = Field(..., min_length=1, max_length=5000)
    # photos will be uploaded separately via multipart/form-data


class PostUpdate(BaseModel):
    """更新貼文 schema"""
    content: Optional[str] = Field(None, min_length=1, max_length=5000)
    post_type: Optional[PostTypeEnum] = None


class UserBasicInfo(BaseModel):
    """用戶基本資訊"""
    id: int
    name: Optional[str]
    email: str

    class Config:
        from_attributes = True


class PostResponse(BaseModel):
    """貼文回應 schema"""
    id: int
    user_id: int
    user: UserBasicInfo
    post_type: PostTypeEnum
    content: str
    photos: List[PostPhotoResponse] = []
    like_count: int = 0
    comment_count: int = 0
    is_liked: bool = False  # 當前用戶是否已按讚
    is_deleted: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PostListResponse(BaseModel):
    """貼文列表回應"""
    total: int
    posts: List[PostResponse]
    has_more: bool = False


# ===== Comment Schemas =====
class CommentCreate(BaseModel):
    """建立留言 schema"""
    content: str = Field(..., min_length=1, max_length=1000)


class CommentUpdate(BaseModel):
    """更新留言 schema"""
    content: str = Field(..., min_length=1, max_length=1000)


class CommentResponse(BaseModel):
    """留言回應 schema"""
    id: int
    post_id: int
    user_id: int
    user: UserBasicInfo
    content: str
    like_count: int = 0
    is_liked: bool = False  # 當前用戶是否已按讚
    is_deleted: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class CommentListResponse(BaseModel):
    """留言列表回應"""
    total: int
    comments: List[CommentResponse]


# ===== Like Schemas =====
class LikeResponse(BaseModel):
    """按讚回應 schema"""
    success: bool
    is_liked: bool  # 操作後的狀態
    like_count: int  # 總讚數

    class Config:
        from_attributes = True


# ===== Report Schemas =====
class PostReportCreate(BaseModel):
    """檢舉貼文 schema"""
    reason: str = Field(..., min_length=1, max_length=1000, description="檢舉原因")


class PostReportResponse(BaseModel):
    """檢舉貼文回應 schema"""
    success: bool
    message: str

    class Config:
        from_attributes = True
