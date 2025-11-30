"""
Password History Repository
密碼歷史記錄資料存取層
"""
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.password_history import PasswordHistory


class PasswordHistoryRepository(BaseRepository[PasswordHistory]):
    """密碼歷史 Repository"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, PasswordHistory)
    
    async def get_recent_passwords(
        self,
        user_id: int,
        limit: int = 5
    ) -> List[PasswordHistory]:
        """
        獲取用戶最近的密碼記錄
        
        Args:
            user_id: 用戶 ID
            limit: 返回數量限制
            
        Returns:
            密碼歷史記錄列表
        """
        result = await self.db.execute(
            select(PasswordHistory)
            .where(PasswordHistory.user_id == user_id)
            .order_by(PasswordHistory.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def count_by_user(self, user_id: int) -> int:
        """
        計算用戶的密碼記錄數量
        
        Args:
            user_id: 用戶 ID
            
        Returns:
            記錄數量
        """
        from sqlalchemy import func
        
        result = await self.db.execute(
            select(func.count())
            .select_from(PasswordHistory)
            .where(PasswordHistory.user_id == user_id)
        )
        return result.scalar() or 0
    
    async def delete_old_passwords(
        self,
        user_id: int,
        keep_recent: int = 10
    ) -> int:
        """
        刪除舊的密碼記錄，只保留最近的 N 條
        
        Args:
            user_id: 用戶 ID
            keep_recent: 保留最近的記錄數
            
        Returns:
            刪除的記錄數量
        """
        # 獲取要保留的記錄
        recent = await self.get_recent_passwords(user_id, keep_recent)
        if len(recent) < keep_recent:
            return 0
        
        # 獲取最舊保留記錄的時間
        oldest_kept = recent[-1]
        
        # 刪除更早的記錄
        from sqlalchemy import delete
        
        result = await self.db.execute(
            delete(PasswordHistory)
            .where(PasswordHistory.user_id == user_id)
            .where(PasswordHistory.created_at < oldest_kept.created_at)
        )
        
        await self.db.commit()
        return result.rowcount or 0
