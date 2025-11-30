"""
Pets API V2 - 簡化版本（使用 dict 返回，不依賴複雜schema）
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import inspect
from pydantic import BaseModel

from app.database import get_db
from app.auth.dependencies import get_current_user_optional, get_current_user
from app.models.user import User
from app.services.factories import PetServiceFactory
from app.services.s3 import S3Service
from app.exceptions import PetNotFoundError

router = APIRouter()

# 初始化 S3 服務
s3_service = S3Service()


def _get_shelter_name(pet) -> Optional[str]:
    """安全獲取 shelter name，避免延遲加載"""
    try:
        # 檢查 shelter 關聯是否已加載
        insp = inspect(pet)
        shelter_state = insp.attrs.shelter
        
        # 如果 shelter 已加載到內存中，直接返回
        if not shelter_state.loaded_value:
            return None
        
        shelter = shelter_state.loaded_value
        return shelter.name if shelter else None
    except Exception:
        # Fallback: 如果檢查失敗，返回 None
        return None


def _serialize_pet(pet, include_photos: bool = False) -> Dict[str, Any]:
    """序列化寵物對象"""
    from app.core.config import settings
    
    # 獲取主照片並動態生成簽名 URL
    primary_photo_url = None
    if hasattr(pet, 'primary_photo') and pet.primary_photo:
        if hasattr(pet.primary_photo, 'file_key') and pet.primary_photo.file_key:
            if s3_service.use_s3 and s3_service.s3_client:
                try:
                    # 總是生成新的預簽名 URL（24小時有效期）
                    primary_photo_url = s3_service.generate_presigned_url(
                        pet.primary_photo.file_key, 
                        expiration=86400  # 24 小時
                    )
                except Exception as e:
                    print(f"⚠️ Failed to generate presigned URL for primary photo: {e}")
                    # Fallback: 嘗試使用原始 URL 或構建本地路徑
                    primary_photo_url = getattr(pet.primary_photo, 'file_url', None)
    elif hasattr(pet, 'photos') and pet.photos and len(pet.photos) > 0:
        if hasattr(pet.photos[0], 'file_key') and pet.photos[0].file_key:
            if s3_service.use_s3 and s3_service.s3_client:
                try:
                    primary_photo_url = s3_service.generate_presigned_url(
                        pet.photos[0].file_key,
                        expiration=86400  # 24 小時
                    )
                except Exception as e:
                    print(f"⚠️ Failed to generate presigned URL for first photo: {e}")
                    primary_photo_url = getattr(pet.photos[0], 'file_url', None)
    
    # 序列化所有照片（如果需要）
    photos_list = []
    if include_photos and hasattr(pet, 'photos') and pet.photos:
        for photo in pet.photos:
            file_url = None
            if hasattr(photo, 'file_key') and photo.file_key:
                if s3_service.use_s3 and s3_service.s3_client:
                    try:
                        # 總是生成新的預簽名 URL（24小時有效期）
                        file_url = s3_service.generate_presigned_url(
                            photo.file_key,
                            expiration=86400  # 24 小時
                        )
                    except Exception as e:
                        print(f"⚠️ Failed to generate presigned URL for {photo.file_key}: {e}")
                        file_url = getattr(photo, 'file_url', None)
                else:
                    # S3 未啟用，使用原始 URL
                    file_url = getattr(photo, 'file_url', None)
            
            photos_list.append({
                "id": photo.id,
                "file_url": file_url,
                "file_key": photo.file_key if hasattr(photo, 'file_key') else None,
                "is_primary": photo.is_primary if hasattr(photo, 'is_primary') else False,
            })
    
    result = {
        "id": pet.id,
        "name": pet.name,
        "species": pet.species.value if hasattr(pet.species, 'value') else pet.species,
        "breed": pet.breed,
        "gender": pet.gender.value if hasattr(pet.gender, 'value') else pet.gender,
        "age_years": pet.age_years,
        "age_months": pet.age_months,
        "size": pet.size.value if hasattr(pet.size, 'value') else pet.size,
        "color": pet.color if hasattr(pet, 'color') else None,
        "weight_kg": float(pet.weight_kg) if pet.weight_kg else None,
        "description": pet.description,
        "medical_info": pet.medical_info if hasattr(pet, 'medical_info') else None,
        "health_status": pet.medical_info if hasattr(pet, 'medical_info') else None,  # 前端兼容性
        "behavioral_info": pet.behavioral_info if hasattr(pet, 'behavioral_info') else None,
        "status": pet.status.value if hasattr(pet.status, 'value') else pet.status,
        "adoption_fee": float(pet.adoption_fee) if pet.adoption_fee else None,
        "primary_photo_url": primary_photo_url,
        "good_with_kids": pet.good_with_kids,
        "good_with_pets": pet.good_with_pets,
        "house_trained": pet.house_trained if hasattr(pet, 'house_trained') else None,
        "energy_level": pet.energy_level.value if hasattr(pet, 'energy_level') and pet.energy_level and hasattr(pet.energy_level, 'value') else None,
        "vaccination_status": pet.vaccination_status,
        "spayed_neutered": pet.spayed_neutered,
        "sterilized": pet.spayed_neutered,  # 前端兼容性
        "special_needs": pet.special_needs if hasattr(pet, 'special_needs') else None,
        "microchip_id": pet.microchip_id if hasattr(pet, 'microchip_id') else None,
        "shelter_id": pet.shelter_id if hasattr(pet, 'shelter_id') else None,
        "shelter_name": _get_shelter_name(pet),
        "created_at": pet.created_at.isoformat() if pet.created_at else None,
        "updated_at": pet.updated_at.isoformat() if pet.updated_at else None,
    }
    
    # 只在詳細視圖時包含完整照片陣列
    if include_photos:
        result["photos"] = photos_list
    
    return result


@router.get("/")
async def list_pets(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    species: Optional[str] = None,
    size: Optional[str] = None,
    gender: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    列出可領養的寵物
    
    使用新的 Service 層架構
    """
    try:
        service = PetServiceFactory.create(db)
        
        # PetService.list_available_pets 返回 (pets, total, total_pages)
        pets, total, total_pages = await service.list_available_pets(
            page=page,
            limit=page_size,
            species=species,
            size=size,
            gender=gender
        )
        
        return {
            "items": [_serialize_pet(pet) for pet in pets],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/my-pets")
async def get_my_pets(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    獲取收容所管理的寵物
    
    - 只有收容所可以使用
    - 可按狀態篩選
    - 可按名稱搜尋
    - 返回格式：{pets: [], pagination: {page, limit, total, pages}}
    """
    from app.models.user import UserRole
    from app.models.pet import PetStatus
    
    # 驗證用戶角色
    if current_user.role != UserRole.shelter:
        raise HTTPException(status_code=403, detail="只有收容所可以查看管理的寵物")
    
    try:
        service = PetServiceFactory.create(db)
        
        # 轉換狀態參數
        status_filter = None
        if status:
            try:
                status_filter = PetStatus(status)
            except ValueError:
                pass
        
        # 獲取寵物列表
        skip = (page - 1) * limit
        pets = await service.get_shelter_pets(
            current_user.id,
            status_filter,
            skip,
            limit,
            search
        )
        
        # 獲取總數
        total = await service.count_shelter_pets(current_user.id, status_filter, search)
        total_pages = (total + limit - 1) // limit if limit > 0 else 1
        
        # 序列化寵物數據
        pets_data = [_serialize_pet(pet, include_photos=True) for pet in pets]
        
        return {
            "pets": pets_data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "pages": total_pages
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_pet(
    pet_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    創建新的寵物檔案
    
    - 只有收容所可以使用
    - 返回創建的寵物數據
    """
    from app.models.user import UserRole
    from app.models.pet import PetStatus
    
    # 驗證用戶角色
    if current_user.role != UserRole.shelter:
        raise HTTPException(status_code=403, detail="只有收容所可以創建寵物檔案")
    
    try:
        service = PetServiceFactory.create(db)
        
        # 驗證必填字段
        required_fields = ['name', 'species', 'gender']
        missing_fields = [f for f in required_fields if not pet_data.get(f)]
        if missing_fields:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required fields: {', '.join(missing_fields)}"
            )
        
        # 字段映射：前端 -> 資料庫
        field_mapping = {
            'sterilized': 'spayed_neutered',
            'health_status': 'medical_info',  # 健康狀況 -> 醫療資訊
        }
        
        # 轉換字段名
        for frontend_field, db_field in field_mapping.items():
            if frontend_field in pet_data:
                pet_data[db_field] = pet_data.pop(frontend_field)
        
        # 移除無效字段（不在 Pet 模型中的字段）
        valid_fields = {
            'name', 'species', 'breed', 'gender', 'age_years', 'age_months',
            'size', 'weight_kg', 'color', 'description', 'medical_info',
            'behavioral_info', 'vaccination_status', 'spayed_neutered',
            'special_needs', 'microchip_id', 'house_trained', 'good_with_kids',
            'good_with_pets', 'energy_level', 'adoption_fee'
        }
        pet_data = {k: v for k, v in pet_data.items() if k in valid_fields}
        
        # 清理數據：將空字符串轉換為 None（針對數字和布林字段）
        numeric_fields = {'weight_kg', 'age_years', 'age_months', 'adoption_fee'}
        boolean_fields = {'spayed_neutered', 'house_trained', 'good_with_kids', 'good_with_pets'}
        
        for field in numeric_fields:
            if field in pet_data and pet_data[field] == '':
                pet_data[field] = None
        
        for field in boolean_fields:
            if field in pet_data and pet_data[field] == '':
                pet_data[field] = None
        
        # 創建寵物
        pet = await service.create_pet(
            shelter_id=current_user.id,
            pet_data=pet_data,
            created_by=current_user.id
        )
        
        # 序列化並返回
        return _serialize_pet(pet, include_photos=True)
        
    except Exception as e:
        print(f"❌ 創建寵物失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{pet_id}")
async def update_pet(
    pet_id: int,
    pet_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    更新寵物資訊
    
    - 只有收容所可以更新自己的寵物
    - 返回更新後的寵物數據
    """
    from app.models.user import UserRole
    
    # 驗證用戶角色
    if current_user.role != UserRole.shelter:
        raise HTTPException(status_code=403, detail="只有收容所可以更新寵物檔案")
    
    try:
        service = PetServiceFactory.create(db)
        
        # 驗證寵物存在
        try:
            existing_pet = await service.get_pet(pet_id)
        except PetNotFoundError:
            raise HTTPException(status_code=404, detail="Pet not found")
        
        # 驗證權限
        if existing_pet.shelter_id != current_user.id:
            raise HTTPException(status_code=403, detail="只能更新自己收容所的寵物")
        
        # 字段映射：前端 -> 資料庫
        field_mapping = {
            'sterilized': 'spayed_neutered',
            'health_status': 'medical_info',  # 健康狀況 -> 醫療資訊
        }
        
        # 轉換字段名
        for frontend_field, db_field in field_mapping.items():
            if frontend_field in pet_data:
                pet_data[db_field] = pet_data.pop(frontend_field)
        
        # 移除無效字段
        valid_fields = {
            'name', 'species', 'breed', 'gender', 'age_years', 'age_months',
            'size', 'weight_kg', 'color', 'description', 'medical_info',
            'behavioral_info', 'vaccination_status', 'spayed_neutered',
            'special_needs', 'microchip_id', 'house_trained', 'good_with_kids',
            'good_with_pets', 'energy_level', 'adoption_fee', 'status'
        }
        pet_data = {k: v for k, v in pet_data.items() if k in valid_fields}
        
        # 清理數據：將空字符串轉換為 None
        numeric_fields = {'weight_kg', 'age_years', 'age_months', 'adoption_fee'}
        boolean_fields = {'spayed_neutered', 'house_trained', 'good_with_kids', 'good_with_pets'}
        
        for field in numeric_fields:
            if field in pet_data and pet_data[field] == '':
                pet_data[field] = None
        
        for field in boolean_fields:
            if field in pet_data and pet_data[field] == '':
                pet_data[field] = None
        
        # 更新寵物
        updated_pet = await service.update_pet(
            pet_id=pet_id,
            shelter_id=current_user.id,
            pet_data=pet_data
        )
        
        # 序列化並返回
        return _serialize_pet(updated_pet, include_photos=True)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 更新寵物失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{pet_id}/status")
async def update_pet_status(
    pet_id: int,
    status_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    更新寵物狀態
    
    - 收容所可以更新自己寵物的狀態
    """
    from app.models.user import UserRole
    from app.models.pet import PetStatus
    
    # 驗證用戶角色
    if current_user.role != UserRole.shelter:
        raise HTTPException(status_code=403, detail="只有收容所可以更新寵物狀態")
    
    try:
        service = PetServiceFactory.create(db)
        
        # 驗證寵物存在
        try:
            existing_pet = await service.get_pet(pet_id)
        except PetNotFoundError:
            raise HTTPException(status_code=404, detail="Pet not found")
        
        # 驗證權限
        if existing_pet.shelter_id != current_user.id:
            raise HTTPException(status_code=403, detail="只能更新自己收容所的寵物")
        
        # 獲取新狀態
        new_status_str = status_data.get('status')
        if not new_status_str:
            raise HTTPException(status_code=400, detail="Missing status field")
        
        # 轉換為 PetStatus enum
        try:
            new_status = PetStatus(new_status_str)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {new_status_str}")
        
        # 更新狀態
        updated_pet = await service.update_pet_status(
            pet_id=pet_id,
            shelter_id=current_user.id,
            new_status=new_status
        )
        
        # 序列化並返回
        return _serialize_pet(updated_pet, include_photos=True)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 更新寵物狀態失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{pet_id}")
async def delete_pet(
    pet_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    刪除寵物
    
    - 只有收容所可以刪除自己的寵物
    """
    from app.models.user import UserRole
    
    # 驗證用戶角色
    if current_user.role != UserRole.shelter:
        raise HTTPException(status_code=403, detail="只有收容所可以刪除寵物檔案")
    
    try:
        service = PetServiceFactory.create(db)
        
        # 驗證寵物存在
        try:
            existing_pet = await service.get_pet(pet_id)
        except PetNotFoundError:
            raise HTTPException(status_code=404, detail="Pet not found")
        
        # 驗證權限
        if existing_pet.shelter_id != current_user.id:
            raise HTTPException(status_code=403, detail="只能刪除自己收容所的寵物")
        
        # 刪除寵物
        await service.delete_pet(pet_id, current_user.id)
        
        return {"message": "Pet deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 刪除寵物失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/favorites")
async def get_user_favorites(
    skip: int = Query(0, ge=0),
    limit: int = Query(12, ge=1, le=100),
    current_user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    獲取當前用戶的收藏寵物列表
    
    - 已登入：返回該用戶的收藏
    - 未登入：返回空列表（不觸發 401 錯誤）
    """
    from sqlalchemy import select, func
    from sqlalchemy.orm import selectinload
    from app.models.notification import UserFavorite
    from app.models.pet import Pet
    
    # 未登入用戶返回空結果
    if not current_user:
        return {
            "data": {
                "items": [],
                "total": 0,
                "skip": skip,
                "limit": limit,
            }
        }
    
    try:
        user_id = current_user.id
        
        # 統計總收藏數
        count_query = select(func.count(UserFavorite.pet_id)).where(UserFavorite.user_id == user_id)
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查詢收藏列表（預加載寵物、照片、收容所）
        query = (
            select(UserFavorite, Pet)
            .join(Pet, UserFavorite.pet_id == Pet.id)
            .options(
                selectinload(Pet.photos),
                selectinload(Pet.shelter)
            )
            .where(UserFavorite.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .order_by(UserFavorite.created_at.desc())
        )
        
        result = await db.execute(query)
        favorites_with_pets = result.all()
        
        # 序列化收藏項目
        items = []
        for favorite, pet in favorites_with_pets:
            # 獲取主照片 URL
            primary_photo_url = None
            if hasattr(pet, 'photos') and pet.photos:
                for photo in pet.photos:
                    if getattr(photo, 'is_primary', False):
                        if hasattr(photo, 'file_key') and photo.file_key:
                            try:
                                primary_photo_url = s3_service.generate_presigned_url(
                                    photo.file_key,
                                    expiration=604800
                                )
                            except Exception:
                                pass
                        break
                
                # 如果沒有主照片，使用第一張
                if not primary_photo_url and len(pet.photos) > 0:
                    first_photo = pet.photos[0]
                    if hasattr(first_photo, 'file_key') and first_photo.file_key:
                        try:
                            primary_photo_url = s3_service.generate_presigned_url(
                                first_photo.file_key,
                                expiration=604800
                            )
                        except Exception:
                            pass
            
            items.append({
                "pet_id": favorite.pet_id,
                "created_at": favorite.created_at.isoformat() if favorite.created_at else None,
                "pet_name": pet.name,
                "pet_species": pet.species.value if hasattr(pet.species, 'value') else str(pet.species),
                "pet_status": pet.status.value if hasattr(pet.status, 'value') else str(pet.status),
                "pet_breed": pet.breed,
                "pet_age_years": pet.age_years,
                "pet_age_months": pet.age_months,
                "pet_gender": pet.gender.value if hasattr(pet.gender, 'value') else str(pet.gender),
                "pet_size": pet.size.value if hasattr(pet.size, 'value') else str(pet.size),
                "pet_photo_url": primary_photo_url,
                "adoption_fee": float(pet.adoption_fee) if pet.adoption_fee else 0.0,
                "location": getattr(pet, 'location', None),
            })
        
        return {
            "data": {
                "items": items,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{pet_id}")
async def get_pet(
    pet_id: int,
    current_user = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    獲取單個寵物詳情
    
    返回格式與 V1 兼容: {"data": {...}}
    """
    try:
        from app.models.notification import UserFavorite
        from sqlalchemy import select
        
        service = PetServiceFactory.create(db)
        pet = await service.get_pet(pet_id)
        
        # 序列化寵物資料，包含完整照片陣列
        pet_data = _serialize_pet(pet, include_photos=True)
        
        # 檢查是否已收藏（如果用戶已登入）
        is_favorited = False
        if current_user:
            fav_check = select(UserFavorite).where(
                UserFavorite.user_id == current_user.id,
                UserFavorite.pet_id == pet_id
            )
            result = await db.execute(fav_check)
            is_favorited = result.scalar_one_or_none() is not None
        
        pet_data["is_favorited"] = is_favorited
        
        # 返回與 V1 兼容的格式
        return {"data": pet_data}
    except PetNotFoundError:
        raise HTTPException(status_code=404, detail="Pet not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{pet_id}/favorite")
async def add_to_favorites(
    pet_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """添加寵物到收藏（需要認證）"""
    from sqlalchemy import insert, select
    from app.models.notification import UserFavorite
    
    try:
        # 驗證寵物是否存在
        service = PetServiceFactory.create(db)
        pet = await service.get_pet(pet_id)
        
        user_id = current_user.id
        
        # 檢查是否已收藏
        query = select(UserFavorite).where(
            UserFavorite.user_id == user_id,
            UserFavorite.pet_id == pet_id
        )
        result = await db.execute(query)
        existing = result.scalar_one_or_none()
        
        if existing:
            return {"message": "Already in favorites", "pet_id": pet_id}
        
        # 添加到收藏
        stmt = insert(UserFavorite).values(user_id=user_id, pet_id=pet_id)
        await db.execute(stmt)
        await db.commit()
        
        return {"message": "Added to favorites", "pet_id": pet_id}
    except PetNotFoundError:
        raise HTTPException(status_code=404, detail="Pet not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{pet_id}/favorite")
async def remove_from_favorites(
    pet_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """從收藏中移除寵物（需要認證）"""
    from sqlalchemy import delete as sql_delete
    from app.models.notification import UserFavorite
    
    try:
        user_id = current_user.id
        
        stmt = sql_delete(UserFavorite).where(
            UserFavorite.user_id == user_id,
            UserFavorite.pet_id == pet_id
        )
        result = await db.execute(stmt)
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Favorite not found")
        
        await db.commit()
        
        return {"message": "Removed from favorites", "pet_id": pet_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class SearchPetsRequest(BaseModel):
    query: Optional[str] = None
    species: Optional[List[str]] = None
    size: Optional[List[str]] = None
    gender: Optional[str] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    spayed_neutered: Optional[bool] = None
    good_with_kids: Optional[bool] = None
    good_with_pets: Optional[bool] = None
    energy_level: Optional[str] = None
    max_adoption_fee: Optional[float] = None
    skip: Optional[int] = 0
    limit: Optional[int] = 20
    page: Optional[int] = 1
    page_size: Optional[int] = 20


@router.post("/search")
async def search_pets(
    request: SearchPetsRequest,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    搜尋寵物
    """
    try:
        service = PetServiceFactory.create(db)
        
        # 構建 filters 字典（Service 期望的格式）
        filters = {
            'page': request.page,
            'limit': request.page_size or request.limit
        }
        
        if request.query:
            filters['query'] = request.query
        if request.species:
            filters['species'] = request.species
        if request.size:
            filters['size'] = request.size
        if request.gender and request.gender != 'all':
            filters['gender'] = request.gender
        if request.min_age is not None:
            filters['min_age'] = request.min_age
        if request.max_age is not None:
            filters['max_age'] = request.max_age
        if request.spayed_neutered is not None:
            filters['spayed_neutered'] = request.spayed_neutered
        if request.good_with_kids is not None:
            filters['good_with_kids'] = request.good_with_kids
        if request.good_with_pets is not None:
            filters['good_with_pets'] = request.good_with_pets
        if request.energy_level:
            filters['energy_level'] = request.energy_level
        if request.max_adoption_fee is not None:
            filters['max_adoption_fee'] = request.max_adoption_fee
            
        result = await service.search_pets(filters)
        
        return {
            "items": [_serialize_pet(pet) for pet in result['results']],
            "total": result['total'],
            "page": result['page'],
            "page_size": result['page_size'],
            "total_pages": result['total_pages'],
            "results": [_serialize_pet(pet) for pet in result['results']]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{pet_id}/photos/link")
async def link_pet_photos(
    pet_id: int,
    payload: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Link uploaded photos to a pet"""
    from sqlalchemy import insert, select, func
    from app.models.pet import PetPhoto
    
    try:
        print(f"📸 Linking photos to pet {pet_id}")
        print(f"📦 Payload: {payload}")
        
        service = PetServiceFactory.create(db)
        
        # Verify pet exists and user has permission
        try:
            pet = await service.get_pet(pet_id)
        except PetNotFoundError:
            raise HTTPException(status_code=404, detail="Pet not found")
        
        # Check if user owns the pet
        if pet.shelter_id != current_user.id and pet.created_by != current_user.id:
            raise HTTPException(status_code=403, detail="You don't have permission to manage photos for this pet")
        
        photos = payload.get("photos", [])
        if not photos:
            print("⚠️  No photos provided in payload")
            return {"message": "No photos to link", "data": []}
        
        print(f"📷 Processing {len(photos)} photos")
        
        # Get current photo count
        count_query = select(func.count(PetPhoto.id)).where(PetPhoto.pet_id == pet_id)
        count_result = await db.execute(count_query)
        current_count = count_result.scalar() or 0
        
        linked_photos = []
        
        for idx, photo_data in enumerate(photos):
            file_url = photo_data.get("url") or photo_data.get("file_url")
            if not file_url:
                print(f"⚠️  Photo {idx} missing file_url, skipping")
                continue
            
            # Extract file_key from URL or use URL as key
            file_key = photo_data.get("file_key") or file_url.split("/")[-2:] 
            if isinstance(file_key, list):
                file_key = "/".join(file_key)
            
            # First photo is primary
            is_primary = (current_count == 0 and idx == 0)
            
            photo_insert_data = {
                "pet_id": pet_id,
                "file_url": file_url,
                "file_key": file_key,
                "is_primary": is_primary,
                "upload_order": current_count + idx,
            }
            
            print(f"💾 Inserting photo {idx}: {file_key[:50]}...")
            
            stmt = insert(PetPhoto).values(**photo_insert_data)
            result = await db.execute(stmt)
            await db.commit()
            
            photo_id = result.inserted_primary_key[0]
            linked_photos.append({
                "id": photo_id,
                "file_url": file_url,
                "is_primary": is_primary
            })
            
            print(f"✅ Photo {idx} linked successfully (ID: {photo_id})")
        
        print(f"✅ Successfully linked {len(linked_photos)} photos to pet {pet_id}")
        
        return {
            "message": f"Successfully linked {len(linked_photos)} photos",
            "data": linked_photos
        }
    
    except Exception as e:
        print(f"❌ Failed to link photos: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/filters/options")
async def get_filter_options(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    獲取篩選選項
    """
    try:
        service = PetServiceFactory.create(db)
        options = await service.get_filter_options()
        return options
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
