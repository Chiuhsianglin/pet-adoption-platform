"""
Adoption Service
領養申請業務邏輯層
"""
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.repositories import AdoptionRepository, PetRepository, UserRepository
from app.models.adoption import AdoptionApplication, ApplicationStatus
from app.exceptions import (
    ApplicationNotFoundError,
    PetNotFoundError,
    UserNotFoundError,
    PermissionDeniedError,
    BusinessException,
    DuplicateApplicationError,
    InvalidStatusTransitionError
)


class AdoptionService:
    """領養申請業務邏輯"""
    
    def __init__(
        self,
        adoption_repo: AdoptionRepository,
        pet_repo: PetRepository,
        user_repo: UserRepository
    ):
        self.adoption_repo = adoption_repo
        self.pet_repo = pet_repo
        self.user_repo = user_repo
    
    async def create_draft(
        self,
        user_id: int,
        pet_id: int,
        application_data: Optional[Dict[str, Any]] = None
    ) -> AdoptionApplication:
        """創建領養申請草稿
        
        Args:
            user_id: 申請人 ID
            pet_id: 寵物 ID
            application_data: 可選的表單資料（personal_info, living_environment, pet_experience）
        """
        # 驗證寵物存在且可領養（使用 async/await）
        pet = await self.pet_repo.get_by_id(pet_id)
        if not pet:
            raise PetNotFoundError(f"寵物 ID {pet_id} 不存在")
        
        # 檢查寵物狀態（確保在 async context 內存取屬性）
        from app.models.pet import PetStatus
        is_available = False
        try:
            # 直接比較 enum
            is_available = (pet.status == PetStatus.AVAILABLE)
        except Exception as e:
            print(f"⚠️ Error checking pet status: {e}")
            is_available = False

        if not is_available:
            raise BusinessException(f"該寵物目前無法申請領養（狀態：{pet.status}）")
        
        # 檢查是否已有草稿
        existing = await self.adoption_repo.get_draft_by_user_and_pet(user_id, pet_id)
        if existing:
            # 如果提供了資料，更新現有草稿
            if application_data:
                if application_data.get("personal_info"):
                    existing.personal_info = application_data["personal_info"]
                if application_data.get("living_environment"):
                    existing.living_environment = application_data["living_environment"]
                if application_data.get("pet_experience"):
                    existing.pet_experience = application_data["pet_experience"]
                await self.adoption_repo.db.commit()
                await self.adoption_repo.db.refresh(existing)
            return existing
        
        # 生成 application_id
        import uuid
        application_id = f"APP{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}"
        
        # 準備 JSON 欄位資料（使用提供的資料或空物件）
        personal_info = {}
        living_environment = {}
        pet_experience = {}
        
        if application_data:
            personal_info = application_data.get("personal_info", {})
            living_environment = application_data.get("living_environment", {})
            pet_experience = application_data.get("pet_experience", {})
        
        # 創建草稿
        application = AdoptionApplication(
            application_id=application_id,
            applicant_id=user_id,
            pet_id=pet_id,
            shelter_id=pet.shelter_id,
            status=ApplicationStatus.DRAFT,
            personal_info=personal_info,
            living_environment=living_environment,
            pet_experience=pet_experience
        )
        
        return await self.adoption_repo.create(application)
    
    async def submit_application(
        self,
        application_id: int,
        user_id: int,
        application_data: Dict[str, Any]
    ) -> AdoptionApplication:
        """提交領養申請"""
        application = await self.adoption_repo.get_by_id_with_relations(application_id)
        if not application:
            raise ApplicationNotFoundError(f"申請 ID {application_id} 不存在")
        
        if application.applicant_id != user_id:
            raise PermissionDeniedError("您沒有權限修改此申請")
        
        if application.status != ApplicationStatus.DRAFT:
            raise InvalidStatusTransitionError("只能提交草稿狀態的申請")
        
        # 更新申請資料
        application.personal_info = application_data.get("personal_info")
        application.living_environment = application_data.get("living_environment")
        application.pet_experience = application_data.get("pet_experience")
        application.status = ApplicationStatus.SUBMITTED
        application.submitted_at = datetime.utcnow()
        
        return await self.adoption_repo.update(application_id, application)
    
    async def get_application(
        self,
        application_id: int,
        user_id: int
    ) -> AdoptionApplication:
        """獲取申請詳情"""
        application = await self.adoption_repo.get_by_id_with_relations(application_id)
        if not application:
            raise ApplicationNotFoundError(f"申請 ID {application_id} 不存在")
        
        # 權限檢查：只有申請人或收容所可查看
        if application.applicant_id != user_id and application.shelter_id != user_id:
            raise PermissionDeniedError("您沒有權限查看此申請")
        
        return application
    
    async def list_user_applications(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[AdoptionApplication]:
        """列出用戶的所有申請"""
        return await self.adoption_repo.get_user_applications(user_id, skip, limit)
    
    async def list_shelter_applications(
        self,
        shelter_id: int,
        status: Optional[ApplicationStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AdoptionApplication]:
        """列出收容所的申請（可按狀態篩選）"""
        return await self.adoption_repo.get_shelter_applications(
            shelter_id, status, skip, limit
        )
    
    async def update_status(
        self,
        application_id: int,
        new_status: ApplicationStatus,
        operator_id: int
    ) -> AdoptionApplication:
        """更新申請狀態（收容所操作）"""
        application = await self.adoption_repo.get_by_id_with_relations(application_id)
        if not application:
            raise ApplicationNotFoundError(f"申請 ID {application_id} 不存在")
        
        # 權限檢查：只有收容所可以更新狀態
        if application.shelter_id != operator_id:
            raise PermissionDeniedError("只有收容所可以更新申請狀態")
        
        # 狀態轉換驗證（可根據業務規則擴展）
        return await self.adoption_repo.update_status(application, new_status)
    
    async def withdraw_application(
        self,
        application_id: int,
        user_id: int
    ) -> AdoptionApplication:
        """撤回申請（申請人操作）"""
        application = await self.adoption_repo.get_by_id(application_id)
        if not application:
            raise ApplicationNotFoundError(f"申請 ID {application_id} 不存在")
        
        if application.applicant_id != user_id:
            raise PermissionDeniedError("只能撤回自己的申請")
        
        if application.status in [ApplicationStatus.COMPLETED, ApplicationStatus.WITHDRAWN]:
            raise InvalidStatusTransitionError("該申請無法撤回")
        
        return await self.adoption_repo.update_status(application, ApplicationStatus.WITHDRAWN)
    
    async def get_application_count(self, shelter_id: int, status: Optional[ApplicationStatus] = None) -> int:
        """獲取申請數量統計"""
        return await self.adoption_repo.count_by_shelter(shelter_id, status)
