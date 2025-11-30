"""
Files API V2 - 簡化版本
"""
from typing import List
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
import uuid

from app.auth.dependencies import get_current_user
from app.models.user import User
from app.services.s3 import S3Service

router = APIRouter()

# 初始化 S3 服務
s3_service = S3Service()

# 允許的文件分類
CATEGORIES = ["pet_photo", "document", "profile"]

# 允許的文件擴展名
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".pdf", ".doc", ".docx"}


def get_file_extension(filename: str) -> str:
    """獲取文件擴展名"""
    return filename[filename.rfind('.'):].lower() if '.' in filename else ''


@router.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    category: str = Form("pet_photo"),
    current_user: User = Depends(get_current_user),
):
    """
    上傳一個或多個文件
    
    Args:
        files: 要上傳的文件列表
        category: 文件分類 (pet_photo, document, profile)
        current_user: 當前認證用戶
    
    Returns:
        上傳文件的元數據列表
    """
    print(f"📤 V2 上傳請求 - 文件數: {len(files)}, 分類: {category}, 用戶: {current_user.id}")
    
    # 驗證分類
    if category not in CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {', '.join(CATEGORIES)}"
        )
    
    # 驗證文件類型
    for file in files:
        ext = get_file_extension(file.filename)
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type {ext} not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
    
    # 上傳文件
    uploaded_files = []
    for file in files:
        try:
            print(f"  📁 處理文件: {file.filename}")
            
            # 讀取文件內容
            content = await file.read()
            print(f"  📊 文件大小: {len(content)} bytes")
            
            # 使用 S3 服務上傳
            upload_result = s3_service.upload_file(
                file_content=content,
                filename=file.filename,
                category=category,
                content_type=file.content_type or "application/octet-stream"
            )
            
            print(f"  ✅ 上傳成功!")
            print(f"  🔗 URL: {upload_result['file_url']}")
            print(f"  🔑 Key: {upload_result['file_key']}")
            
            # 構建返回數據
            file_metadata = {
                "id": str(uuid.uuid4()),
                "filename": file.filename,
                "file_url": upload_result["file_url"],
                "file_key": upload_result["file_key"],
                "file_size": len(content),
                "content_type": file.content_type,
                "category": category,
                "urls": {
                    "original": upload_result["file_url"],
                    "large": upload_result["file_url"],
                    "thumbnail": upload_result["file_url"],
                }
            }
            
            uploaded_files.append(file_metadata)
            
        except Exception as e:
            print(f"  ❌ 上傳失敗: {str(e)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload {file.filename}: {str(e)}"
            )
    
    return {
        "success": True,
        "message": f"Successfully uploaded {len(uploaded_files)} file(s)",
        "files": uploaded_files,
    }
