"""
Service Factory Classes
Service 工廠類別 - 負責建立和組裝 Service 實例
"""
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import (
    AdoptionRepository,
    PetRepository,
    NotificationRepository,
    UserRepository,
    ChatRepository,
    MessageRepository,
    CommunityRepository,
    CommentRepository,
    PostLikeRepository,
    PhotoRepository,
)

# Import new service classes
from app.services.adoption_service_new import AdoptionService
from app.services.pet_service_new import PetService
from app.services.notification_service_new import NotificationService
from app.services.chat_service_new import ChatService
from app.services.community_service_new import CommunityService


class AdoptionServiceFactory:
    """領養申請 Service 工廠"""
    
    @staticmethod
    def create(db: AsyncSession) -> AdoptionService:
        adoption_repo = AdoptionRepository(db)
        pet_repo = PetRepository(db)
        user_repo = UserRepository(db)
        
        return AdoptionService(
            adoption_repo=adoption_repo,
            pet_repo=pet_repo,
            user_repo=user_repo
        )


class PetServiceFactory:
    """寵物管理 Service 工廠"""
    
    @staticmethod
    def create(db: AsyncSession) -> PetService:
        pet_repo = PetRepository(db)
        
        return PetService(pet_repo=pet_repo)


class NotificationServiceFactory:
    """通知 Service 工廠"""
    
    @staticmethod
    def create(db: AsyncSession) -> NotificationService:
        notification_repo = NotificationRepository(db)
        
        return NotificationService(notification_repo=notification_repo)


class ChatServiceFactory:
    """聊天 Service 工廠"""
    
    @staticmethod
    def create(db: AsyncSession) -> ChatService:
        chat_repo = ChatRepository(db)
        message_repo = MessageRepository(db)
        user_repo = UserRepository(db)
        pet_repo = PetRepository(db)
        
        return ChatService(
            chat_repo=chat_repo,
            message_repo=message_repo,
            user_repo=user_repo,
            pet_repo=pet_repo
        )


class CommunityServiceFactory:
    """社群 Service 工廠"""
    
    @staticmethod
    def create(db: AsyncSession) -> CommunityService:
        post_repo = CommunityRepository(db)
        comment_repo = CommentRepository(db)
        post_like_repo = PostLikeRepository(db)
        photo_repo = PhotoRepository(db)
        
        return CommunityService(
            post_repo=post_repo,
            comment_repo=comment_repo,
            post_like_repo=post_like_repo,
            photo_repo=photo_repo
        )
