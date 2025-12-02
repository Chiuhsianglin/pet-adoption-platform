"""
Authentication module initialization
"""
from .jwt_handler import JWTHandler, jwt_handler
from .password_handler import PasswordHandler, password_handler
from .auth_service import AuthService
from .auth_factory import AuthServiceFactory
from .dependencies import (
    get_current_user, 
    get_current_active_user, 
    get_current_verified_user,
    require_roles,
    require_admin,
    require_shelter,
    require_adopter,
    require_shelter_or_adopter,
    get_optional_user
)

__all__ = [
    "JWTHandler",
    "jwt_handler",
    "PasswordHandler", 
    "password_handler",
    "AuthService",
    "AuthServiceFactory",
    "get_current_user",
    "get_current_active_user",
    "get_current_verified_user",
    "require_roles",
    "require_admin",
    "require_shelter", 
    "require_adopter",
    "require_shelter_or_adopter",
    "get_optional_user"
]
