"""
Authentication Dependencies for FastAPI
Dependency injection functions for authentication and authorization
"""
from typing import List, Optional, Callable
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.database import get_db
from app.repositories.user import UserRepository
from .jwt_handler import jwt_handler


# Security scheme for Bearer token
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    request: Request = None,
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    """
    token = credentials.credentials
    
    try:
        # Decode and validate token
        payload = jwt_handler.decode_token(token)
        user_id: int = int(payload.get("sub"))
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # Get user from database
        user_repo = UserRepository(db)
        user = await user_repo.get_by_id(user_id)
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current user and ensure they are active
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    return current_user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Get current user from token if provided, otherwise return None
    Useful for endpoints that work for both authenticated and anonymous users
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    
    try:
        payload = jwt_handler.decode_token(token)
        user_id: int = int(payload.get("sub"))
        
        if user_id is None:
            return None
        
        user_repo = UserRepository(db)
        user = await user_repo.get_by_id(user_id)
        
        return user
    except Exception:
        # If token is invalid, just return None instead of raising error
        return None


async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Get current user and ensure they are verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email verification required"
        )
    return current_user


def require_roles(allowed_roles: List[UserRole]) -> Callable:
    """
    Dependency factory for role-based access control
    
    Usage:
        @app.get("/admin/users")
        async def get_users(user: User = Depends(require_roles([UserRole.admin]))):
            ...
    """
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[role.value for role in allowed_roles]}"
            )
        return current_user
    
    return role_checker


def require_admin() -> Callable:
    """
    Dependency for admin-only access
    """
    return require_roles([UserRole.admin])


def require_shelter() -> Callable:
    """
    Dependency for shelter users
    """
    return require_roles([UserRole.shelter, UserRole.admin])


def require_adopter() -> Callable:
    """
    Dependency for adopter users
    """
    return require_roles([UserRole.adopter, UserRole.admin])


def require_shelter_or_adopter() -> Callable:
    """
    Dependency for shelter or adopter users
    """
    return require_roles([UserRole.shelter, UserRole.adopter, UserRole.admin])


class ResourcePermission:
    """
    Resource-level permission checker
    """
    
    @staticmethod
    async def can_access_user_profile(
        target_user_id: int,
        current_user: User = Depends(get_current_active_user)
    ) -> bool:
        """
        Check if user can access another user's profile
        """
        # Users can access their own profile, admins can access any profile
        if current_user.role == UserRole.admin or current_user.id == target_user_id:
            return True
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to user profile"
        )
    
    @staticmethod
    async def can_manage_pet(
        pet_shelter_id: int,
        current_user: User = Depends(get_current_active_user)
    ) -> bool:
        """
        Check if user can manage a specific pet
        """
        # Admins can manage any pet, shelters can manage their own pets
        if (current_user.role == UserRole.admin or 
            (current_user.role == UserRole.shelter and current_user.id == pet_shelter_id)):
            return True
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to pet management"
        )
    
    @staticmethod
    async def can_access_application(
        application_applicant_id: int,
        application_shelter_id: int,
        current_user: User = Depends(get_current_active_user)
    ) -> bool:
        """
        Check if user can access an adoption application
        """
        # Admins can access any application
        # Applicants can access their own applications
        # Shelters can access applications for their pets
        if (current_user.role == UserRole.admin or
            current_user.id == application_applicant_id or
            (current_user.role == UserRole.shelter and current_user.id == application_shelter_id)):
            return True
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to adoption application"
        )


# Optional middleware for IP-based restrictions
class IPRestrictionMiddleware:
    """
    Middleware for IP-based access restrictions
    """
    
    def __init__(self, allowed_ips: Optional[List[str]] = None):
        self.allowed_ips = allowed_ips or []
    
    async def __call__(self, request: Request):
        if self.allowed_ips:
            client_ip = request.client.host
            if client_ip not in self.allowed_ips:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="IP address not allowed"
                )


# Rate limiting dependency (basic implementation)
class RateLimiter:
    """
    Basic rate limiting for sensitive endpoints
    """
    
    def __init__(self, max_requests: int = 60, window_minutes: int = 1):
        self.max_requests = max_requests
        self.window_minutes = window_minutes
    
    async def __call__(self, request: Request):
        # This is a simplified rate limiter
        # In production, you'd use Redis or a proper rate limiting library
        client_ip = request.client.host
        
        # TODO: Implement proper rate limiting with Redis
        # For now, this is just a placeholder
        
        return True


# Common dependency combinations
async def get_admin_user(
    current_user: User = Depends(require_admin())
) -> User:
    """Get current user ensuring admin role"""
    return current_user


async def get_shelter_user(
    current_user: User = Depends(require_shelter())
) -> User:
    """Get current user ensuring shelter role"""
    return current_user


async def get_adopter_user(
    current_user: User = Depends(require_adopter())
) -> User:
    """Get current user ensuring adopter role"""
    return current_user


# Optional token dependency (for endpoints that work with or without auth)
async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[User]:
    """
    Get current user if token is provided, otherwise return None
    Useful for endpoints that enhance functionality when authenticated
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None

