"""
Community Models
社群功能資料模型：貼文、留言、按讚
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class PostTypeEnum(str, enum.Enum):
    """貼文類型"""
    question = "question"  # 問題
    share = "share"        # 分享


class CommunityPost(Base):
    """社群貼文"""
    __tablename__ = "community_posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="發文者ID")
    post_type = Column(SQLEnum(PostTypeEnum, native_enum=False, length=20), nullable=False, default=PostTypeEnum.share, comment="貼文類型")
    content = Column(Text, nullable=False, comment="貼文內容")
    is_deleted = Column(Boolean, default=False, nullable=False, comment="是否已刪除")
    created_at = Column(DateTime, server_default=func.now(), comment="建立時間")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="更新時間")

    # Relationships
    user = relationship("User", back_populates="community_posts")
    photos = relationship("PostPhoto", back_populates="post", cascade="all, delete-orphan", order_by="PostPhoto.display_order")
    comments = relationship("PostComment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("PostLike", back_populates="post", cascade="all, delete-orphan")
    reports = relationship("PostReport", back_populates="post", cascade="all, delete-orphan")

    # 索引
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
        Index('idx_post_type', 'post_type'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
        {'extend_existing': True}
    )

    def __repr__(self):
        return f"<CommunityPost(id={self.id}, user_id={self.user_id}, type={self.post_type})>"


class PostPhoto(Base):
    """貼文照片"""
    __tablename__ = "post_photos"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("community_posts.id", ondelete="CASCADE"), nullable=False, comment="貼文ID")
    file_key = Column(String(500), nullable=False, comment="S3檔案key")
    display_order = Column(Integer, nullable=False, default=0, comment="顯示順序")
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    post = relationship("CommunityPost", back_populates="photos")

    # 索引
    __table_args__ = (
        Index('idx_post_id', 'post_id'),
        {'extend_existing': True}
    )

    def __repr__(self):
        return f"<PostPhoto(id={self.id}, post_id={self.post_id}, order={self.display_order})>"


class PostComment(Base):
    """貼文留言"""
    __tablename__ = "post_comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("community_posts.id", ondelete="CASCADE"), nullable=False, comment="貼文ID")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="留言者ID")
    content = Column(Text, nullable=False, comment="留言內容")
    is_deleted = Column(Boolean, default=False, nullable=False, comment="是否已刪除")
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    post = relationship("CommunityPost", back_populates="comments")
    user = relationship("User", back_populates="post_comments")

    # 索引
    __table_args__ = (
        Index('idx_post_id', 'post_id'),
        Index('idx_user_id', 'user_id'),
        Index('idx_created_at', 'created_at'),
        {'extend_existing': True}
    )

    def __repr__(self):
        return f"<PostComment(id={self.id}, post_id={self.post_id}, user_id={self.user_id})>"


class PostLike(Base):
    """貼文按讚"""
    __tablename__ = "post_likes"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("community_posts.id", ondelete="CASCADE"), nullable=False, comment="貼文ID")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="按讚者ID")
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    post = relationship("CommunityPost", back_populates="likes")
    user = relationship("User", back_populates="post_likes")

    # 唯一約束：每個用戶對每個貼文只能按讚一次
    __table_args__ = (
        UniqueConstraint('post_id', 'user_id', name='uq_post_user_like'),
        Index('idx_post_id', 'post_id'),
        Index('idx_user_id', 'user_id'),
        {'extend_existing': True}
    )

    def __repr__(self):
        return f"<PostLike(post_id={self.post_id}, user_id={self.user_id})>"
