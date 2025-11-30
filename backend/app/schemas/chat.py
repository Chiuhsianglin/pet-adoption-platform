"""
Chat System Pydantic Schemas
聊天系統的請求/回應資料結構
"""
from pydantic import BaseModel, Field, field_serializer
from datetime import datetime
from typing import Optional, List
from enum import Enum


# ===== Message Type Enum =====
class MessageTypeEnum(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"
    PET_CARD = "pet_card"


# ===== Pet Card Data =====
class PetCardData(BaseModel):
    """寵物卡片資料（快照）"""
    pet_id: int
    pet_name: str
    pet_species: Optional[str] = None
    pet_breed: Optional[str] = None
    pet_age: Optional[int] = None  # 保留舊欄位以向後相容
    pet_age_years: Optional[int] = None
    pet_age_months: Optional[int] = None
    pet_photo_url: Optional[str] = None


# ===== Chat Message Schemas =====
class ChatMessageBase(BaseModel):
    content: Optional[str] = None
    message_type: MessageTypeEnum = MessageTypeEnum.TEXT


class ChatMessageCreate(ChatMessageBase):
    """發送訊息請求"""
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    pet_card_data: Optional[PetCardData] = None  # 寵物卡片資料


class ChatMessageResponse(ChatMessageBase):
    """訊息回應"""
    id: int
    room_id: int
    sender_id: int
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    is_read: bool
    created_at: datetime
    pet_card_data: Optional[PetCardData] = None  # 寵物卡片資料
    
    # 發送者資訊（額外附加）
    sender_name: Optional[str] = None
    sender_email: Optional[str] = None

    @field_serializer('created_at')
    def serialize_created_at(self, dt: datetime, _info):
        """將 datetime 序列化為 UTC ISO 格式字串"""
        if dt.tzinfo is None:
            # 如果沒有時區資訊，假設為 UTC
            from datetime import timezone
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()

    class Config:
        from_attributes = True


# ===== Chat Room Schemas =====
class ChatRoomBase(BaseModel):
    user_id: int
    shelter_id: int
    pet_id: int


class ChatRoomCreate(BaseModel):
    """建立或獲取聊天室請求"""
    pet_id: int  # 前端只需提供寵物ID，後端自動查詢 shelter_id


class ChatRoomResponse(ChatRoomBase):
    """聊天室回應"""
    id: int
    last_message_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # 關聯資訊
    user_name: Optional[str] = None
    shelter_name: Optional[str] = None
    pet_name: Optional[str] = None
    pet_photo_url: Optional[str] = None
    
    # 統計資訊
    unread_count: int = 0  # 未讀訊息數
    last_message: Optional[str] = None  # 最後一則訊息內容

    @field_serializer('last_message_at', 'created_at', 'updated_at')
    def serialize_datetime(self, dt: Optional[datetime], _info):
        """將 datetime 序列化為 UTC ISO 格式字串"""
        if dt is None:
            return None
        if dt.tzinfo is None:
            # 如果沒有時區資訊，假設為 UTC
            from datetime import timezone
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()
    last_message_type: Optional[MessageTypeEnum] = None

    class Config:
        from_attributes = True


class ChatRoomListResponse(BaseModel):
    """聊天室列表回應"""
    total: int
    rooms: List[ChatRoomResponse]


# ===== Message List Schemas =====
class ChatMessageListResponse(BaseModel):
    """訊息列表回應"""
    total: int
    messages: List[ChatMessageResponse]
    has_more: bool  # 是否有更多歷史訊息


# ===== WebSocket Message Schemas =====
class WebSocketMessage(BaseModel):
    """WebSocket 訊息格式"""
    type: str = Field(..., description="訊息類型: new_message, message_read, error")
    room_id: Optional[int] = None
    message: Optional[ChatMessageResponse] = None
    error: Optional[str] = None
    unread_count: Optional[int] = None


# ===== File Upload Schemas =====
class FileUploadResponse(BaseModel):
    """檔案上傳回應"""
    file_url: str
    file_name: str
    file_size: int
    message_type: MessageTypeEnum


# ===== Mark Read Request =====
class MarkReadRequest(BaseModel):
    """標記已讀請求"""
    message_ids: List[int] = Field(..., description="要標記為已讀的訊息ID列表")
