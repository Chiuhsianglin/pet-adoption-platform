"""
Notification Service
通知業務邏輯層
"""
from typing import Optional, List
from datetime import datetime

from app.repositories import NotificationRepository
from app.models.notification import Notification, NotificationType
from app.exceptions import NotificationNotFoundError, PermissionDeniedError


class NotificationService:
    """通知業務邏輯"""
    
    def __init__(self, notification_repo: NotificationRepository):
        self.notification_repo = notification_repo
    
    async def get_user_notifications(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        unread_only: bool = False
    ) -> List[Notification]:
        """獲取用戶通知列表"""
        return await self.notification_repo.get_user_notifications(
            user_id, skip, limit, unread_only
        )
    
    async def get_unread_count(self, user_id: int) -> int:
        """獲取未讀通知數量"""
        return await self.notification_repo.get_unread_count(user_id)
    
    async def mark_as_read(
        self,
        notification_id: int,
        user_id: int
    ) -> bool:
        """標記通知為已讀"""
        notification = await self.notification_repo.get_by_id(notification_id)
        if not notification:
            raise NotificationNotFoundError(f"通知 ID {notification_id} 不存在")
        
        if notification.user_id != user_id:
            raise PermissionDeniedError("只能標記自己的通知")
        
        return await self.notification_repo.mark_as_read(notification_id, user_id)
    
    async def mark_all_as_read(self, user_id: int) -> int:
        """標記所有通知為已讀"""
        return await self.notification_repo.mark_all_as_read(user_id)
    
    async def create_notification(
        self,
        user_id: int,
        title: str,
        message: str,
        notification_type: NotificationType,
        link: Optional[str] = None
    ) -> Notification:
        """創建新通知"""
        return await self.notification_repo.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            link=link
        )
    
    async def delete_notification(
        self,
        notification_id: int,
        user_id: int
    ) -> bool:
        """刪除通知"""
        notification = await self.notification_repo.get_by_id(notification_id)
        if not notification:
            raise NotificationNotFoundError(f"通知 ID {notification_id} 不存在")
        
        if notification.user_id != user_id:
            raise PermissionDeniedError("只能刪除自己的通知")
        
        return await self.notification_repo.delete(notification_id)
    
    async def cleanup_old_notifications(
        self,
        user_id: int,
        days: int = 30
    ) -> int:
        """清理舊的已讀通知"""
        return await self.notification_repo.delete_old_read_notifications(user_id, days)
    
    async def get_by_type(
        self,
        user_id: int,
        notification_type: NotificationType,
        skip: int = 0,
        limit: int = 100
    ) -> List[Notification]:
        """根據類型獲取通知"""
        return await self.notification_repo.get_by_type(
            user_id, notification_type, skip, limit
        )
    
    # 業務邏輯：創建特定類型的通知
    
    async def notify_application_status_change(
        self,
        user_id: int,
        application_id: str,
        new_status: str
    ) -> Notification:
        """通知申請狀態變更"""
        status_messages = {
            "submitted": "您的領養申請已提交，收容所將盡快審核",
            "document_review": "您的申請文件正在審核中",
            "home_visit_scheduled": "您的家訪已安排",
            "approved": "恭喜！您的領養申請已通過",
            "rejected": "很抱歉，您的領養申請未通過審核",
            "completed": "領養流程已完成，感謝您給予寵物新的家"
        }
        
        message = status_messages.get(new_status, f"您的申請狀態已更新為：{new_status}")
        
        return await self.create_notification(
            user_id=user_id,
            title="領養申請狀態更新",
            message=message,
            notification_type=NotificationType.APPLICATION_STATUS,
            link=f"/applications/{application_id}"
        )
    
    async def notify_new_message(
        self,
        user_id: int,
        sender_name: str,
        room_id: int
    ) -> Notification:
        """通知新訊息"""
        return await self.create_notification(
            user_id=user_id,
            title="新訊息",
            message=f"{sender_name} 傳送了新訊息給您",
            notification_type=NotificationType.MESSAGE,
            link=f"/chat/{room_id}"
        )
    
    async def notify_post_interaction(
        self,
        user_id: int,
        interaction_type: str,
        actor_name: str,
        post_id: int
    ) -> Notification:
        """通知貼文互動（按讚、留言）"""
        type_map = {
            "like": (NotificationType.POST_LIKE, "按讚了您的貼文"),
            "comment": (NotificationType.POST_COMMENT, "留言了您的貼文")
        }
        
        notification_type, action = type_map.get(interaction_type, (NotificationType.SYSTEM, "與您的貼文互動"))
        
        return await self.create_notification(
            user_id=user_id,
            title="貼文互動",
            message=f"{actor_name} {action}",
            notification_type=notification_type,
            link=f"/community/posts/{post_id}"
        )
