"""
User model for authentication and user management
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from app.database import Base
from app.models.adoption import AdoptionApplication


class UserRole(str, enum.Enum):
    """User role enumeration.
    NOTE: Removed invalid USER value reference; using existing roles only.
    If a generic default user role is needed, we treat 'adopter' as the
    baseline general user role.
    """
    admin = "admin"
    adopter = "adopter"
    shelter = "shelter"


class User(Base):
    """User model for authentication and profile management"""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Authentication fields
    email = Column(String(255), unique=True, index=True, nullable=False)
    #username = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Profile information
    name = Column(String(200))
    phone = Column(String(20))
    address_line1 = Column(String(255))
    
    # User status and role
    # Default role corrected: previous code referenced UserRole.USER which
    # did not exist and caused AttributeError on import. We default to the
    # general role 'adopter'.
    role = Column(Enum(UserRole), default=UserRole.adopter, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    #last_login_at = Column(DateTime(timezone=True))
    
    # Relationships
    pets = relationship("Pet", back_populates="shelter", foreign_keys="Pet.shelter_id")
    created_pets = relationship("Pet", back_populates="creator", foreign_keys="Pet.created_by")
    adoption_applications = relationship(
        "AdoptionApplication",
        back_populates="applicant",
        foreign_keys=[AdoptionApplication.applicant_id]
    )
    # Note: Old Message and RoomMember relationships removed - using new chat system
    # sent_messages = relationship("Message", back_populates="sender")
    # room_memberships = relationship("RoomMember", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    favorites = relationship("UserFavorite", back_populates="user")
    password_history = relationship("PasswordHistory", back_populates="user", order_by="PasswordHistory.created_at.desc()")
    community_posts = relationship("CommunityPost", back_populates="user")
    post_comments = relationship("PostComment", back_populates="user")
    post_likes = relationship("PostLike", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"
    
    @property
    def is_shelter_admin(self) -> bool:
        """Check if user is a shelter admin"""
        return self.role == UserRole.shelter
    
    @property
    def is_system_admin(self) -> bool:
        """Check if user is a system admin"""
        return self.role == UserRole.admin
    
    @property
    def display_name(self) -> str:
        """Get display name (full name or username)"""
        return self.name