"""
Chat Service
聊天室與訊息業務邏輯層
"""
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.repositories.chat import ChatRepository, MessageRepository
from app.repositories import UserRepository, PetRepository
from app.models.chat_room import ChatRoom
from app.models.chat_message import ChatMessage, MessageType
from app.exceptions import (
    ChatRoomNotFoundError,
    MessageNotFoundError,
    PetNotFoundError,
    UserNotFoundError,
    PermissionDeniedError
)


class ChatService:
    """聊天室與訊息業務邏輯"""
    
    def __init__(
        self,
        chat_repo: ChatRepository,
        message_repo: MessageRepository,
        user_repo: UserRepository,
        pet_repo: PetRepository
    ):
        self.chat_repo = chat_repo
        self.message_repo = message_repo
        self.user_repo = user_repo
        self.pet_repo = pet_repo
    
    async def get_or_create_room(
        self,
        user_id: int,
        shelter_id: int,
        pet_id: int
    ) -> ChatRoom:
        """獲取或創建聊天室"""
        # 驗證寵物存在
        pet = await self.pet_repo.get_by_id(pet_id)
        if not pet:
            raise PetNotFoundError(f"寵物 ID {pet_id} 不存在")
        
        # 驗證收容所存在
        shelter = await self.user_repo.get_by_id(shelter_id)
        if not shelter or shelter.role != "shelter":
            raise UserNotFoundError(f"收容所 ID {shelter_id} 不存在")
        
        return await self.chat_repo.get_or_create_room(user_id, shelter_id, pet_id)
    
    async def get_room(self, room_id: int, user_id: int) -> ChatRoom:
        """獲取聊天室詳情（權限檢查）"""
        room = await self.chat_repo.get_room_with_relations(room_id)
        if not room:
            raise ChatRoomNotFoundError(f"聊天室 ID {room_id} 不存在")
        
        # 權限檢查：只有參與者可以查看
        if room.user_id != user_id and room.shelter_id != user_id:
            raise PermissionDeniedError("您沒有權限查看此聊天室")
        
        return room
    
    async def get_user_rooms(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ChatRoom]:
        """獲取用戶的聊天室列表"""
        return await self.chat_repo.get_user_rooms(user_id, skip, limit)
    
    async def get_shelter_rooms(
        self,
        shelter_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ChatRoom]:
        """獲取收容所的聊天室列表"""
        return await self.chat_repo.get_shelter_rooms(shelter_id, skip, limit)
    
    async def get_room_messages(
        self,
        room_id: int,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ChatMessage]:
        """獲取聊天室訊息（權限檢查）"""
        # 驗證權限
        room = await self.get_room(room_id, user_id)
        
        # 標記訊息為已讀
        await self.message_repo.mark_as_read(room_id, user_id)
        
        return await self.message_repo.get_room_messages(room_id, skip, limit)
    
    async def send_text_message(
        self,
        room_id: int,
        sender_id: int,
        content: str
    ) -> ChatMessage:
        """發送文字訊息"""
        # 驗證權限
        room = await self.get_room(room_id, sender_id)
        
        # 創建訊息
        message = await self.message_repo.create_text_message(room_id, sender_id, content)
        
        # 更新聊天室最後訊息時間
        await self.chat_repo.update_last_message_time(room_id)
        
        return message
    
    async def send_image_message(
        self,
        room_id: int,
        sender_id: int,
        file_url: str,
        file_name: str,
        file_size: int
    ) -> ChatMessage:
        """發送圖片訊息"""
        room = await self.get_room(room_id, sender_id)
        
        message = await self.message_repo.create_image_message(
            room_id, sender_id, file_url, file_name, file_size
        )
        
        await self.chat_repo.update_last_message_time(room_id)
        
        return message
    
    async def send_file_message(
        self,
        room_id: int,
        sender_id: int,
        file_url: str,
        file_name: str,
        file_size: int
    ) -> ChatMessage:
        """發送檔案訊息"""
        room = await self.get_room(room_id, sender_id)
        
        message = await self.message_repo.create_file_message(
            room_id, sender_id, file_url, file_name, file_size
        )
        
        await self.chat_repo.update_last_message_time(room_id)
        
        return message
    
    async def get_unread_count(self, room_id: int, user_id: int) -> int:
        """獲取聊天室未讀訊息數"""
        return await self.message_repo.get_unread_count(room_id, user_id)
    
    async def get_total_unread_count(self, user_id: int) -> int:
        """獲取用戶所有聊天室的未讀訊息總數"""
        return await self.message_repo.get_user_total_unread_count(user_id)
    
    async def delete_message(
        self,
        message_id: int,
        user_id: int
    ) -> bool:
        """刪除訊息（只能刪除自己的訊息）"""
        message = await self.message_repo.get_by_id(message_id)
        if not message:
            raise MessageNotFoundError(f"訊息 ID {message_id} 不存在")
        
        if message.sender_id != user_id:
            raise PermissionDeniedError("只能刪除自己的訊息")
        
        return await self.message_repo.delete(message_id)
