"""
Models package initialization
Import all models to ensure they are registered with SQLAlchemy
"""

from app.models.user import User, UserRole
from app.models.password_history import PasswordHistory
from app.models.pet import Pet, PetPhoto, PetSpecies, PetGender, PetSize, PetStatus
from app.models.adoption import AdoptionApplication, ApplicationDocument, ApplicationStatus
# New chat models
from app.models.chat_room import ChatRoom
from app.models.chat_message import ChatMessage, MessageType
# Old message models (if still needed elsewhere)
# from app.models.message import RoomMember, Message, ChatRoomType, MemberRole
from app.models.notification import Notification, UserFavorite, NotificationType

# File model removed - not used, files are stored in specific tables (pet_photos, post_photos, application_documents)
# DocumentRequest, ApplicationReviewer, ApplicationStatus models removed - not used in V2
# Community models
from app.models.community import CommunityPost, PostPhoto, PostComment, PostLike, PostTypeEnum
from app.models.post_report import PostReport

__all__ = [
    # User models
    "User",
    "UserRole",
    "PasswordHistory",
    
    # Pet models
    "Pet",
    "PetPhoto",
    "PetSpecies",
    "PetGender", 
    "PetSize",
    "PetStatus",
    
    # Adoption models
    "AdoptionApplication",
    "ApplicationDocument",
    "ApplicationStatus",
    
    # Message models
    "ChatRoom",
    "ChatMessage",
    "MessageType",
    
    # Notification models
    "Notification",
    "UserFavorite",
    "NotificationType",
    

    
    # Community models
    "CommunityPost",
    "PostPhoto",
    "PostLike",
    "PostComment",
    "PostTypeEnum",
    "PostReport",
    
    # Analytics models

]