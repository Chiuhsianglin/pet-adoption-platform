"""
Community API V2 - Simplified Version
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel

from app.database import get_db
from app.auth.dependencies import get_current_user, get_current_user_optional
from app.models.user import User
from app.services.factories import CommunityServiceFactory, NotificationServiceFactory
from app.services.s3 import S3Service
from app.models.notification import NotificationType
from app.exceptions import (
    PostNotFoundError,
    CommentNotFoundError,
    PermissionDeniedError,
    ValidationError
)

router = APIRouter()


# ===== Request Models =====

class CreatePostRequest(BaseModel):
    content: str
    post_type: str
    photo_urls: Optional[List[str]] = None


class UpdatePostRequest(BaseModel):
    content: str


class CreateCommentRequest(BaseModel):
    content: str


class ReportPostRequest(BaseModel):
    reason: str


# ===== Serialization Functions =====

def _serialize_user(user) -> Dict[str, Any]:
    """Serialize user basic info"""
    if not user:
        return {"id": 0, "name": "Unknown", "email": ""}
    return {
        "id": user.id,
        "name": user.name or "Unknown",
        "email": user.email
    }


def _serialize_post(post, current_user_id: Optional[int] = None, s3_service=None) -> Dict[str, Any]:
    """Serialize post with user, photos, and stats"""
    # Serialize photos
    photos_data = []
    if hasattr(post, 'photos') and post.photos:
        for photo in post.photos:
            # 如果 file_key 已經是完整 URL（包含 http），直接使用
            if photo.file_key and (photo.file_key.startswith('http://') or photo.file_key.startswith('https://')):
                photo_url = photo.file_key
            elif photo.file_key and s3_service:
                # 否則生成預簽名 URL
                photo_url = s3_service.generate_presigned_url(photo.file_key, 604800)
            else:
                photo_url = ""
            
            photos_data.append({
                "id": photo.id,
                "post_id": photo.post_id,
                "file_key": photo.file_key,
                "display_order": photo.display_order,
                "photo_url": photo_url,
                "created_at": photo.created_at.isoformat() if photo.created_at else None
            })
    
    # Calculate stats
    like_count = len(post.likes) if hasattr(post, 'likes') and post.likes else 0
    comment_count = len([c for c in post.comments if not c.is_deleted]) if hasattr(post, 'comments') and post.comments else 0
    is_liked = False
    if current_user_id and hasattr(post, 'likes') and post.likes:
        is_liked = any(like.user_id == current_user_id for like in post.likes)
    
    return {
        "id": post.id,
        "user_id": post.user_id,
        "user": _serialize_user(post.user if hasattr(post, 'user') else None),
        "content": post.content,
        "post_type": post.post_type.value if hasattr(post.post_type, 'value') else post.post_type,
        "photos": photos_data,
        "like_count": like_count,
        "comment_count": comment_count,
        "is_liked": is_liked,
        "is_deleted": post.is_deleted,
        "created_at": post.created_at.isoformat() if post.created_at else None,
        "updated_at": post.updated_at.isoformat() if post.updated_at else None,
    }


def _serialize_comment(comment, current_user_id: Optional[int] = None) -> Dict[str, Any]:
    """Serialize comment with user info"""
    like_count = 0  # 留言按讚功能已移除
    is_liked = False
    
    return {
        "id": comment.id,
        "post_id": comment.post_id,
        "user_id": comment.user_id,
        "user": _serialize_user(comment.user if hasattr(comment, 'user') else None),
        "content": comment.content,
        "like_count": like_count,
        "is_liked": is_liked,
        "is_deleted": comment.is_deleted,
        "created_at": comment.created_at.isoformat() if comment.created_at else None,
    }


def _handle_error(error: Exception):
    """Handle errors"""
    if isinstance(error, (PostNotFoundError, CommentNotFoundError)):
        raise HTTPException(status_code=404, detail=str(error))
    elif isinstance(error, PermissionDeniedError):
        raise HTTPException(status_code=403, detail=str(error))
    elif isinstance(error, ValidationError):
        raise HTTPException(status_code=400, detail=str(error))
    else:
        raise HTTPException(status_code=500, detail=str(error))


# ===== API Endpoints =====

@router.post("/posts", status_code=status.HTTP_201_CREATED)
async def create_post(
    content: str = Form(...),
    post_type: str = Form(...),
    photos: List[UploadFile] = File(default=[]),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Create a new post with optional photo uploads"""
    try:
        service = CommunityServiceFactory.create(db)
        s3_service = S3Service()
        
        # 上傳照片到 S3
        photo_urls = []
        for photo in photos:
            if photo.filename:
                file_content = await photo.read()
                upload_result = s3_service.upload_file(
                    file_content,
                    photo.filename,
                    "community",
                    photo.content_type or "image/jpeg"
                )
                photo_urls.append(upload_result["file_url"])
        
        post = await service.create_post(
            current_user.id,
            content,
            post_type,
            photo_urls
        )
        return _serialize_post(post, current_user.id, s3_service)
    except Exception as e:
        _handle_error(e)


@router.get("/posts/my")
async def get_my_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get my posts"""
    try:
        service = CommunityServiceFactory.create(db)
        s3_service = S3Service()
        
        posts = await service.get_user_posts(current_user.id, skip, limit)
        
        serialized_posts = [_serialize_post(post, current_user.id, s3_service) for post in posts]
        has_more = len(posts) == limit
        
        return {
            "posts": serialized_posts,
            "total": len(serialized_posts),
            "has_more": has_more
        }
    except Exception as e:
        _handle_error(e)


@router.get("/posts/{post_id}")
async def get_post(
    post_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get post details"""
    try:
        service = CommunityServiceFactory.create(db)
        s3_service = S3Service()
        post = await service.get_post(post_id)
        user_id = current_user.id if current_user else None
        return _serialize_post(post, user_id, s3_service)
    except Exception as e:
        _handle_error(e)


@router.get("/posts")
async def list_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    post_type: Optional[str] = None,
    search: Optional[str] = None,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """List posts"""
    try:
        service = CommunityServiceFactory.create(db)
        s3_service = S3Service()
        
        # Calculate page
        page = (skip // limit) + 1
        
        result = await service.list_posts(
            page=page,
            limit=limit,
            post_type=post_type
        )
        
        user_id = current_user.id if current_user else None
        posts = [_serialize_post(post, user_id, s3_service) for post in result['results']]
        
        has_more = len(posts) == limit
        
        return {
            "posts": posts,
            "total": result['total'],
            "has_more": has_more
        }
    except Exception as e:
        _handle_error(e)


@router.put("/posts/{post_id}")
async def update_post(
    post_id: int,
    content: str = Form(...),
    post_type: Optional[str] = Form(None),
    delete_photo_ids: Optional[str] = Form(None),
    photos: Optional[List[UploadFile]] = File(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Update post content and optionally manage photos"""
    try:
        print(f"🔍 Update post {post_id} - User: {current_user.id}, Content length: {len(content)}")
        print(f"   post_type: {post_type}, delete_photo_ids: {delete_photo_ids}, photos: {photos}")
        
        service = CommunityServiceFactory.create(db)
        s3_service = S3Service()
        
        # 基本更新
        post = await service.update_post(
            post_id,
            current_user.id,
            content,
            post_type
        )
        print(f"✅ Post {post_id} updated successfully (type: {post_type})")
        
        # 重新獲取帶關聯的貼文（包含 photos）
        post = await service.get_post(post_id)
        
        # TODO: 處理照片刪除和新增
        # if delete_photo_ids:
        #     ids = json.loads(delete_photo_ids)
        #     await service.delete_post_photos(post_id, ids)
        #
        # if photos:
        #     for photo in photos:
        #         await service.add_post_photo(post_id, photo)
        
        return _serialize_post(post, current_user.id, s3_service)
    except Exception as e:
        print(f"❌ Update post failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        _handle_error(e)
        _handle_error(e)


@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Delete post"""
    try:
        service = CommunityServiceFactory.create(db)
        await service.delete_post(post_id, current_user.id)
        return {"message": "Post deleted"}
    except Exception as e:
        _handle_error(e)


@router.post("/posts/{post_id}/comments", status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: int,
    request: CreateCommentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Create comment"""
    try:
        print(f"🔍 Create comment on post {post_id} - User: {current_user.id}, Content: {request.content[:50]}...")
        service = CommunityServiceFactory.create(db)
        comment = await service.create_comment(
            post_id,
            current_user.id,
            request.content
        )
        
        # Get post to notify author
        post = await service.get_post(post_id)
        
        # Notify post author (if not commenting on own post)
        if post.user_id != current_user.id:
            notification_service = NotificationServiceFactory.create(db)
            await notification_service.create_notification(
                user_id=post.user_id,
                notification_type=NotificationType.SYSTEM,
                title="新的留言",
                message=f"{current_user.name or current_user.email} 在您的貼文留言了",
                link=f"/community/{post_id}"
            )
        
        print(f"✅ Comment created successfully")
        return _serialize_comment(comment, current_user.id)
    except Exception as e:
        print(f"❌ Create comment failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        _handle_error(e)


@router.get("/posts/{post_id}/comments")
async def get_comments(
    post_id: int,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get post comments"""
    try:
        service = CommunityServiceFactory.create(db)
        comments = await service.get_post_comments(post_id)
        user_id = current_user.id if current_user else None
        return {
            "comments": [_serialize_comment(c, user_id) for c in comments],
            "total": len(comments)
        }
    except Exception as e:
        _handle_error(e)


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Delete comment"""
    try:
        service = CommunityServiceFactory.create(db)
        await service.delete_comment(comment_id, current_user.id)
        return {"message": "Comment deleted"}
    except Exception as e:
        _handle_error(e)


@router.post("/posts/{post_id}/like")
async def like_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Like post"""
    try:
        print(f"🔍 Like post {post_id} - User: {current_user.id}")
        service = CommunityServiceFactory.create(db)
        await service.like_post(post_id, current_user.id)
        
        # Get latest stats
        post = await service.get_post(post_id)
        like_count = len(post.likes) if hasattr(post, 'likes') else 0
        
        # Notify post author (if not liking own post)
        if post.user_id != current_user.id:
            notification_service = NotificationServiceFactory.create(db)
            await notification_service.create_notification(
                user_id=post.user_id,
                notification_type=NotificationType.SYSTEM,
                title="新的按讚",
                message=f"{current_user.name or current_user.email} 按讚了您的貼文",
                link=f"/community/{post_id}"
            )
        
        print(f"✅ Post {post_id} liked successfully, total likes: {like_count}")
        return {
            "success": True,
            "is_liked": True,
            "like_count": like_count
        }
    except Exception as e:
        print(f"❌ Like post failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        _handle_error(e)


@router.delete("/posts/{post_id}/like")
async def unlike_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Unlike post"""
    try:
        print(f"🔍 Unlike post {post_id} - User: {current_user.id}")
        service = CommunityServiceFactory.create(db)
        await service.unlike_post(post_id, current_user.id)
        
        # Get latest stats
        post = await service.get_post(post_id)
        like_count = len(post.likes) if hasattr(post, 'likes') else 0
        
        print(f"✅ Post {post_id} unliked successfully, total likes: {like_count}")
        return {
            "success": True,
            "is_liked": False,
            "like_count": like_count
        }
    except Exception as e:
        print(f"❌ Unlike post failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        _handle_error(e)


@router.get("/posts/{post_id}/stats")
async def get_post_stats(
    post_id: int,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, int]:
    """Get post stats"""
    try:
        service = CommunityServiceFactory.create(db)
        stats = await service.get_post_stats(post_id)
        return stats
    except Exception as e:
        _handle_error(e)


@router.post("/posts/{post_id}/report", status_code=status.HTTP_201_CREATED)
async def report_post(
    post_id: int,
    request: ReportPostRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """Report post"""
    try:
        from app.models.post_report import PostReport
        from app.models.user import UserRole
        from app.models.notification import Notification, NotificationType
        from app.services.factories import NotificationServiceFactory
        
        # Check if already reported
        result = await db.execute(
            select(PostReport).where(
                and_(
                    PostReport.post_id == post_id,
                    PostReport.reporter_id == current_user.id
                )
            )
        )
        existing_report = result.scalar_one_or_none()
        
        if existing_report:
            raise HTTPException(status_code=400, detail="You have already reported this post")
        
        # Get post details for notification
        service = CommunityServiceFactory.create(db)
        post = await service.get_post(post_id)
        
        # Create report record
        report = PostReport(
            post_id=post_id,
            reporter_id=current_user.id,
            reason=request.reason
        )
        db.add(report)
        await db.commit()
        
        # Notify all admins
        admin_result = await db.execute(
            select(User).where(User.role == UserRole.admin)
        )
        admins = admin_result.scalars().all()
        
        notification_service = NotificationServiceFactory.create(db)
        for admin in admins:
            await notification_service.create_notification(
                user_id=admin.id,
                notification_type=NotificationType.SYSTEM,
                title="新的貼文檢舉",
                message=f"用戶 {current_user.name or current_user.email} 檢舉了一則貼文",
                link=f"/community/{post_id}"
            )
        
        return {"message": "Report submitted"}
    except HTTPException:
        raise
    except Exception as e:
        _handle_error(e)
