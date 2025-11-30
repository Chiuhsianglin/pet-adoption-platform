"""
Notifications API V2 - 簡化版本
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth.dependencies import get_current_user, get_current_user_optional
from app.models.user import User
from app.services.factories import NotificationServiceFactory
from app.exceptions import NotificationNotFoundError, PermissionDeniedError

router = APIRouter()


def _serialize_notification(notif) -> Dict[str, Any]:
    """序列化通知"""
    return {
        "id": notif.id,
        "user_id": notif.user_id,
        "notification_type": notif.notification_type.value if hasattr(notif, 'notification_type') and notif.notification_type and hasattr(notif.notification_type, 'value') else str(notif.notification_type) if hasattr(notif, 'notification_type') else None,
        "title": notif.title,
        "message": notif.message,
        "is_read": notif.is_read,
        "link": notif.link if hasattr(notif, 'link') else None,
        "created_at": notif.created_at.isoformat() if notif.created_at else None,
    }


@router.get("/")
async def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    unread_only: bool = Query(False),
    current_user: User = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """獲取通知列表"""
    # 未登入用戶返回空結果
    if not current_user:
        return {
            "notifications": [],
            "total": 0,
            "unread_count": 0
        }
    
    try:
        service = NotificationServiceFactory.create(db)
        notifications = await service.get_user_notifications(
            current_user.id,
            skip=skip,
            limit=limit,
            unread_only=unread_only
        )
        
        # 獲取未讀數量
        unread_count = await service.get_unread_count(current_user.id)
        
        return {
            "notifications": [_serialize_notification(n) for n in notifications],
            "total": len(notifications),
            "unread_count": unread_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, int]:
    """獲取未讀數量"""
    # 未登入用戶返回 0
    if not current_user:
        return {"unread_count": 0}
    
    try:
        service = NotificationServiceFactory.create(db)
        count = await service.get_unread_count(current_user.id)
        return {"unread_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{notification_id}/read")
async def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """標記為已讀"""
    try:
        service = NotificationServiceFactory.create(db)
        await service.mark_as_read(notification_id, current_user.id)
        return {"message": "Marked as read"}
    except NotificationNotFoundError:
        raise HTTPException(status_code=404, detail="Notification not found")
    except PermissionDeniedError:
        raise HTTPException(status_code=403, detail="Permission denied")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mark-all-read")
async def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, int]:
    """標記全部已讀"""
    try:
        service = NotificationServiceFactory.create(db)
        count = await service.mark_all_as_read(current_user.id)
        return {"marked_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """刪除通知"""
    try:
        service = NotificationServiceFactory.create(db)
        await service.delete_notification(notification_id, current_user.id)
        return {"message": "Notification deleted"}
    except NotificationNotFoundError:
        raise HTTPException(status_code=404, detail="Notification not found")
    except PermissionDeniedError:
        raise HTTPException(status_code=403, detail="Permission denied")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
