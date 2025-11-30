"""
Adoptions API V2 - 簡化版本
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Body, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User, UserRole
from app.services.factories import AdoptionServiceFactory
from app.exceptions import (
    ApplicationNotFoundError,
    PetNotFoundError,
    PermissionDeniedError,
    DuplicateApplicationError,
    InvalidStatusTransitionError
)

router = APIRouter()


def _serialize_application(app) -> Dict[str, Any]:
    """序列化領養申請"""
    # 從 JSON 欄位提取數據
    living_env = app.living_environment if hasattr(app, 'living_environment') and app.living_environment else {}
    pet_exp = app.pet_experience if hasattr(app, 'pet_experience') and app.pet_experience else {}
    personal = app.personal_info if hasattr(app, 'personal_info') and app.personal_info else {}
    
    # 序列化 pet 信息
    pet_data = None
    if hasattr(app, 'pet') and app.pet:
        from app.services.s3 import S3Service
        from app.core.config import settings
        import traceback
        
        s3_service = S3Service()
        pet = app.pet
        
        # 序列化所有照片
        photos_data = []
        if hasattr(pet, 'photos') and pet.photos:
            print(f"\n🔍 Generating URLs for {len(pet.photos)} photos:")
            print(f"   USE_S3: {settings.USE_S3}")
            print(f"   S3 Client exists: {s3_service.s3_client is not None}")
            
            for photo in pet.photos:
                file_url = None
                file_key = photo.file_key if hasattr(photo, 'file_key') else None
                
                if file_key:
                    try:
                        print(f"   🔑 Generating URL for: {file_key}")
                        file_url = s3_service.generate_presigned_url(
                            file_key,
                            expiration=604800  # 7 天
                        )
                        if file_url:
                            print(f"   ✅ URL generated (length: {len(file_url)})")
                        else:
                            print(f"   ⚠️ URL is None (S3 may be disabled or error occurred)")
                    except Exception as e:
                        print(f"   ❌ Failed to generate presigned URL for {file_key}:")
                        print(f"      Error: {e}")
                        traceback.print_exc()
                else:
                    print(f"   ⚠️ Photo {photo.id} has no file_key")
                
                photos_data.append({
                    "id": photo.id,
                    "file_url": file_url,
                    "file_key": file_key,
                    "is_primary": photo.is_primary if hasattr(photo, 'is_primary') else False,
                })
        
        pet_data = {
            "id": pet.id,
            "name": pet.name,
            "species": pet.species.value if hasattr(pet.species, 'value') else pet.species,
            "breed": pet.breed,
            "age_years": pet.age_years,
            "age_months": pet.age_months,
            "gender": pet.gender.value if hasattr(pet.gender, 'value') else pet.gender,
            "size": pet.size.value if hasattr(pet.size, 'value') else pet.size,
            "status": pet.status.value if hasattr(pet.status, 'value') else pet.status,
            "photos": photos_data,
        }
    
    # 序列化 documents 信息
    documents_data = []
    if hasattr(app, 'documents') and app.documents:
        from app.services.s3 import S3Service
        
        s3_service = S3Service()
        
        for doc in app.documents:
            # 總是嘗試生成新的預簽名 URL（如果使用 S3）
            file_url = None
            
            if doc.file_key:
                if s3_service.use_s3 and s3_service.s3_client:
                    # S3 模式，生成預簽名 URL
                    try:
                        file_url = s3_service.generate_presigned_url(doc.file_key, expiration=86400)
                    except Exception as e:
                        print(f"⚠️ Failed to generate presigned URL for document {doc.file_key}: {e}")
                        file_url = doc.file_url if hasattr(doc, 'file_url') else None
                else:
                    # S3 未啟用，使用原始 URL
                    file_url = doc.file_url if hasattr(doc, 'file_url') else None
            else:
                # 沒有 file_key，使用原始 URL
                file_url = doc.file_url if hasattr(doc, 'file_url') else None
            
            documents_data.append({
                "id": doc.id,
                "document_type": doc.document_type.value if hasattr(doc.document_type, 'value') else doc.document_type,
                "file_url": file_url,
                "file_name": doc.file_name if hasattr(doc, 'file_name') else None,
                "original_filename": doc.original_filename if hasattr(doc, 'original_filename') else None,
                "mime_type": doc.mime_type if hasattr(doc, 'mime_type') else None,
                "status": doc.status.value if hasattr(doc, 'status') and hasattr(doc.status, 'value') else (doc.status if hasattr(doc, 'status') else None),
                "uploaded_at": doc.uploaded_at.isoformat() if hasattr(doc, 'uploaded_at') and doc.uploaded_at else None,
            })
    
    # 處理 living_environment 中的 environment_photos
    if isinstance(living_env, dict) and 'environment_photos' in living_env:
        from app.services.s3 import S3Service
        s3_service = S3Service()
        
        print(f"🏠 處理 {len(living_env.get('environment_photos', []))} 張居住環境照片")
        
        updated_photos = []
        for photo in living_env.get('environment_photos', []):
            if isinstance(photo, dict):
                file_key = photo.get('file_key')
                if file_key and s3_service.use_s3 and s3_service.s3_client:
                    try:
                        # 生成新的預簽名 URL（24小時）
                        new_url = s3_service.generate_presigned_url(file_key, expiration=86400)
                        photo['file_url'] = new_url
                        photo['url'] = new_url  # 兼容性
                        print(f"   ✅ 環境照片 URL 已更新: {file_key[:50]}...")
                    except Exception as e:
                        print(f"   ❌ 生成環境照片 URL 失敗: {e}")
                updated_photos.append(photo)
        
        living_env['environment_photos'] = updated_photos
    
    # 處理 home_visit_document
    home_visit_doc_url = None
    if hasattr(app, 'home_visit_document') and app.home_visit_document:
        from app.services.s3 import S3Service
        s3_service = S3Service()
        
        if s3_service.use_s3 and s3_service.s3_client:
            try:
                home_visit_doc_url = s3_service.generate_presigned_url(app.home_visit_document, expiration=86400)
                print(f"   ✅ 家訪文件 URL 已生成")
            except Exception as e:
                print(f"   ❌ 生成家訪文件 URL 失敗: {e}")
    
    # 序列化申請人資訊
    user_data = None
    if hasattr(app, 'applicant') and app.applicant:
        user = app.applicant
        user_data = {
            "id": user.id,
            "name": user.name if hasattr(user, 'name') else None,
            "email": user.email if hasattr(user, 'email') else None,
            "phone": user.phone if hasattr(user, 'phone') else None,
        }
    
    return {
        "id": app.id,
        "application_id": app.application_id,
        "pet_id": app.pet_id,
        "applicant_id": app.applicant_id,
        "shelter_id": app.shelter_id,
        "status": app.status.value if hasattr(app.status, 'value') else app.status,
        "living_space": living_env.get('living_space') if isinstance(living_env, dict) else None,
        "has_other_pets": pet_exp.get('has_other_pets') if isinstance(pet_exp, dict) else None,
        "experience_level": pet_exp.get('experience_level') if isinstance(pet_exp, dict) else None,
        "reason_for_adoption": personal.get('reason_for_adoption') if isinstance(personal, dict) else None,
        "submitted_at": app.submitted_at.isoformat() if app.submitted_at else None,
        "created_at": app.created_at.isoformat() if app.created_at else None,
        "updated_at": app.updated_at.isoformat() if app.updated_at else None,
        "personal_info": personal,
        "living_environment": living_env,
        "pet_experience": pet_exp,
        "pet": pet_data,
        "user": user_data,
        "documents": documents_data,
        "home_visit_date": app.home_visit_date.isoformat() if hasattr(app, 'home_visit_date') and app.home_visit_date else None,
        "home_visit_notes": app.home_visit_notes if hasattr(app, 'home_visit_notes') else None,
        "home_visit_document": home_visit_doc_url,
        "final_decision_notes": app.final_decision_notes if hasattr(app, 'final_decision_notes') else None,
    }


def _handle_error(error: Exception):
    """處理 Service 層例外"""
    if isinstance(error, ApplicationNotFoundError):
        raise HTTPException(status_code=404, detail=str(error))
    elif isinstance(error, PetNotFoundError):
        raise HTTPException(status_code=404, detail=str(error))
    elif isinstance(error, PermissionDeniedError):
        raise HTTPException(status_code=403, detail=str(error))
    elif isinstance(error, DuplicateApplicationError):
        raise HTTPException(status_code=400, detail=str(error))
    elif isinstance(error, InvalidStatusTransitionError):
        raise HTTPException(status_code=400, detail=str(error))
    else:
        raise HTTPException(status_code=500, detail=str(error))


@router.post("/applications", status_code=status.HTTP_201_CREATED)
async def create_draft_application(
    pet_id: Optional[int] = Query(None, description="Pet ID (can be provided as query or in JSON body)"),
    application_body: Optional[Dict[str, Any]] = Body(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """創建草稿申請或直接建立完整申請

    支援兩種請求格式：
    - Query param: `POST /applications?pet_id=123` （建立空草稿）
    - JSON body: `{ "pet_id": 123, "personal_info": {...}, ... }` （建立草稿並填入資料）
    """
    try:
        # 支援從 body 拿 pet_id（前端可能會傳整個表單物件）
        resolved_pet_id = pet_id
        if not resolved_pet_id and application_body:
            try:
                resolved_pet_id = int(application_body.get("pet_id")) if application_body.get("pet_id") is not None else None
            except Exception:
                resolved_pet_id = None

        if not resolved_pet_id:
            raise HTTPException(status_code=400, detail="pet_id is required (query or JSON body)")

        service = AdoptionServiceFactory.create(db)
        
        # 檢查 body 是否包含完整的表單資料
        application_data = None
        if application_body:
            # 提取表單資料（如果存在）
            has_form_data = (
                application_body.get("personal_info") or 
                application_body.get("living_environment") or 
                application_body.get("pet_experience")
            )
            if has_form_data:
                application_data = {
                    "personal_info": application_body.get("personal_info", {}),
                    "living_environment": application_body.get("living_environment", {}),
                    "pet_experience": application_body.get("pet_experience", {})
                }
        
        # 建立草稿（帶或不帶資料）
        print(f"🔍 Creating draft: user_id={current_user.id}, pet_id={resolved_pet_id}, has_data={application_data is not None}")
        if application_data:
            print(f"📝 Application data keys: {list(application_data.keys())}")
        
        application = await service.create_draft(current_user.id, resolved_pet_id, application_data)
        print(f"✅ Draft created: id={application.id}, application_id={application.application_id}")
        
        serialized = _serialize_application(application)
        print(f"✅ Serialization complete")
        return serialized
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ create_draft_application error: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        _handle_error(e)


@router.put("/applications/{application_id}")
async def submit_application(
    application_id: int,
    application_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """提交申請"""
    try:
        service = AdoptionServiceFactory.create(db)
        # service.submit_application signature: (application_id, user_id, application_data)
        application = await service.submit_application(
            application_id,
            current_user.id,
            application_data
        )
        return _serialize_application(application)
    except Exception as e:
        _handle_error(e)


@router.get("/applications/{application_id}")
async def get_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """獲取申請詳情"""
    try:
        service = AdoptionServiceFactory.create(db)
        application = await service.get_application(application_id, current_user.id)
        return _serialize_application(application)
    except Exception as e:
        _handle_error(e)


@router.get("/applications")
async def list_applications(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """列出申請（根據角色）"""
    try:
        print(f"🔍 List applications - User: {current_user.id}, Role: {current_user.role}, Status filter: {status}")
        service = AdoptionServiceFactory.create(db)
        
        if current_user.role == UserRole.adopter:
            applications = await service.list_user_applications(
                current_user.id
            )
        elif current_user.role == UserRole.shelter:
            applications = await service.list_shelter_applications(
                current_user.id,
                status=status
            )
        else:
            raise HTTPException(status_code=403, detail="Invalid role")
        
        print(f"✅ Found {len(applications)} applications")
        # 返回格式與前端兼容
        return {
            "applications": [_serialize_application(app) for app in applications],
            "total": len(applications)
        }
    except Exception as e:
        print(f"❌ List applications failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        _handle_error(e)


@router.patch("/applications/{application_id}/status")
async def update_application_status(
    application_id: int,
    new_status: str,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """更新申請狀態"""
    try:
        service = AdoptionServiceFactory.create(db)
        application = await service.update_status(
            current_user.id,
            application_id,
            new_status,
            notes
        )
        return _serialize_application(application)
    except Exception as e:
        _handle_error(e)


@router.post("/applications/{application_id}/withdraw")
async def withdraw_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """撤回申請"""
    try:
        service = AdoptionServiceFactory.create(db)
        application = await service.withdraw_application(
            current_user.id,
            application_id
        )
        return _serialize_application(application)
    except Exception as e:
        _handle_error(e)


# ==================== Shelter Review APIs ====================

@router.get("/shelter/applications")
async def get_shelter_applications(
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """獲取收容所的申請列表"""
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.models.pet import Pet
    from app.models.adoption import AdoptionApplication, ApplicationStatus
    from datetime import datetime
    
    if current_user.role != UserRole.shelter:
        raise HTTPException(status_code=403, detail="Only shelter users can access this")
    
    # 獲取收容所的寵物 IDs
    pets_query = select(Pet.id).where(Pet.shelter_id == current_user.id)
    pets_result = await db.execute(pets_query)
    pet_ids = [row[0] for row in pets_result.fetchall()]
    
    if not pet_ids:
        return []
    
    # 查詢申請
    query = select(AdoptionApplication).options(
        selectinload(AdoptionApplication.pet).selectinload(Pet.photos),
        selectinload(AdoptionApplication.applicant),
        selectinload(AdoptionApplication.documents)
    ).where(
        AdoptionApplication.pet_id.in_(pet_ids),
        AdoptionApplication.status != ApplicationStatus.DRAFT
    )
    
    if status:
        try:
            status_enum = ApplicationStatus(status)
            query = query.where(AdoptionApplication.status == status_enum)
        except ValueError:
            pass
    
    if search:
        from app.models.user import User as UserModel
        query = query.join(UserModel, AdoptionApplication.applicant_id == UserModel.id)
        query = query.join(Pet, AdoptionApplication.pet_id == Pet.id)
        search_term = f"%{search}%"
        query = query.where(
            (UserModel.name.ilike(search_term)) |
            (Pet.name.ilike(search_term))
        )
    
    result = await db.execute(query)
    applications = result.unique().scalars().all()
    
    # 排序
    applications = sorted(
        applications,
        key=lambda x: x.created_at if x.created_at else datetime.min,
        reverse=True
    )
    
    # 序列化
    return [_serialize_application(app) for app in applications]


@router.get("/applications/{application_id}/documents")
async def get_application_documents(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """獲取申請文件"""
    from sqlalchemy import select
    from app.models.adoption import ApplicationDocument, AdoptionApplication
    from app.models.pet import Pet
    from app.services.s3 import S3Service
    
    # 驗證權限
    app_query = select(AdoptionApplication).where(AdoptionApplication.id == application_id)
    app_result = await db.execute(app_query)
    application = app_result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # 檢查權限
    pet_query = select(Pet).where(Pet.id == application.pet_id)
    pet_result = await db.execute(pet_query)
    pet = pet_result.scalar_one_or_none()
    
    if current_user.id != application.applicant_id and (not pet or pet.shelter_id != current_user.id):
        raise HTTPException(status_code=403, detail="No permission")
    
    # 獲取文件
    docs_query = select(ApplicationDocument).where(
        ApplicationDocument.application_id == application_id
    ).order_by(ApplicationDocument.created_at.desc())
    
    docs_result = await db.execute(docs_query)
    documents = docs_result.scalars().all()
    
    # 生成預簽名 URL
    s3_service = S3Service()
    docs_data = []
    
    print(f"🔍 處理 {len(documents)} 個文件")
    print(f"   S3 狀態: USE_S3={s3_service.use_s3}")
    
    for doc in documents:
        print(f"  📄 文件: {doc.file_name}")
        print(f"     - file_key: {doc.file_key}")
        
        # 總是嘗試生成新的預簽名 URL（如果使用 S3）
        presigned_url = None
        
        if doc.file_key:
            if s3_service.use_s3 and s3_service.s3_client:
                try:
                    # 生成新的預簽名 URL（24小時有效期）
                    presigned_url = s3_service.generate_presigned_url(doc.file_key, expiration=86400)
                    print(f"     - ✅ S3 預簽名 URL 已生成（24小時）")
                except Exception as e:
                    print(f"     - ❌ S3 預簽名失敗: {e}")
                    import traceback
                    traceback.print_exc()
                    # Fallback 使用原始 URL
                    presigned_url = doc.file_url
            else:
                # S3 未啟用，使用原始 URL
                print(f"     - ℹ️ S3 未啟用，使用原始 URL")
                presigned_url = doc.file_url
        else:
            # 沒有 file_key，使用原始 URL
            print(f"     - ⚠️ 無 file_key，使用原始 URL")
            presigned_url = doc.file_url
        
        docs_data.append({
            "id": doc.id,
            "application_id": doc.application_id,
            "document_type": doc.document_type,
            "file_name": doc.file_name,
            "original_filename": doc.original_filename or doc.file_name,
            "file_url": presigned_url,
            "file_key": doc.file_key,
            "file_size": doc.file_size,
            "mime_type": doc.mime_type,
            "uploaded_at": doc.uploaded_at.isoformat() if doc.uploaded_at else None,
            "created_at": doc.created_at.isoformat() if doc.created_at else None,
        })
    
    required_types = ['identity', 'income', 'residence']
    uploaded_types = list(set([d["document_type"] for d in docs_data]))
    missing = [t for t in required_types if t not in uploaded_types]
    
    return {
        "documents": docs_data,
        "required_documents": required_types,
        "completed_documents": uploaded_types,
        "missing_documents": missing,
        "completion_percentage": int((len(uploaded_types) / len(required_types)) * 100) if required_types else 100,
        "total_size": sum(d["file_size"] or 0 for d in docs_data)
    }


@router.post("/applications/{application_id}/request-documents")
async def request_documents(
    application_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """通知申請者補充文件"""
    from datetime import datetime
    from sqlalchemy import select
    from app.models.pet import Pet
    from app.models.adoption import AdoptionApplication, ApplicationStatus
    from app.models.notification import Notification
    from datetime import timezone as dt_timezone
    
    print(f"📄 通知補件:")
    print(f"   Application ID: {application_id}")
    print(f"   Current User: {current_user.email} (role: {current_user.role})")
    
    if current_user.role != UserRole.shelter:
        print(f"   ❌ 權限錯誤: 只有 shelter 可以通知補件")
        raise HTTPException(status_code=403, detail="Only shelter can request documents")
    
    app_query = select(AdoptionApplication).where(AdoptionApplication.id == application_id)
    result = await db.execute(app_query)
    application = result.scalar_one_or_none()
    
    if not application:
        print(f"   ❌ 申請不存在: {application_id}")
        raise HTTPException(status_code=404, detail="Application not found")
    
    pet_query = select(Pet).where(Pet.id == application.pet_id)
    pet_result = await db.execute(pet_query)
    pet = pet_result.scalar_one_or_none()
    
    if not pet or pet.shelter_id != current_user.id:
        print(f"   ❌ 權限錯誤: 寵物不屬於此 shelter")
        raise HTTPException(status_code=403, detail="No permission")
    
    # Check status - should be in submitted or document_review
    allowed_statuses = [ApplicationStatus.SUBMITTED, ApplicationStatus.DOCUMENT_REVIEW]
    if application.status not in allowed_statuses:
        print(f"   ❌ 狀態錯誤: {application.status}")
        raise HTTPException(status_code=400, detail=f"Cannot request documents for status: {application.status}")
    
    # Update status to document_review if currently submitted
    if application.status == ApplicationStatus.SUBMITTED:
        application.status = ApplicationStatus.DOCUMENT_REVIEW
    
    application.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(application)
    
    print(f"   ✅ 補件通知已發送")
    
    # Send notification to applicant
    notification = Notification(
        user_id=application.applicant_id,
        title="請補充文件",
        message=f"您的申請文件（申請編號 #{application.id}）尚未上傳完整。請至「我的申請」頁面上傳所需文件，以便我們進行審核。感謝您的配合！",
        created_at=datetime.now(dt_timezone.utc)
    )
    db.add(notification)
    await db.commit()
    
    return {
        "message": "Document request notification sent",
        "application_id": application.id,
        "status": application.status.value
    }


@router.post("/applications/{application_id}/schedule-home-visit")
async def schedule_home_visit(
    application_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """安排家訪"""
    from datetime import datetime
    from sqlalchemy import select
    from app.models.pet import Pet
    from app.models.adoption import AdoptionApplication, ApplicationStatus
    from app.models.notification import Notification
    from datetime import timezone as dt_timezone
    
    # 讀取請求 body
    try:
        body = await request.json()
        print(f"🏠 安排家訪請求:")
        print(f"   Application ID: {application_id}")
        print(f"   Request Body: {body}")
        print(f"   Body Type: {type(body)}")
        
        # 嘗試多種方式提取日期
        home_visit_date = None
        if isinstance(body, dict):
            home_visit_date = body.get('home_visit_date') or body.get('homeVisitDate') or body.get('date')
        elif isinstance(body, str):
            home_visit_date = body
        
        if not home_visit_date:
            print(f"   ❌ 無法從請求中提取日期")
            raise HTTPException(status_code=422, detail="Missing home_visit_date in request body")
        
        print(f"   Home Visit Date: {home_visit_date}")
        print(f"   Date Type: {type(home_visit_date)}")
    except Exception as e:
        print(f"   ❌ 解析請求失敗: {e}")
        raise HTTPException(status_code=422, detail=f"Invalid request format: {str(e)}")
    
    print(f"   Current User: {current_user.email} (role: {current_user.role})")
    
    if current_user.role != UserRole.shelter:
        print(f"   ❌ 權限錯誤: 只有 shelter 可以安排家訪")
        raise HTTPException(status_code=403, detail="Only shelter can schedule")
    
    app_query = select(AdoptionApplication).where(AdoptionApplication.id == application_id)
    result = await db.execute(app_query)
    application = result.scalar_one_or_none()
    
    if not application:
        print(f"   ❌ 申請不存在: {application_id}")
        raise HTTPException(status_code=404, detail="Not found")
    
    pet_query = select(Pet).where(Pet.id == application.pet_id)
    pet_result = await db.execute(pet_query)
    pet = pet_result.scalar_one_or_none()
    
    if not pet or pet.shelter_id != current_user.id:
        print(f"   ❌ 權限錯誤: 寵物不屬於此 shelter")
        raise HTTPException(status_code=403, detail="No permission")
    
    print(f"   當前狀態: {application.status}")
    if application.status not in [ApplicationStatus.SUBMITTED, ApplicationStatus.DOCUMENT_REVIEW, ApplicationStatus.HOME_VISIT_SCHEDULED]:
        print(f"   ❌ 狀態錯誤: 無法在此狀態安排家訪")
        raise HTTPException(status_code=400, detail=f"Invalid status: {application.status}")
    
    # Accept multiple common date formats
    visit_date = None
    # Try ISO format first (handles '2025-11-27T15:00:00' and with timezone Z)
    try:
        iso_input = home_visit_date.replace("Z", "+00:00") if isinstance(home_visit_date, str) else home_visit_date
        visit_date = datetime.fromisoformat(iso_input)
        print(f"   ✅ 日期解析成功 (ISO): {visit_date}")
    except Exception as e1:
        print(f"   ⚠️ ISO 格式解析失敗: {e1}")
        try:
            visit_date = datetime.strptime(home_visit_date, "%Y-%m-%d %H:%M")
            print(f"   ✅ 日期解析成功 (YYYY-MM-DD HH:MM): {visit_date}")
        except Exception as e2:
            print(f"   ❌ 日期格式錯誤: {e2}")
            raise HTTPException(status_code=400, detail=f"Invalid date format: {home_visit_date}. Use 'YYYY-MM-DD HH:MM' or ISO8601 string")
    
    application.home_visit_date = visit_date
    application.status = ApplicationStatus.HOME_VISIT_SCHEDULED
    application.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(application)
    
    print(f"   ✅ 家訪已安排: {visit_date}")
    
    notification = Notification(
        user_id=application.applicant_id,
        title="家訪已安排",
        message=f"申請編號：#{application.id}\n家訪時間：{visit_date.strftime('%Y年%m月%d日 %H:%M')}",
        created_at=datetime.now(dt_timezone.utc)
    )
    db.add(notification)
    await db.commit()
    
    return {
        "message": "Scheduled",
        "application_id": application.id,
        "home_visit_date": application.home_visit_date.isoformat() if application.home_visit_date else None,
        "status": application.status.value
    }


@router.post("/applications/{application_id}/complete-home-visit")
async def complete_home_visit(
    application_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """完成家訪並上傳紀錄"""
    from datetime import datetime
    from sqlalchemy import select
    from app.models.pet import Pet, PetStatus
    from app.models.adoption import AdoptionApplication, ApplicationStatus
    from app.models.notification import Notification
    from datetime import timezone as dt_timezone
    from app.services.s3 import s3_service
    
    # Parse multipart form data
    form = await request.form()
    notes = form.get('notes')
    document = form.get('document')
    
    print(f"🏠 完成家訪:")
    print(f"   Application ID: {application_id}")
    print(f"   Notes: {notes}")
    print(f"   Has Document: {document is not None}")
    
    if not notes:
        raise HTTPException(status_code=422, detail="Missing notes")
    
    if current_user.role != UserRole.shelter:
        print(f"   ❌ 權限錯誤: 只有 shelter 可以完成家訪")
        raise HTTPException(status_code=403, detail="Only shelter can complete home visit")
    
    app_query = select(AdoptionApplication).where(AdoptionApplication.id == application_id)
    result = await db.execute(app_query)
    application = result.scalar_one_or_none()
    
    if not application:
        print(f"   ❌ 申請不存在: {application_id}")
        raise HTTPException(status_code=404, detail="Not found")
    
    pet_query = select(Pet).where(Pet.id == application.pet_id)
    pet_result = await db.execute(pet_query)
    pet = pet_result.scalar_one_or_none()
    
    if not pet or pet.shelter_id != current_user.id:
        print(f"   ❌ 權限錯誤: 寵物不屬於此 shelter")
        raise HTTPException(status_code=403, detail="No permission")
    
    if pet.status != PetStatus.AVAILABLE:
        print(f"   ❌ 寵物狀態錯誤: {pet.status}")
        raise HTTPException(status_code=400, detail=f"Pet not available: {pet.status}")
    
    allowed_statuses = [
        ApplicationStatus.HOME_VISIT_SCHEDULED,
        ApplicationStatus.HOME_VISIT_COMPLETED,
        ApplicationStatus.UNDER_EVALUATION
    ]
    if application.status not in allowed_statuses:
        print(f"   ❌ 狀態錯誤: {application.status}")
        raise HTTPException(status_code=400, detail=f"Invalid status: {application.status}")
    
    # Upload document if provided
    document_key = None
    if document and hasattr(document, 'filename'):
        try:
            file_content = await document.read()
            print(f"   📄 上傳文件: {document.filename} ({len(file_content)} bytes)")
            
            upload_result = s3_service.upload_file(
                file_content=file_content,
                filename=document.filename,
                category="home_visit_document",
                content_type=getattr(document, 'content_type', 'application/octet-stream')
            )
            document_key = upload_result.get("file_key")
            print(f"   ✅ 文件已上傳: {document_key}")
        except Exception as e:
            print(f"   ❌ 文件上傳失敗: {e}")
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
    # Update application
    application.home_visit_notes = notes
    if document_key:
        application.home_visit_document = document_key
    
    # Only change status if currently HOME_VISIT_SCHEDULED
    if application.status == ApplicationStatus.HOME_VISIT_SCHEDULED:
        application.status = ApplicationStatus.HOME_VISIT_COMPLETED
    
    application.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(application)
    
    print(f"   ✅ 家訪已完成")
    
    notification = Notification(
        user_id=application.applicant_id,
        title="家訪已完成",
        message=f"申請編號：#{application.id}\n您的領養申請家訪已完成，我們正在進行評估。",
        created_at=datetime.now(dt_timezone.utc)
    )
    db.add(notification)
    await db.commit()
    
    return {
        "message": "Home visit completed",
        "application_id": application.id,
        "home_visit_notes": application.home_visit_notes,
        "home_visit_document": application.home_visit_document,
        "status": application.status.value
    }


@router.put("/applications/{application_id}/home-visit-record")
async def update_home_visit_record(
    application_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """修改家訪紀錄"""
    from datetime import datetime
    from sqlalchemy import select
    from app.models.pet import Pet, PetStatus
    from app.models.adoption import AdoptionApplication, ApplicationStatus
    from app.models.notification import Notification
    from datetime import timezone as dt_timezone
    from app.services.s3 import s3_service
    
    # Parse multipart form data
    form = await request.form()
    notes = form.get('notes')
    document = form.get('document')
    
    print(f"📝 修改家訪紀錄:")
    print(f"   Application ID: {application_id}")
    print(f"   Notes: {notes}")
    print(f"   Has New Document: {document is not None}")
    
    if not notes:
        raise HTTPException(status_code=422, detail="Missing notes")
    
    if current_user.role != UserRole.shelter:
        print(f"   ❌ 權限錯誤: 只有 shelter 可以修改家訪紀錄")
        raise HTTPException(status_code=403, detail="Only shelter can update home visit record")
    
    app_query = select(AdoptionApplication).where(AdoptionApplication.id == application_id)
    result = await db.execute(app_query)
    application = result.scalar_one_or_none()
    
    if not application:
        print(f"   ❌ 申請不存在: {application_id}")
        raise HTTPException(status_code=404, detail="Not found")
    
    pet_query = select(Pet).where(Pet.id == application.pet_id)
    pet_result = await db.execute(pet_query)
    pet = pet_result.scalar_one_or_none()
    
    if not pet or pet.shelter_id != current_user.id:
        print(f"   ❌ 權限錯誤: 寵物不屬於此 shelter")
        raise HTTPException(status_code=403, detail="No permission")
    
    # Check status - must have completed home visit already
    allowed_statuses = [
        ApplicationStatus.HOME_VISIT_COMPLETED,
        ApplicationStatus.UNDER_EVALUATION
    ]
    if application.status not in allowed_statuses:
        print(f"   ❌ 狀態錯誤: {application.status}")
        raise HTTPException(status_code=400, detail=f"Can only update record after home visit is completed")
    
    # Upload document if provided
    document_key = None
    if document and hasattr(document, 'filename'):
        try:
            file_content = await document.read()
            print(f"   📄 上傳新文件: {document.filename} ({len(file_content)} bytes)")
            
            upload_result = s3_service.upload_file(
                file_content=file_content,
                filename=document.filename,
                category="home_visit_document",
                content_type=getattr(document, 'content_type', 'application/octet-stream')
            )
            document_key = upload_result.get("file_key")
            print(f"   ✅ 新文件已上傳: {document_key}")
        except Exception as e:
            print(f"   ❌ 文件上傳失敗: {e}")
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
    # Update application
    application.home_visit_notes = notes
    if document_key:  # Only update document if a new one was uploaded
        application.home_visit_document = document_key
    
    application.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(application)
    
    print(f"   ✅ 家訪紀錄已更新")
    
    return {
        "message": "Home visit record updated",
        "application_id": application.id,
        "home_visit_notes": application.home_visit_notes,
        "home_visit_document": application.home_visit_document,
        "status": application.status.value
    }


@router.put("/applications/{application_id}/home-visit-date")
async def update_home_visit_date(
    application_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """編輯家訪日期"""
    from datetime import datetime
    from sqlalchemy import select
    from app.models.pet import Pet
    from app.models.adoption import AdoptionApplication
    from app.models.notification import Notification
    from datetime import timezone as dt_timezone
    
    # 讀取請求 body
    try:
        body = await request.json()
        home_visit_date = None
        if isinstance(body, dict):
            home_visit_date = body.get('home_visit_date') or body.get('homeVisitDate') or body.get('date')
        elif isinstance(body, str):
            home_visit_date = body
        
        if not home_visit_date:
            raise HTTPException(status_code=422, detail="Missing home_visit_date")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid request: {str(e)}")
    
    print(f"📝 修改家訪時間:")
    print(f"   Application ID: {application_id}")
    print(f"   New Date: {home_visit_date}")
    
    if current_user.role != UserRole.shelter:
        raise HTTPException(status_code=403, detail="Only shelter")
    
    app_query = select(AdoptionApplication).where(AdoptionApplication.id == application_id)
    result = await db.execute(app_query)
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(status_code=404, detail="Not found")
    
    pet_query = select(Pet).where(Pet.id == application.pet_id)
    pet_result = await db.execute(pet_query)
    pet = pet_result.scalar_one_or_none()
    
    if not pet or pet.shelter_id != current_user.id:
        raise HTTPException(status_code=403, detail="No permission")
    
    # Parse date (support both ISO and YYYY-MM-DD HH:MM formats)
    visit_date = None
    try:
        iso_input = home_visit_date.replace("Z", "+00:00") if isinstance(home_visit_date, str) else home_visit_date
        visit_date = datetime.fromisoformat(iso_input)
        print(f"   ✅ 日期解析成功 (ISO): {visit_date}")
    except Exception as e1:
        try:
            visit_date = datetime.strptime(home_visit_date, "%Y-%m-%d %H:%M")
            print(f"   ✅ 日期解析成功 (YYYY-MM-DD HH:MM): {visit_date}")
        except Exception as e2:
            raise HTTPException(status_code=400, detail="Invalid date format")
    
    application.home_visit_date = visit_date
    application.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(application)
    
    print(f"   ✅ 家訪時間已更新: {visit_date}")
    
    notification = Notification(
        user_id=application.applicant_id,
        title="家訪時間已更改",
        message=f"新時間：{visit_date.strftime('%Y年%m月%d日 %H:%M')}",
        created_at=datetime.now(dt_timezone.utc)
    )
    db.add(notification)
    await db.commit()
    
    return {
        "message": "Updated",
        "application_id": application.id,
        "home_visit_date": application.home_visit_date.isoformat() if application.home_visit_date else None
    }


@router.post("/applications/{application_id}/complete-home-visit")
async def complete_home_visit(
    application_id: int,
    notes: str,
    document_key: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """完成家訪"""
    from datetime import datetime
    from sqlalchemy import select
    from app.models.pet import Pet
    from app.models.adoption import AdoptionApplication, ApplicationStatus
    from app.models.notification import Notification
    from datetime import timezone as dt_timezone
    
    if current_user.role != UserRole.shelter:
        raise HTTPException(status_code=403, detail="Only shelter")
    
    app_query = select(AdoptionApplication).where(AdoptionApplication.id == application_id)
    result = await db.execute(app_query)
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(status_code=404, detail="Not found")
    
    pet_query = select(Pet).where(Pet.id == application.pet_id)
    pet_result = await db.execute(pet_query)
    pet = pet_result.scalar_one_or_none()
    
    if not pet or pet.shelter_id != current_user.id:
        raise HTTPException(status_code=403, detail="No permission")
    
    allowed = [ApplicationStatus.HOME_VISIT_SCHEDULED, ApplicationStatus.HOME_VISIT_COMPLETED, ApplicationStatus.UNDER_EVALUATION]
    if application.status not in allowed:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    application.home_visit_notes = notes
    if document_key:
        application.home_visit_document = document_key
    
    if application.status == ApplicationStatus.HOME_VISIT_SCHEDULED:
        application.status = ApplicationStatus.HOME_VISIT_COMPLETED
    
    application.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(application)
    
    notification = Notification(
        user_id=application.applicant_id,
        title="家訪已完成",
        message="家訪已完成，正在評估中",
        created_at=datetime.now(dt_timezone.utc)
    )
    db.add(notification)
    await db.commit()
    
    return {
        "message": "Completed",
        "application_id": application.id,
        "home_visit_notes": application.home_visit_notes,
        "home_visit_document": application.home_visit_document,
        "status": application.status.value
    }


@router.post("/applications/{application_id}/final-decision")
async def make_final_decision(
    application_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """最終決定"""
    from datetime import datetime
    from sqlalchemy import select
    from app.models.pet import Pet, PetStatus
    from app.models.adoption import AdoptionApplication, ApplicationStatus
    from app.models.notification import Notification
    from datetime import timezone as dt_timezone
    
    # Parse multipart form data
    form = await request.form()
    decision = form.get('decision')
    notes = form.get('notes')
    
    print(f"⚖️ 最終決定:")
    print(f"   Application ID: {application_id}")
    print(f"   Decision: {decision}")
    print(f"   Notes: {notes}")
    
    if not decision or not notes:
        raise HTTPException(status_code=422, detail="Missing decision or notes")
    
    if current_user.role != UserRole.shelter:
        raise HTTPException(status_code=403, detail="Only shelter")
    
    if decision not in ["approved", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid decision")
    
    app_query = select(AdoptionApplication).where(AdoptionApplication.id == application_id)
    result = await db.execute(app_query)
    application = result.scalar_one_or_none()
    
    if not application:
        raise HTTPException(status_code=404, detail="Not found")
    
    pet_query = select(Pet).where(Pet.id == application.pet_id)
    pet_result = await db.execute(pet_query)
    pet = pet_result.scalar_one_or_none()
    
    if not pet or pet.shelter_id != current_user.id:
        raise HTTPException(status_code=403, detail="No permission")
    
    if decision == "approved" and pet.status != PetStatus.AVAILABLE:
        raise HTTPException(status_code=400, detail="Pet not available")
    
    if application.status not in [ApplicationStatus.HOME_VISIT_COMPLETED, ApplicationStatus.UNDER_EVALUATION]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    application.final_decision_notes = notes
    application.status = ApplicationStatus.APPROVED if decision == "approved" else ApplicationStatus.REJECTED
    application.reviewed_by = current_user.id
    application.reviewed_at = datetime.utcnow()
    application.updated_at = datetime.utcnow()
    
    if decision == "approved":
        pet.status = PetStatus.ADOPTED
    
    await db.commit()
    await db.refresh(application)
    
    print(f"   ✅ 最終決定: {decision}")
    
    if decision == "approved":
        notification = Notification(
            user_id=application.applicant_id,
            title="領養申請已通過",
            message=f"申請編號：#{application.id}\n恭喜！申請已通過，請聯繫收容所安排領養手續。",
            created_at=datetime.now(dt_timezone.utc)
        )
    else:
        notification = Notification(
            user_id=application.applicant_id,
            title="領養申請未通過",
            message=f"申請編號：#{application.id}\n很抱歉，申請未能通過。{notes or '歡迎申請其他寵物。'}",
            created_at=datetime.now(dt_timezone.utc)
        )
    
    db.add(notification)
    await db.commit()
    
    return {
        "message": f"Application {decision}",
        "application_id": application.id,
        "decision": application.status.value,
        "final_decision_notes": application.final_decision_notes,
        "pet_status": pet.status.value if decision == "approved" else None
    }
