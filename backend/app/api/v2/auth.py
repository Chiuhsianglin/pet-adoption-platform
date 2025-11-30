"""
Authentication API V2 - Three-Layer Architecture
使用三層架構的認證 API
"""
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User, UserRole
from app.auth.auth_factory import AuthServiceFactory
from app.auth.dependencies import security, get_current_user, get_current_active_user
from app.exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    UserNotFoundError,
    AccountDeactivatedError,
)

router = APIRouter()


# ========== Request/Response Models ==========

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    role: Optional[UserRole] = UserRole.adopter


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: Optional[bool] = False


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=255)


class EmailVerificationRequest(BaseModel):
    user_id: int
    token: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    is_active: bool
    is_verified: bool
    phone: Optional[str] = None
    address: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class AuthResponse(BaseModel):
    user: UserResponse
    tokens: TokenResponse
    message: str


class MessageResponse(BaseModel):
    message: str


# ========== Helper Functions ==========

def _handle_error(error: Exception):
    """統一錯誤處理"""
    if isinstance(error, UserAlreadyExistsError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )
    elif isinstance(error, InvalidCredentialsError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error)
        )
    elif isinstance(error, UserNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )
    elif isinstance(error, AccountDeactivatedError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error)
        )
    elif isinstance(error, ValueError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(error)}"
        )


# ========== API Endpoints ==========

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
) -> AuthResponse:
    """
    註冊新用戶
    
    - **email**: 用戶 email（必須唯一）
    - **password**: 密碼（最少 8 個字元）
    - **name**: 用戶姓名
    - **phone**: 電話號碼（可選）
    - **role**: 用戶角色（預設為 adopter）
    
    返回用戶資訊和 JWT tokens
    """
    try:
        service = AuthServiceFactory.create(db)
        result = await service.register_user(
            email=request.email,
            password=request.password,
            name=request.name,
            phone=request.phone,
            role=request.role or UserRole.adopter
        )
        return AuthResponse(**result)
    
    except Exception as e:
        _handle_error(e)


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_db)
) -> AuthResponse:
    """
    用戶登入
    
    - **email**: 用戶 email
    - **password**: 密碼
    - **remember_me**: 是否記住登入（延長 session）
    
    返回 access token (15 分鐘) 和 refresh token (7 天)
    """
    try:
        service = AuthServiceFactory.create(db)
        client_ip = http_request.client.host
        
        result = await service.login_user(
            email=request.email,
            password=request.password,
            remember_me=request.remember_me,
            ip_address=client_ip
        )
        return AuthResponse(**result)
    
    except Exception as e:
        _handle_error(e)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    refresh_token: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """
    用戶登出
    
    將 access token 和 refresh token 加入黑名單
    
    - **Authorization**: Bearer access token（header）
    - **refresh_token**: 可選的 refresh token
    """
    try:
        service = AuthServiceFactory.create(db)
        access_token = credentials.credentials
        
        result = await service.logout_user(access_token, refresh_token)
        return MessageResponse(**result)
    
    except Exception as e:
        _handle_error(e)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    刷新 access token
    
    使用 refresh token 獲取新的 access token
    
    - **refresh_token**: 有效的 refresh token
    """
    try:
        service = AuthServiceFactory.create(db)
        result = await service.refresh_token(request.refresh_token)
        return TokenResponse(**result)
    
    except Exception as e:
        _handle_error(e)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> UserResponse:
    """
    獲取當前認證用戶資訊
    
    需要在 Authorization header 中提供有效的 access token
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role.value,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        phone=current_user.phone,
        address=current_user.address_line1,
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user_info(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    更新當前認證用戶資訊
    
    需要在 Authorization header 中提供有效的 access token
    
    - **name**: 用戶姓名
    - **phone**: 電話號碼
    - **address**: 地址
    """
    try:
        # 從當前 session 重新取得用戶
        from sqlalchemy import select
        result = await db.execute(
            select(User).where(User.id == current_user.id)
        )
        user = result.scalar_one()
        
        # 更新用戶資訊
        if request.name is not None:
            user.name = request.name
        if request.phone is not None:
            user.phone = request.phone
        if request.address is not None:
            user.address_line1 = request.address
        
        # 提交更新
        await db.commit()
        await db.refresh(user)
        
        return UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            role=user.role.value,
            is_active=user.is_active,
            is_verified=user.is_verified,
            phone=user.phone,
            address=user.address_line1,
        )
    
    except Exception as e:
        _handle_error(e)


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """
    修改密碼
    
    需要提供當前密碼和新密碼
    
    - **current_password**: 當前密碼
    - **new_password**: 新密碼（最少 8 個字元）
    """
    try:
        service = AuthServiceFactory.create(db)
        result = await service.change_password(
            user_id=current_user.id,
            current_password=request.current_password,
            new_password=request.new_password
        )
        return MessageResponse(**result)
    
    except Exception as e:
        _handle_error(e)


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    request: EmailVerificationRequest,
    db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """
    驗證用戶 email
    
    - **user_id**: 用戶 ID
    - **token**: 驗證 token
    """
    try:
        service = AuthServiceFactory.create(db)
        result = await service.verify_email(
            user_id=request.user_id,
            token=request.token
        )
        return MessageResponse(**result)
    
    except Exception as e:
        _handle_error(e)


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    健康檢查端點
    """
    return {
        "status": "healthy",
        "service": "auth-v2",
        "architecture": "three-layer"
    }


@router.get("/users/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    獲取當前登入用戶的資訊
    
    返回格式兼容 v1 API
    """
    return {
        "success": True,
        "data": {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
            "phone": current_user.phone,
            "role": current_user.role.value if hasattr(current_user.role, 'value') else current_user.role,
            "is_active": current_user.is_active,
            "is_email_verified": current_user.is_email_verified,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
            "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None,
        }
    }
