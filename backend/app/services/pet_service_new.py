"""
Pet Service (New Architecture)
寵物業務邏輯層 - 使用 Repository 模式
"""
from typing import Optional, List, Dict, Any, Tuple
from math import ceil

from app.repositories import PetRepository
from app.models.pet import Pet, PetStatus, PetSpecies, PetGender, PetSize, EnergyLevel
from app.exceptions import PetNotFoundError, PermissionDeniedError, InvalidStatusTransitionError


class PetService:
    """寵物業務邏輯"""
    
    def __init__(self, pet_repo: PetRepository):
        self.pet_repo = pet_repo
    
    async def get_pet(self, pet_id: int) -> Pet:
        """獲取寵物詳情"""
        pet = await self.pet_repo.get_by_id_with_shelter(pet_id)
        if not pet:
            raise PetNotFoundError(f"寵物 ID {pet_id} 不存在")
        return pet
    
    async def list_available_pets(
        self,
        page: int = 1,
        limit: int = 24,
        species: Optional[PetSpecies] = None,
        size: Optional[PetSize] = None,
        gender: Optional[PetGender] = None
    ) -> Tuple[List[Pet], int, int]:
        """列出可領養的寵物（支援分頁和篩選）"""
        skip = (page - 1) * limit
        
        pets = await self.pet_repo.get_available_pets(skip, limit, species, size, gender)
        total = await self.pet_repo.count_available()
        total_pages = ceil(total / limit) if limit > 0 else 1
        
        return pets, total, total_pages
    
    async def search_pets(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """搜尋寵物（支援多條件）"""
        page = int(filters.get("page", 1))
        limit = int(filters.get("limit", 24))
        skip = (page - 1) * limit
        
        # 從 filters 提取搜尋條件
        search_filters = {}
        
        if "query" in filters and filters["query"]:
            search_filters["query"] = filters["query"]
        if "species" in filters:
            search_filters["species"] = filters["species"]
        if "size" in filters:
            search_filters["size"] = filters["size"]
        if "gender" in filters:
            search_filters["gender"] = filters["gender"]
        if "breed" in filters:
            search_filters["breed"] = filters["breed"]
        if "min_age" in filters:
            search_filters["min_age_years"] = filters["min_age"]
        if "max_age" in filters:
            search_filters["max_age_years"] = filters["max_age"]
        if "min_age_years" in filters:
            search_filters["min_age_years"] = filters["min_age_years"]
        if "max_age_years" in filters:
            search_filters["max_age_years"] = filters["max_age_years"]
        if "good_with_kids" in filters:
            search_filters["good_with_kids"] = filters["good_with_kids"]
        if "good_with_pets" in filters:
            search_filters["good_with_pets"] = filters["good_with_pets"]
        if "spayed_neutered" in filters:
            search_filters["spayed_neutered"] = filters["spayed_neutered"]
        if "energy_level" in filters:
            search_filters["energy_level"] = filters["energy_level"]
        if "max_adoption_fee" in filters:
            search_filters["max_adoption_fee"] = filters["max_adoption_fee"]
        if "sort_by" in filters:
            search_filters["sort_by"] = filters["sort_by"]
        if "order" in filters:
            search_filters["order"] = filters["order"]
        
        # 搜尋寵物並計算總數
        pets, total = await self.pet_repo.search_pets_with_count(search_filters, skip, limit)
        total_pages = ceil(total / limit) if limit > 0 else 1
        
        return {
            "results": pets,
            "total": total,
            "page": page,
            "page_size": limit,
            "total_pages": total_pages,
            "applied_filters": filters
        }
    
    async def get_shelter_pets(
        self,
        shelter_id: int,
        status: Optional[PetStatus] = None,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None
    ) -> List[Pet]:
        """獲取收容所的寵物"""
        return await self.pet_repo.get_shelter_pets(shelter_id, status, skip, limit, search)
    
    async def count_shelter_pets(
        self,
        shelter_id: int,
        status: Optional[PetStatus] = None,
        search: Optional[str] = None
    ) -> int:
        """計算收容所的寵物數量"""
        return await self.pet_repo.count_by_shelter(shelter_id, status, search)
    
    async def create_pet(
        self,
        shelter_id: int,
        pet_data: Dict[str, Any],
        created_by: Optional[int] = None
    ) -> Pet:
        """創建寵物檔案（收容所操作）"""
        pet = Pet(
            shelter_id=shelter_id,
            created_by=created_by or shelter_id,
            status=PetStatus.AVAILABLE,  # 直接設為可領養，不需審核
            **pet_data
        )
        created_pet = await self.pet_repo.create(pet)
        
        # 重新加載以獲取關聯數據
        return await self.pet_repo.get_by_id_with_shelter(created_pet.id)
    
    async def update_pet(
        self,
        pet_id: int,
        shelter_id: int,
        pet_data: Dict[str, Any]
    ) -> Pet:
        """更新寵物資訊（收容所操作）"""
        pet = await self.pet_repo.get_by_id(pet_id)
        if not pet:
            raise PetNotFoundError(f"寵物 ID {pet_id} 不存在")
        
        if pet.shelter_id != shelter_id:
            raise PermissionDeniedError("只能修改自己收容所的寵物")
        
        return await self.pet_repo.update_by_id(pet_id, **pet_data)
    
    async def update_pet_status(
        self,
        pet_id: int,
        shelter_id: int,
        new_status: PetStatus
    ) -> Pet:
        """更新寵物狀態"""
        pet = await self.pet_repo.get_by_id(pet_id)
        if not pet:
            raise PetNotFoundError(f"寵物 ID {pet_id} 不存在")
        
        if pet.shelter_id != shelter_id:
            raise PermissionDeniedError("只能修改自己收容所的寵物狀態")
        
        return await self.pet_repo.update_status(pet, new_status)
    
    async def delete_pet(
        self,
        pet_id: int,
        shelter_id: int
    ) -> bool:
        """刪除寵物（收容所操作）"""
        from sqlalchemy import delete as sql_delete
        from app.models.pet import PetPhoto
        
        pet = await self.pet_repo.get_by_id(pet_id)
        if not pet:
            raise PetNotFoundError(f"寵物 ID {pet_id} 不存在")
        
        if pet.shelter_id != shelter_id:
            raise PermissionDeniedError("只能刪除自己收容所的寵物")
        
        # 先刪除關聯的照片
        delete_photos_stmt = sql_delete(PetPhoto).where(PetPhoto.pet_id == pet_id)
        await self.pet_repo.db.execute(delete_photos_stmt)
        await self.pet_repo.db.commit()
        
        # 再刪除寵物
        return await self.pet_repo.delete_by_id(pet_id)
    
    async def add_to_favorites(
        self,
        pet_id: int,
        user_id: int
    ) -> bool:
        """添加寵物到收藏"""
        pet = await self.pet_repo.get_by_id(pet_id)
        if not pet:
            raise PetNotFoundError(f"寵物 ID {pet_id} 不存在")
        
        # 這裡需要實作收藏邏輯（通常在 user_favorites 關聯表）
        # 暫時返回 True
        return True
    
    async def remove_from_favorites(
        self,
        pet_id: int,
        user_id: int
    ) -> bool:
        """從收藏移除寵物"""
        pet = await self.pet_repo.get_by_id(pet_id)
        if not pet:
            raise PetNotFoundError(f"寵物 ID {pet_id} 不存在")
        
        # 這裡需要實作取消收藏邏輯
        return True
    
    async def get_user_favorites(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Pet]:
        """獲取用戶收藏的寵物"""
        return await self.pet_repo.get_user_favorites(user_id, skip, limit)
    
    async def is_favorited(
        self,
        pet_id: int,
        user_id: int
    ) -> bool:
        """檢查寵物是否被收藏"""
        return await self.pet_repo.is_favorited_by_user(pet_id, user_id)
    
    async def get_filter_options(self) -> Dict[str, Any]:
        """獲取篩選選項（物種、性別、體型等）"""
        # 定義中文標籤映射
        species_labels = {
            "dog": "狗",
            "cat": "貓",
            "bird": "鳥",
            "rabbit": "兔子",
            "hamster": "倉鼠",
            "fish": "魚",
            "reptile": "爬蟲類",
            "other": "其他"
        }
        
        gender_labels = {
            "male": "公",
            "female": "母",
            "unknown": "未知"
        }
        
        size_labels = {
            "small": "小型",
            "medium": "中型",
            "large": "大型",
            "extra_large": "超大型"
        }
        
        energy_labels = {
            "low": "低",
            "medium": "中",
            "high": "高"
        }
        
        return {
            "species": [{"value": s.value, "label": species_labels.get(s.value, s.value)} for s in PetSpecies],
            "genders": [{"value": g.value, "label": gender_labels.get(g.value, g.value)} for g in PetGender],
            "sizes": [{"value": sz.value, "label": size_labels.get(sz.value, sz.value)} for sz in PetSize],
            "energy_levels": [{"value": e.value, "label": energy_labels.get(e.value, e.value)} for e in EnergyLevel]
        }
    
    async def get_shelter_stats(self, shelter_id: int) -> Dict[str, int]:
        """獲取收容所的寵物統計"""
        available_count = await self.pet_repo.count_by_shelter(shelter_id, PetStatus.AVAILABLE)
        pending_count = await self.pet_repo.count_by_shelter(shelter_id, PetStatus.PENDING)
        adopted_count = await self.pet_repo.count_by_shelter(shelter_id, PetStatus.ADOPTED)
        
        return {
            "available": available_count,
            "pending": pending_count,
            "adopted": adopted_count,
            "total": available_count + pending_count + adopted_count
        }
