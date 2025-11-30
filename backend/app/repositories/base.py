"""
Base Repository
基礎 Repository 提供通用 CRUD 操作
"""
from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import Base

T = TypeVar('T', bound=Base)


class BaseRepository(Generic[T]):
    """通用 Repository 基礎類別"""
    
    def __init__(self, db: AsyncSession, model: Type[T]):
        self.db = db
        self.model = model
    
    async def get_by_id(self, id: int) -> Optional[T]:
        """根據 ID 查詢單筆資料"""
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        order_by: Any = None
    ) -> List[T]:
        """查詢所有資料（分頁）"""
        query = select(self.model).offset(skip).limit(limit)
        if order_by is not None:
            query = query.order_by(order_by)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_by_field(
        self, 
        field_name: str, 
        field_value: Any
    ) -> Optional[T]:
        """根據欄位查詢單筆資料"""
        result = await self.db.execute(
            select(self.model).where(
                getattr(self.model, field_name) == field_value
            )
        )
        return result.scalar_one_or_none()
    
    async def get_all_by_field(
        self, 
        field_name: str, 
        field_value: Any,
        skip: int = 0,
        limit: int = 100
    ) -> List[T]:
        """根據欄位查詢多筆資料"""
        result = await self.db.execute(
            select(self.model)
            .where(getattr(self.model, field_name) == field_value)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def create(self, obj: T) -> T:
        """新增資料"""
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj
    
    async def update(self, obj: T) -> T:
        """更新資料"""
        await self.db.commit()
        await self.db.refresh(obj)
        return obj
    
    async def update_by_id(self, id: int, **kwargs) -> Optional[T]:
        """根據 ID 更新資料"""
        await self.db.execute(
            update(self.model)
            .where(self.model.id == id)
            .values(**kwargs)
        )
        await self.db.commit()
        return await self.get_by_id(id)
    
    async def delete(self, obj: T) -> None:
        """刪除資料"""
        await self.db.delete(obj)
        await self.db.commit()
    
    async def delete_by_id(self, id: int) -> bool:
        """根據 ID 刪除資料"""
        result = await self.db.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.db.commit()
        return result.rowcount > 0
    
    async def count(self, **filters) -> int:
        """計算符合條件的資料數量"""
        query = select(func.count()).select_from(self.model)
        for field, value in filters.items():
            query = query.where(getattr(self.model, field) == value)
        result = await self.db.execute(query)
        return result.scalar()
    
    async def exists(self, id: int) -> bool:
        """檢查資料是否存在"""
        result = await self.db.execute(
            select(func.count())
            .select_from(self.model)
            .where(self.model.id == id)
        )
        return result.scalar() > 0
