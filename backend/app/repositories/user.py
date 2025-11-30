"""
User Repository
用戶資料存取層
"""
from typing import Optional, List
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.user import User, UserRole


class UserRepository(BaseRepository[User]):
    """用戶 Repository"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, User)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """根據 email 查詢用戶"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """根據 username 查詢用戶"""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def email_exists(self, email: str, exclude_user_id: Optional[int] = None) -> bool:
        """檢查 email 是否已存在"""
        query = select(func.count()).select_from(User).where(User.email == email)
        
        if exclude_user_id:
            query = query.where(User.id != exclude_user_id)
        
        result = await self.db.execute(query)
        return result.scalar() > 0
    
    async def username_exists(self, username: str, exclude_user_id: Optional[int] = None) -> bool:
        """檢查 username 是否已存在"""
        query = select(func.count()).select_from(User).where(User.username == username)
        
        if exclude_user_id:
            query = query.where(User.id != exclude_user_id)
        
        result = await self.db.execute(query)
        return result.scalar() > 0
    
    async def get_by_role(self, role: UserRole, skip: int = 0, limit: int = 100) -> List[User]:
        """根據角色查詢用戶"""
        result = await self.db.execute(
            select(User)
            .where(User.role == role)
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """獲取活躍用戶"""
        result = await self.db.execute(
            select(User)
            .where(User.is_active == True)
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def search_users(
        self,
        search_term: str,
        role: Optional[UserRole] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """搜尋用戶（支援 email、username、full_name）"""
        query = select(User).where(
            or_(
                User.email.ilike(f"%{search_term}%"),
                User.username.ilike(f"%{search_term}%"),
                User.full_name.ilike(f"%{search_term}%")
            )
        )
        
        if role:
            query = query.where(User.role == role)
        
        query = query.order_by(User.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_last_login(self, user_id: int) -> bool:
        """更新最後登入時間"""
        from datetime import datetime
        
        user = await self.get_by_id(user_id)
        if not user:
            return False
        
        user.last_login = datetime.utcnow()
        await self.db.commit()
        return True
    
    async def get_shelter_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """獲取收容所用戶"""
        return await self.get_by_role(UserRole.SHELTER, skip, limit)
    
    async def get_admin_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """獲取管理員用戶"""
        return await self.get_by_role(UserRole.ADMIN, skip, limit)
    
    async def count_by_role(self, role: UserRole) -> int:
        """計算特定角色的用戶數量"""
        result = await self.db.execute(
            select(func.count())
            .select_from(User)
            .where(User.role == role)
        )
        return result.scalar()
    
    async def deactivate_user(self, user_id: int) -> bool:
        """停用用戶"""
        user = await self.get_by_id(user_id)
        if not user:
            return False
        
        user.is_active = False
        await self.db.commit()
        return True
    
    async def activate_user(self, user_id: int) -> bool:
        """啟用用戶"""
        user = await self.get_by_id(user_id)
        if not user:
            return False
        
        user.is_active = True
        await self.db.commit()
        return True
