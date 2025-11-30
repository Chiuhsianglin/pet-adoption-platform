"""
Adoption Repository
領養申請資料存取層
"""
from typing import Optional, List
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.adoption import AdoptionApplication, ApplicationStatus
from app.models.pet import Pet


class AdoptionRepository(BaseRepository[AdoptionApplication]):
    """領養申請 Repository"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, AdoptionApplication)
    
    async def get_by_id_with_relations(self, application_id: int) -> Optional[AdoptionApplication]:
        """獲取申請（包含關聯資料）"""
        from app.models.pet import Pet
        result = await self.db.execute(
            select(AdoptionApplication)
            .options(
                selectinload(AdoptionApplication.pet).selectinload(Pet.photos),
                selectinload(AdoptionApplication.applicant),
                selectinload(AdoptionApplication.shelter),
                selectinload(AdoptionApplication.documents)
                # 暫時移除 review_decision 因為資料庫欄位不匹配
                # selectinload(AdoptionApplication.review_decision)
            )
            .where(AdoptionApplication.id == application_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_application_id(self, application_id: str) -> Optional[AdoptionApplication]:
        """根據 application_id 查詢"""
        result = await self.db.execute(
            select(AdoptionApplication)
            .where(AdoptionApplication.application_id == application_id)
        )
        return result.scalar_one_or_none()
    
    async def get_draft_by_user_and_pet(
        self, 
        user_id: int, 
        pet_id: int
    ) -> Optional[AdoptionApplication]:
        """查詢用戶對特定寵物的草稿申請"""
        result = await self.db.execute(
            select(AdoptionApplication).where(
                and_(
                    AdoptionApplication.applicant_id == user_id,
                    AdoptionApplication.pet_id == pet_id,
                    AdoptionApplication.status == ApplicationStatus.DRAFT
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_user_applications(
        self, 
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[AdoptionApplication]:
        """獲取用戶的所有申請"""
        result = await self.db.execute(
            select(AdoptionApplication)
            .options(
                selectinload(AdoptionApplication.pet).selectinload(Pet.photos),
                selectinload(AdoptionApplication.documents),
                selectinload(AdoptionApplication.applicant)
            )
            .where(AdoptionApplication.applicant_id == user_id)
            .order_by(AdoptionApplication.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_shelter_applications(
        self,
        shelter_id: int,
        status: Optional[ApplicationStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AdoptionApplication]:
        """獲取收容所的申請（可按狀態篩選）"""
        query = (
            select(AdoptionApplication)
            .options(
                selectinload(AdoptionApplication.pet),
                selectinload(AdoptionApplication.applicant)
            )
            .where(AdoptionApplication.shelter_id == shelter_id)
        )
        
        if status:
            query = query.where(AdoptionApplication.status == status)
        
        query = query.order_by(AdoptionApplication.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_pet_applications(
        self,
        pet_id: int,
        exclude_draft: bool = True
    ) -> List[AdoptionApplication]:
        """獲取特定寵物的所有申請"""
        query = select(AdoptionApplication).where(
            AdoptionApplication.pet_id == pet_id
        )
        
        if exclude_draft:
            query = query.where(AdoptionApplication.status != ApplicationStatus.DRAFT)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def update_status(
        self,
        application: AdoptionApplication,
        new_status: ApplicationStatus
    ) -> AdoptionApplication:
        """更新申請狀態"""
        application.status = new_status
        application.updated_at = func.now()
        await self.db.commit()
        await self.db.refresh(application)
        return application
    
    async def count_by_shelter(self, shelter_id: int, status: Optional[ApplicationStatus] = None) -> int:
        """計算收容所的申請數量"""
        query = select(func.count()).select_from(AdoptionApplication).where(
            AdoptionApplication.shelter_id == shelter_id
        )
        
        if status:
            query = query.where(AdoptionApplication.status == status)
        
        result = await self.db.execute(query)
        return result.scalar()
    
    async def count_by_user(self, user_id: int) -> int:
        """計算用戶的申請數量"""
        result = await self.db.execute(
            select(func.count())
            .select_from(AdoptionApplication)
            .where(AdoptionApplication.applicant_id == user_id)
        )
        return result.scalar()
