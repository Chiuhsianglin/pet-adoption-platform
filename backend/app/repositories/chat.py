"""
Chat Repository
聊天室與訊息資料存取層
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.chat_room import ChatRoom
from app.models.chat_message import ChatMessage, MessageType
from app.models.user import User


class ChatRepository(BaseRepository[ChatRoom]):
    """聊天室 Repository"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, ChatRoom)
    
    async def get_or_create_room(
        self,
        user_id: int,
        shelter_id: int,
        pet_id: int
    ) -> ChatRoom:
        """獲取或創建聊天室"""
        # 先查詢是否存在
        result = await self.db.execute(
            select(ChatRoom).where(
                and_(
                    ChatRoom.user_id == user_id,
                    ChatRoom.shelter_id == shelter_id,
                    ChatRoom.pet_id == pet_id
                )
            )
        )
        room = result.scalar_one_or_none()
        
        if room:
            return room
        
        # 不存在則創建
        room = ChatRoom(
            user_id=user_id,
            shelter_id=shelter_id,
            pet_id=pet_id
        )
        return await self.create(room)
    
    async def get_room_with_relations(self, room_id: int) -> Optional[ChatRoom]:
        """獲取聊天室（包含關聯）"""
        result = await self.db.execute(
            select(ChatRoom)
            .options(
                selectinload(ChatRoom.user),
                selectinload(ChatRoom.shelter),
                selectinload(ChatRoom.pet)
            )
            .where(ChatRoom.id == room_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_rooms(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ChatRoom]:
        """獲取用戶的所有聊天室"""
        result = await self.db.execute(
            select(ChatRoom)
            .options(
                selectinload(ChatRoom.shelter),
                selectinload(ChatRoom.pet)
            )
            .where(ChatRoom.user_id == user_id)
            .order_by(desc(ChatRoom.last_message_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_shelter_rooms(
        self,
        shelter_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ChatRoom]:
        """獲取收容所的所有聊天室"""
        result = await self.db.execute(
            select(ChatRoom)
            .options(
                selectinload(ChatRoom.user),
                selectinload(ChatRoom.pet)
            )
            .where(ChatRoom.shelter_id == shelter_id)
            .order_by(desc(ChatRoom.last_message_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def update_last_message_time(self, room_id: int) -> None:
        """更新聊天室最後訊息時間"""
        room = await self.get_by_id(room_id)
        if room:
            room.last_message_at = datetime.utcnow()
            await self.db.commit()


class MessageRepository(BaseRepository[ChatMessage]):
    """訊息 Repository"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, ChatMessage)
    
    async def get_room_messages(
        self,
        room_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ChatMessage]:
        """獲取聊天室訊息（按時間降序，最新的在前）"""
        result = await self.db.execute(
            select(ChatMessage)
            .options(
                selectinload(ChatMessage.sender)
            )
            .where(ChatMessage.room_id == room_id)
            .order_by(ChatMessage.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def create_text_message(
        self,
        room_id: int,
        sender_id: int,
        content: str
    ) -> ChatMessage:
        """創建文字訊息"""
        message = ChatMessage(
            room_id=room_id,
            sender_id=sender_id,
            message_type=MessageType.TEXT,
            content=content
        )
        return await self.create(message)
    
    async def create_image_message(
        self,
        room_id: int,
        sender_id: int,
        file_url: str,
        file_name: str,
        file_size: int
    ) -> ChatMessage:
        """創建圖片訊息"""
        message = ChatMessage(
            room_id=room_id,
            sender_id=sender_id,
            message_type=MessageType.IMAGE,
            file_url=file_url,
            file_name=file_name,
            file_size=file_size
        )
        return await self.create(message)
    
    async def create_file_message(
        self,
        room_id: int,
        sender_id: int,
        file_url: str,
        file_name: str,
        file_size: int
    ) -> ChatMessage:
        """創建檔案訊息"""
        message = ChatMessage(
            room_id=room_id,
            sender_id=sender_id,
            message_type=MessageType.FILE,
            file_url=file_url,
            file_name=file_name,
            file_size=file_size
        )
        return await self.create(message)
    
    async def mark_as_read(
        self,
        room_id: int,
        user_id: int
    ) -> int:
        """標記聊天室訊息為已讀（排除發送者自己的訊息）"""
        from sqlalchemy import update
        
        stmt = (
            update(ChatMessage)
            .where(
                and_(
                    ChatMessage.room_id == room_id,
                    ChatMessage.sender_id != user_id,
                    ChatMessage.is_read == False
                )
            )
            .values(is_read=True)
        )
        
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount
    
    async def get_unread_count(self, room_id: int, user_id: int) -> int:
        """獲取用戶在聊天室的未讀訊息數"""
        result = await self.db.execute(
            select(func.count())
            .select_from(ChatMessage)
            .where(
                and_(
                    ChatMessage.room_id == room_id,
                    ChatMessage.sender_id != user_id,
                    ChatMessage.is_read == False
                )
            )
        )
        return result.scalar()
    
    async def get_user_total_unread_count(self, user_id: int) -> int:
        """獲取用戶所有聊天室的未讀訊息總數"""
        result = await self.db.execute(
            select(func.count())
            .select_from(ChatMessage)
            .join(ChatRoom, ChatMessage.room_id == ChatRoom.id)
            .where(
                and_(
                    or_(
                        ChatRoom.user_id == user_id,
                        ChatRoom.shelter_id == user_id
                    ),
                    ChatMessage.sender_id != user_id,
                    ChatMessage.is_read == False
                )
            )
        )
        return result.scalar()
