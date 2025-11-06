"""
Models package initialization
Import all models to ensure they are registered with SQLAlchemy
"""

from app.models.user import User, UserRole
from app.models.password_history import PasswordHistory
from app.models.pet import Pet, PetPhoto, PetSpecies, PetGender, PetSize, PetStatus
from app.models.adoption import AdoptionApplication, ApplicationDocument, ApplicationStatus
from app.models.message import ChatRoom, RoomMember, Message, ChatRoomType, MessageType, MemberRole
from app.models.notification import Notification, UserFavorite, NotificationType

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
    "RoomMember",
    "Message",
    "ChatRoomType",
    "MessageType",
    "MemberRole",
    
    # Notification models
    "Notification",
    "UserFavorite",
    "NotificationType",
]