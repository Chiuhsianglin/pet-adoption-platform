"""
Notification Repository
通知資料存取層
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.notification import Notification, NotificationType


class NotificationRepository(BaseRepository[Notification]):
    """通知 Repository"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Notification)
    
    async def get_user_notifications(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        unread_only: bool = False
    ) -> List[Notification]:
        """獲取用戶通知"""
        query = select(Notification).where(Notification.user_id == user_id)
        
        if unread_only:
            query = query.where(Notification.is_read == False)
        
        query = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_unread_count(self, user_id: int) -> int:
        """獲取未讀通知數量"""
        result = await self.db.execute(
            select(func.count())
            .select_from(Notification)
            .where(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False
                )
            )
        )
        return result.scalar()
    
    async def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """標記通知為已讀"""
        notification = await self.get_by_id(notification_id)
        if not notification or notification.user_id != user_id:
            return False
        
        notification.is_read = True
        await self.db.commit()
        return True
    
    async def mark_all_as_read(self, user_id: int) -> int:
        """標記所有通知為已讀"""
        from sqlalchemy import update
        
        stmt = (
            update(Notification)
            .where(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False
                )
            )
            .values(is_read=True)
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount
    
    async def create_notification(
        self,
        user_id: int,
        title: str,
        message: str,
        notification_type: NotificationType,
        link: Optional[str] = None
    ) -> Notification:
        """創建通知"""
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            link=link,
            is_read=False
        )
        return await self.create(notification)
    
    async def delete_old_read_notifications(self, user_id: int, days: int = 30) -> int:
        """刪除舊的已讀通知"""
        from datetime import timedelta
        from sqlalchemy import delete
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        stmt = (
            delete(Notification)
            .where(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == True,
                    Notification.read_at < cutoff_date
                )
            )
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount
    
    async def get_by_type(
        self,
        user_id: int,
        notification_type: NotificationType,
        skip: int = 0,
        limit: int = 100
    ) -> List[Notification]:
        """根據類型獲取通知"""
        result = await self.db.execute(
            select(Notification)
            .where(
                and_(
                    Notification.user_id == user_id,
                    Notification.notification_type == notification_type
                )
            )
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
