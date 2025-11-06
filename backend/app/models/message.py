"""
Message and chat room models for real-time communication
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from typing import List

from app.database import Base


class ChatRoomType(str, enum.Enum):
    """Chat room type enumeration"""
    ADOPTION = "adoption"
    SUPPORT = "support"
    GENERAL = "general"


class MessageType(str, enum.Enum):
    """Message type enumeration"""
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    SYSTEM = "system"


class MemberRole(str, enum.Enum):
    """Chat room member role enumeration"""
    ADMIN = "admin"
    MEMBER = "member"


class ChatRoom(Base):
    """Chat room model for managing communication channels"""
    
    __tablename__ = "chat_rooms"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Room information
    name = Column(String(255))
    type = Column(Enum(ChatRoomType), default=ChatRoomType.ADOPTION, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Related entities (optional)
    pet_id = Column(Integer, ForeignKey("pets.id"), index=True)
    application_id = Column(Integer, ForeignKey("adoption_applications.id"), index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    pet = relationship("Pet", back_populates="chat_rooms")
    application = relationship("AdoptionApplication", back_populates="chat_room")
    members = relationship("RoomMember", back_populates="room", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="room", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ChatRoom(id={self.id}, name='{self.name}', type='{self.type}')>"
    
    @property
    def member_count(self) -> int:
        """Get number of members in the room"""
        return len(self.members)
    
    @property
    def last_message(self) -> "Message":
        """Get the last message in the room"""
        if self.messages:
            return sorted(self.messages, key=lambda m: m.created_at)[-1]
        return None


class RoomMember(Base):
    """Chat room member model for managing room membership"""
    
    __tablename__ = "room_members"
    
    # Composite primary key
    room_id = Column(Integer, ForeignKey("chat_rooms.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    
    # Member information
    role = Column(Enum(MemberRole), default=MemberRole.MEMBER, nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_read_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    room = relationship("ChatRoom", back_populates="members")
    user = relationship("User", back_populates="room_memberships")
    
    def __repr__(self):
        return f"<RoomMember(room_id={self.room_id}, user_id={self.user_id}, role='{self.role}')>"
    
    @property
    def is_admin(self) -> bool:
        """Check if member is an admin"""
        return self.role == MemberRole.ADMIN


class Message(Base):
    """Message model for storing chat messages"""
    
    __tablename__ = "messages"
    
    # Primary key (using UUID as string)
    id = Column(String(50), primary_key=True)
    
    # Message content
    room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    message_type = Column(Enum(MessageType), default=MessageType.TEXT, nullable=False)
    
    # File information (for image/file messages)
    file_url = Column(String(500))
    file_name = Column(String(255))
    file_size = Column(Integer)
    
    # Message metadata
    is_edited = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    room = relationship("ChatRoom", back_populates="messages")
    sender = relationship("User", back_populates="sent_messages")
    
    def __repr__(self):
        return f"<Message(id='{self.id}', room_id={self.room_id}, type='{self.message_type}')>"
    
    @property
    def is_text(self) -> bool:
        """Check if message is text type"""
        return self.message_type == MessageType.TEXT
    
    @property
    def is_file(self) -> bool:
        """Check if message contains a file"""
        return self.message_type in [MessageType.IMAGE, MessageType.FILE]
    
    @property
    def is_system(self) -> bool:
        """Check if message is a system message"""
        return self.message_type == MessageType.SYSTEM