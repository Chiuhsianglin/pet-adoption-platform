"""
API v2 - 三層架構 (Controller -> Service -> Repository)
"""

from fastapi import APIRouter

# 主路由器
api_router = APIRouter()

# 導入模組路由
from app.api.v2 import (
    auth,
    pets,
    adoptions,
    notifications,
    chat,
    community,
    files
)

# 註冊各模組路由
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth-v2"]
)

api_router.include_router(
    pets.router,
    prefix="/pets",
    tags=["pets-v2"]
)

api_router.include_router(
    adoptions.router,
    prefix="/adoptions",
    tags=["adoptions-v2"]
)

api_router.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["notifications-v2"]
)

api_router.include_router(
    chat.router,
    prefix="/chat",
    tags=["chat-v2"]
)

api_router.include_router(
    community.router,
    prefix="/community",
    tags=["community-v2"]
)

api_router.include_router(
    files.router,
    prefix="/files",
    tags=["files-v2"]
)
