"""
User model for authentication and user management
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from datetime import datetime

from app.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration"""
    USER = "user"
    SHELTER_ADMIN = "shelter_admin"
    SYSTEM_ADMIN = "system_admin"


class User(Base):
    """User model for authentication and profile management"""
    
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Authentication fields
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # Profile information
    full_name = Column(String(200))
    phone = Column(String(20))
    address = Column(Text)
    
    # User status and role
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login_at = Column(DateTime(timezone=True))
    
    # Relationships
    pets = relationship("Pet", back_populates="shelter", foreign_keys="Pet.shelter_id")
    created_pets = relationship("Pet", back_populates="creator", foreign_keys="Pet.created_by")
    adoption_applications = relationship("AdoptionApplication", back_populates="applicant")
    sent_messages = relationship("Message", back_populates="sender")
    room_memberships = relationship("RoomMember", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    favorites = relationship("UserFavorite", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    @property
    def is_shelter_admin(self) -> bool:
        """Check if user is a shelter admin"""
        return self.role == UserRole.SHELTER_ADMIN
    
    @property
    def is_system_admin(self) -> bool:
        """Check if user is a system admin"""
        return self.role == UserRole.SYSTEM_ADMIN
    
    @property
    def display_name(self) -> str:
        """Get display name (full name or username)"""
        return self.full_name or self.username