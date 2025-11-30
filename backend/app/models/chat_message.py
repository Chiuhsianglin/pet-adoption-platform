"""
Chat Message Model
聊天訊息資料模型：支援文字、圖片、檔案、寵物卡片
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class MessageType(str, enum.Enum):
    """訊息類型"""
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    PET_CARD = "pet_card"


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.id", ondelete="CASCADE"), nullable=False, comment="聊天室ID")
    sender_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="發送者ID")
    message_type = Column(SQLEnum(MessageType), nullable=False, default=MessageType.TEXT, comment="訊息類型")
    content = Column(Text, nullable=True, comment="文字內容")
    file_url = Column(String(500), nullable=True, comment="S3檔案URL")
    file_name = Column(String(255), nullable=True, comment="檔案名稱")
    file_size = Column(Integer, nullable=True, comment="檔案大小(bytes)")
    is_read = Column(Boolean, default=False, nullable=False, comment="是否已讀")
    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    room = relationship("ChatRoom", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id])

    # 索引
    __table_args__ = (
        Index('idx_room_id', 'room_id'),
        Index('idx_sender_id', 'sender_id'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_read', 'is_read'),
        Index('idx_room_created', 'room_id', 'created_at'),
        {'extend_existing': True}
    )

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, room_id={self.room_id}, type={self.message_type})>"
