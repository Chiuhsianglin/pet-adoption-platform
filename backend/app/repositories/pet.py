"""
Pet Repository
寵物資料存取層
"""
from typing import Optional, List, Dict, Any
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.pet import Pet, PetStatus, PetSpecies, PetSize, PetGender
from app.models.user import User


class PetRepository(BaseRepository[Pet]):
    """寵物 Repository"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Pet)
    
    async def get_by_id_with_shelter(self, pet_id: int) -> Optional[Pet]:
        """獲取寵物（包含收容所資訊）"""
        result = await self.db.execute(
            select(Pet)
            .options(selectinload(Pet.shelter), selectinload(Pet.photos))
            .where(Pet.id == pet_id)
        )
        return result.scalar_one_or_none()
    
    async def get_available_pets(
        self,
        skip: int = 0,
        limit: int = 100,
        species: Optional[PetSpecies] = None,
        size: Optional[PetSize] = None,
        gender: Optional[PetGender] = None
    ) -> List[Pet]:
        """獲取可領養的寵物（支援篩選）"""
        query = select(Pet).options(
            selectinload(Pet.photos),
            selectinload(Pet.shelter)
        ).where(Pet.status == PetStatus.AVAILABLE)
        
        if species:
            query = query.where(Pet.species == species)
        if size:
            query = query.where(Pet.size == size)
        if gender:
            query = query.where(Pet.gender == gender)
        
        query = query.order_by(Pet.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_shelter_pets(
        self,
        shelter_id: int,
        status: Optional[PetStatus] = None,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None
    ) -> List[Pet]:
        """獲取收容所的寵物"""
        query = select(Pet).options(
            selectinload(Pet.photos),
            selectinload(Pet.shelter)
        ).where(Pet.shelter_id == shelter_id)
        
        if status:
            query = query.where(Pet.status == status)
        
        if search:
            query = query.where(Pet.name.contains(search))
        
        query = query.order_by(Pet.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def search_pets(
        self,
        filters: Dict[str, Any],
        skip: int = 0,
        limit: int = 100
    ) -> List[Pet]:
        """搜尋寵物（支援多條件）"""
        query = self._build_search_query(filters)
        query = query.order_by(Pet.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def search_pets_with_count(
        self,
        filters: Dict[str, Any],
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Pet], int]:
        """搜尋寵物並返回總數"""
        # 建立基礎查詢
        base_query = self._build_search_query(filters)
        
        # 計算總數
        count_query = select(func.count()).select_from(
            base_query.alias()
        )
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # 取得分頁結果
        query = base_query.order_by(Pet.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        pets = result.scalars().all()
        
        return pets, total
    
    def _build_search_query(self, filters: Dict[str, Any]):
        """建立搜尋查詢"""
        query = select(Pet).options(
            selectinload(Pet.photos),
            selectinload(Pet.shelter)
        ).where(Pet.status == PetStatus.AVAILABLE)
        
        # 文字搜尋（搜尋名稱、品種、描述）
        if "query" in filters and filters["query"]:
            search_text = filters["query"]
            query = query.where(
                or_(
                    Pet.name.ilike(f"%{search_text}%"),
                    Pet.breed.ilike(f"%{search_text}%"),
                    Pet.description.ilike(f"%{search_text}%")
                )
            )
        
        # 基本篩選條件（支援單一值或陣列）
        if "species" in filters and filters["species"]:
            species_val = filters["species"]
            if isinstance(species_val, list):
                query = query.where(Pet.species.in_(species_val))
            else:
                query = query.where(Pet.species == species_val)
        
        if "size" in filters and filters["size"]:
            size_val = filters["size"]
            if isinstance(size_val, list):
                query = query.where(Pet.size.in_(size_val))
            else:
                query = query.where(Pet.size == size_val)
        
        if "gender" in filters and filters["gender"]:
            gender_val = filters["gender"]
            if isinstance(gender_val, list):
                query = query.where(Pet.gender.in_(gender_val))
            else:
                query = query.where(Pet.gender == gender_val)
        
        if "breed" in filters and filters["breed"]:
            query = query.where(Pet.breed.ilike(f"%{filters['breed']}%"))
        
        # 年齡範圍
        if "min_age_years" in filters and filters["min_age_years"] is not None:
            query = query.where(Pet.age_years >= filters["min_age_years"])
        
        if "max_age_years" in filters and filters["max_age_years"] is not None:
            query = query.where(Pet.age_years <= filters["max_age_years"])
        
        # 活力等級
        if "energy_level" in filters and filters["energy_level"]:
            energy_val = filters["energy_level"]
            if isinstance(energy_val, list):
                query = query.where(Pet.energy_level.in_(energy_val))
            else:
                query = query.where(Pet.energy_level == energy_val)
        
        # 領養費用上限
        if "max_adoption_fee" in filters and filters["max_adoption_fee"] is not None:
            query = query.where(Pet.adoption_fee <= filters["max_adoption_fee"])
        
        # 布林條件
        if "good_with_kids" in filters and filters["good_with_kids"]:
            query = query.where(Pet.good_with_kids == True)
        
        if "good_with_pets" in filters and filters["good_with_pets"]:
            query = query.where(Pet.good_with_pets == True)
        
        if "spayed_neutered" in filters and filters["spayed_neutered"]:
            query = query.where(Pet.spayed_neutered == True)
        
        return query
    
    async def update_status(
        self,
        pet: Pet,
        new_status: PetStatus
    ) -> Pet:
        """更新寵物狀態"""
        pet.status = new_status
        pet.updated_at = func.now()
        await self.db.commit()
        await self.db.refresh(pet)
        return pet
    
    async def count_by_shelter(
        self, 
        shelter_id: int, 
        status: Optional[PetStatus] = None,
        search: Optional[str] = None
    ) -> int:
        """計算收容所的寵物數量"""
        query = select(func.count()).select_from(Pet).where(
            Pet.shelter_id == shelter_id
        )
        
        if status:
            query = query.where(Pet.status == status)
        
        if search:
            query = query.where(Pet.name.contains(search))
        
        result = await self.db.execute(query)
        return result.scalar()
    
    async def count_available(self) -> int:
        """計算可領養寵物數量"""
        result = await self.db.execute(
            select(func.count())
            .select_from(Pet)
            .where(Pet.status == PetStatus.AVAILABLE)
        )
        return result.scalar()
    
    async def get_user_favorites(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Pet]:
        """獲取用戶收藏的寵物"""
        from app.models.user import user_favorites
        
        result = await self.db.execute(
            select(Pet)
            .join(user_favorites, Pet.id == user_favorites.c.pet_id)
            .where(user_favorites.c.user_id == user_id)
            .order_by(user_favorites.c.favorited_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def is_favorited_by_user(self, pet_id: int, user_id: int) -> bool:
        """檢查寵物是否被用戶收藏"""
        from app.models.user import user_favorites
        
        result = await self.db.execute(
            select(func.count())
            .select_from(user_favorites)
            .where(
                and_(
                    user_favorites.c.pet_id == pet_id,
                    user_favorites.c.user_id == user_id
                )
            )
        )
        return result.scalar() > 0
