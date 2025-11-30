"""
Chat Room Model
聊天室資料模型：一個寵物對應一個聊天室
"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, String, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="申請者ID")
    shelter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="收容所ID")
    pet_id = Column(Integer, ForeignKey("pets.id", ondelete="CASCADE"), nullable=False, comment="寵物ID")
    last_message_at = Column(DateTime, nullable=True, comment="最後訊息時間")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="chat_rooms_as_user")
    shelter = relationship("User", foreign_keys=[shelter_id], backref="chat_rooms_as_shelter")
    pet = relationship("Pet", backref="chat_rooms")
    messages = relationship("ChatMessage", back_populates="room", cascade="all, delete-orphan", order_by="ChatMessage.created_at")

    # 唯一約束：確保同一個用戶、收容所、寵物只有一個聊天室
    __table_args__ = (
        UniqueConstraint('user_id', 'shelter_id', 'pet_id', name='unique_room'),
        Index('idx_user_id', 'user_id'),
        Index('idx_shelter_id', 'shelter_id'),
        Index('idx_pet_id', 'pet_id'),
        Index('idx_last_message_at', 'last_message_at'),
        {'extend_existing': True}
    )

    def __repr__(self):
        return f"<ChatRoom(id={self.id}, user_id={self.user_id}, shelter_id={self.shelter_id}, pet_id={self.pet_id})>"
