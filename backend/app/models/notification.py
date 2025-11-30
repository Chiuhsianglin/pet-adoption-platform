"""
Notification and user favorite models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class NotificationType(str, enum.Enum):
    """Notification type enumeration"""
    APPLICATION_STATUS = "application_status"
    MESSAGE = "message"
    SYSTEM = "system"
    REMINDER = "reminder"
    REVIEW_STATUS = "review_status"  # Pet review status notifications
    POST_REPORT = "post_report"  # Post report notifications for admins
    POST_LIKE = "post_like"  # Someone liked your post
    POST_COMMENT = "post_comment"  # Someone commented on your post


class Notification(Base):
    """Notification model for user notifications"""
    
    __tablename__ = "notifications"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Notification content
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=True, index=True)
    link = Column(String(500), nullable=True)  # Link to related resource (e.g., post URL)
    
    # Notification status
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification(id={self.id}, is_read={self.is_read})>"


class UserFavorite(Base):
    """User favorite pets model"""
    
    __tablename__ = "user_favorites"
    
    # Composite primary key
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), primary_key=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="favorites")
    pet = relationship("Pet", back_populates="favorites")
    
    def __repr__(self):
        return f"<UserFavorite(user_id={self.user_id}, pet_id={self.pet_id})>"