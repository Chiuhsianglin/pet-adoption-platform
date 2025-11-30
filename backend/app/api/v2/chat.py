"""
Chat API V2 - 簡化版本 with WebSocket
"""
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, Body, WebSocket, WebSocketDisconnect, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import json

from app.database import get_db
from app.auth.dependencies import get_current_user, get_current_user_optional
from app.models.user import User, UserRole
from app.services.factories import ChatServiceFactory
from app.exceptions import (
    ChatRoomNotFoundError,
    MessageNotFoundError,
    PetNotFoundError,
    PermissionDeniedError
)

router = APIRouter()


# ===== WebSocket 連接管理器 =====
class ConnectionManager:
    """
    WebSocket 連接管理器
    支援全局單一連接，用戶可訂閱多個聊天室
    """
    def __init__(self):
        # 儲存連接：{user_id: websocket}
        self.active_connections: Dict[int, WebSocket] = {}
        # 儲存用戶訂閱的聊天室：{user_id: set(room_ids)}
        self.user_rooms: Dict[int, set] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """用戶連接"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_rooms[user_id] = set()
        print(f"✅ User {user_id} connected to WebSocket V2")

    def disconnect(self, user_id: int):
        """用戶斷線"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.user_rooms:
            del self.user_rooms[user_id]
        print(f"❌ User {user_id} disconnected from WebSocket V2")

    def subscribe_room(self, user_id: int, room_id: int):
        """訂閱聊天室"""
        if user_id in self.user_rooms:
            self.user_rooms[user_id].add(room_id)
            print(f"📢 User {user_id} subscribed to room {room_id}")

    def unsubscribe_room(self, user_id: int, room_id: int):
        """取消訂閱聊天室"""
        if user_id in self.user_rooms and room_id in self.user_rooms[user_id]:
            self.user_rooms[user_id].remove(room_id)
            print(f"🔕 User {user_id} unsubscribed from room {room_id}")

    async def send_personal_message(self, message: dict, user_id: int):
        """發送訊息給特定用戶"""
        if user_id in self.active_connections:
            try:
                websocket = self.active_connections[user_id]
                await websocket.send_json(message)
            except Exception as e:
                print(f"❌ Error sending message to user {user_id}: {e}")
                self.disconnect(user_id)

    async def broadcast_to_room(self, message: dict, room_id: int, exclude_user: Optional[int] = None):
        """廣播訊息給聊天室的所有訂閱者（可排除特定用戶）"""
        for user_id, rooms in self.user_rooms.items():
            if room_id in rooms and user_id != exclude_user:
                await self.send_personal_message(message, user_id)

# 全局連接管理器
manager = ConnectionManager()


# ===== WebSocket Endpoint =====
@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    WebSocket 連接端點
    前端連接：ws://localhost:8000/api/v2/chat/ws?token=<jwt_token>
    """
    # 驗證 token
    try:
        from app.auth.jwt_handler import jwt_handler
        payload = jwt_handler.decode_token(token)
        user_id = payload.get("user_id")
        
        if not user_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
            
    except Exception as e:
        print(f"❌ WebSocket authentication failed: {e}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # 建立連接
    await manager.connect(websocket, user_id)

    try:
        while True:
            # 接收前端訊息
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            action = message_data.get("action")
            
            # 訂閱聊天室
            if action == "subscribe":
                room_id = message_data.get("room_id")
                if room_id:
                    manager.subscribe_room(user_id, room_id)
                    await manager.send_personal_message({
                        "type": "subscribed",
                        "room_id": room_id
                    }, user_id)
            
            # 取消訂閱聊天室
            elif action == "unsubscribe":
                room_id = message_data.get("room_id")
                if room_id:
                    manager.unsubscribe_room(user_id, room_id)
                    await manager.send_personal_message({
                        "type": "unsubscribed",
                        "room_id": room_id
                    }, user_id)
            
            # 心跳檢測
            elif action == "ping":
                await manager.send_personal_message({
                    "type": "pong"
                }, user_id)

    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        manager.disconnect(user_id)


class CreateChatRoomRequest(BaseModel):
    """創建聊天室請求"""
    pet_id: int


class SendMessageRequest(BaseModel):
    """發送訊息請求"""
    content: str


class SendImageRequest(BaseModel):
    """發送圖片訊息請求"""
    image_url: str


class SendFileRequest(BaseModel):
    """發送檔案訊息請求"""
    file_url: str
    file_name: str
    file_size: int


def _serialize_room(room) -> Dict[str, Any]:
    """序列化聊天室"""
    from app.services.s3 import S3Service
    
    # 基本聊天室資訊
    room_data = {
        "id": room.id,
        "user_id": room.user_id,
        "shelter_id": room.shelter_id,
        "pet_id": room.pet_id,
        "last_message_at": room.last_message_at.isoformat() if room.last_message_at else None,
        "created_at": room.created_at.isoformat() if room.created_at else None,
        "unread_count": 0,  # 默認值，可以後續實現
        "last_message": None,  # 默認值
        "last_message_type": None,  # 默認值
    }
    
    # 如果有關聯的訊息，獲取最後一條
    from sqlalchemy import inspect
    insp = inspect(room)
    
    if 'messages' not in insp.unloaded and hasattr(room, 'messages') and room.messages:
        # 訊息已經加載，取最後一條
        last_msg = room.messages[-1] if room.messages else None
        if last_msg:
            room_data["last_message"] = last_msg.content or "[圖片]" if last_msg.message_type.value == "image" else last_msg.content
            room_data["last_message_type"] = last_msg.message_type.value if hasattr(last_msg.message_type, 'value') else last_msg.message_type
    
    # 如果有關聯的寵物資訊，序列化寵物資料
    if hasattr(room, 'pet') and room.pet:
        pet = room.pet
        s3_service = S3Service()
        
        # 添加 pet_name 供 shelter 標題使用
        room_data["pet_name"] = pet.name
        
        # 序列化寵物照片
        photos_data = []
        pet_photo_url = None  # 用於列表顯示的主要照片
        
        if hasattr(pet, 'photos') and pet.photos:
            for photo in pet.photos:
                file_url = None
                if photo.file_key and s3_service.use_s3 and s3_service.s3_client:
                    try:
                        file_url = s3_service.generate_presigned_url(photo.file_key, expiration=604800)
                        # 設置主要照片為列表顯示圖片
                        if photo.is_primary and not pet_photo_url:
                            pet_photo_url = file_url
                    except Exception as e:
                        print(f"⚠️ Failed to generate presigned URL: {e}")
                
                photos_data.append({
                    "id": photo.id,
                    "file_url": file_url,
                    "file_key": photo.file_key,
                    "is_primary": photo.is_primary if hasattr(photo, 'is_primary') else False,
                })
            
            # 如果沒有主要照片，使用第一張照片
            if not pet_photo_url and photos_data and photos_data[0]["file_url"]:
                pet_photo_url = photos_data[0]["file_url"]
        
        # 添加 pet_photo_url 供前端列表顯示
        room_data["pet_photo_url"] = pet_photo_url
        
        room_data["pet"] = {
            "id": pet.id,
            "name": pet.name,
            "species": pet.species.value if hasattr(pet.species, 'value') else pet.species,
            "breed": pet.breed,
            "age_years": pet.age_years,
            "age_months": pet.age_months,
            "gender": pet.gender.value if hasattr(pet.gender, 'value') else pet.gender,
            "size": pet.size.value if hasattr(pet.size, 'value') else pet.size,
            "color": pet.color if hasattr(pet, 'color') else None,
            "description": pet.description if hasattr(pet, 'description') else None,
            "status": pet.status.value if hasattr(pet.status, 'value') else pet.status,
            "photos": photos_data,
        }
    
    # 如果有關聯的用戶資訊（檢查是否已加載）
    from sqlalchemy import inspect
    
    insp = inspect(room)
    
    # 檢查 user 是否已加載
    if 'user' not in insp.unloaded and hasattr(room, 'user'):
        user = room.user
        if user:
            room_data["user_name"] = user.name if hasattr(user, 'name') else None
            room_data["user_email"] = user.email if hasattr(user, 'email') else None
    
    # 檢查 shelter 是否已加載
    if 'shelter' not in insp.unloaded and hasattr(room, 'shelter'):
        shelter = room.shelter
        if shelter:
            room_data["shelter_name"] = shelter.name if hasattr(shelter, 'name') else None
            room_data["shelter_email"] = shelter.email if hasattr(shelter, 'email') else None
    
    return room_data


def _serialize_message(msg) -> Dict[str, Any]:
    """序列化訊息"""
    return {
        "id": msg.id,
        "room_id": msg.room_id,
        "sender_id": msg.sender_id,
        "message_type": msg.message_type.value if hasattr(msg.message_type, 'value') else msg.message_type,
        "content": msg.content,
        "file_url": msg.file_url,
        "file_name": msg.file_name,
        "file_size": msg.file_size,
        "is_read": msg.is_read,
        "created_at": msg.created_at.isoformat() if msg.created_at else None,
    }


def _handle_error(error: Exception):
    """處理錯誤"""
    if isinstance(error, (ChatRoomNotFoundError, MessageNotFoundError, PetNotFoundError)):
        raise HTTPException(status_code=404, detail=str(error))
    elif isinstance(error, PermissionDeniedError):
        raise HTTPException(status_code=403, detail=str(error))
    else:
        raise HTTPException(status_code=500, detail=str(error))


@router.post("/rooms", status_code=status.HTTP_201_CREATED)
async def create_or_get_room(
    request: CreateChatRoomRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    創建或獲取聊天室 - V2
    
    - 前端只需提供 pet_id (JSON body)
    - 後端自動查詢寵物的 shelter_id
    - user_id 從當前登入用戶獲取
    """
    try:
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        from app.models.pet import Pet
        
        print(f"📞 Creating chat room for pet_id={request.pet_id}, user_id={current_user.id}")
        
        # 查詢寵物的 shelter_id
        query = select(Pet).where(Pet.id == request.pet_id)
        result = await db.execute(query)
        pet = result.scalar_one_or_none()
        
        if not pet:
            print(f"❌ Pet {request.pet_id} not found")
            raise PetNotFoundError(f"Pet {request.pet_id} not found")
        
        print(f"✅ Pet found: {pet.name}, shelter_id={pet.shelter_id}")
        
        service = ChatServiceFactory.create(db)
        room = await service.get_or_create_room(
            user_id=current_user.id,
            shelter_id=pet.shelter_id,
            pet_id=request.pet_id
        )
        
        print(f"✅ Chat room created/retrieved: room_id={room.id}")
        
        # 重新查詢聊天室以包含所有關聯資料
        from app.models.chat_room import ChatRoom
        room_query = select(ChatRoom).options(
            selectinload(ChatRoom.pet).selectinload(Pet.photos),
            selectinload(ChatRoom.user),
            selectinload(ChatRoom.shelter)
        ).where(ChatRoom.id == room.id)
        room_result = await db.execute(room_query)
        room_with_relations = room_result.scalar_one()
        
        return _serialize_room(room_with_relations)
    except Exception as e:
        print(f"❌ Error in create_or_get_room: {e}")
        _handle_error(e)


@router.get("/rooms/{room_id}")
async def get_room(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """獲取聊天室詳情"""
    try:
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        from app.models.chat_room import ChatRoom
        from app.models.pet import Pet
        
        # 查詢聊天室（包含關聯資料）
        query = select(ChatRoom).options(
            selectinload(ChatRoom.pet).selectinload(Pet.photos),
            selectinload(ChatRoom.user),
            selectinload(ChatRoom.shelter)
        ).where(ChatRoom.id == room_id)
        
        result = await db.execute(query)
        room = result.scalar_one_or_none()
        
        if not room:
            raise ChatRoomNotFoundError(f"Chat room {room_id} not found")
        
        # 驗證權限
        if room.user_id != current_user.id and room.shelter_id != current_user.id:
            raise PermissionDeniedError("You don't have permission to access this chat room")
        
        return _serialize_room(room)
    except Exception as e:
        _handle_error(e)


@router.get("/rooms")
async def list_rooms(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """列出聊天室（只顯示有訊息的聊天室）"""
    try:
        from sqlalchemy import select, exists, desc, func, and_
        from sqlalchemy.orm import selectinload
        from app.models.chat_room import ChatRoom
        from app.models.chat_message import ChatMessage
        from app.models.pet import Pet
        
        print(f"📋 Listing rooms for user_id={current_user.id}, role={current_user.role}")
        
        # 根據角色查詢聊天室（包含關聯資料），並過濾出有訊息的聊天室
        if current_user.role == UserRole.adopter:
            # 子查詢：檢查聊天室是否有訊息
            has_messages = select(ChatMessage.id).where(
                ChatMessage.room_id == ChatRoom.id
            ).limit(1).exists()
            
            query = select(ChatRoom).options(
                selectinload(ChatRoom.pet).selectinload(Pet.photos),
                selectinload(ChatRoom.shelter)
            ).where(
                ChatRoom.user_id == current_user.id
            ).where(
                has_messages  # 只顯示有訊息的聊天室
            ).order_by(desc(ChatRoom.last_message_at))
        elif current_user.role == UserRole.shelter:
            # 子查詢：檢查聊天室是否有訊息
            has_messages = select(ChatMessage.id).where(
                ChatMessage.room_id == ChatRoom.id
            ).limit(1).exists()
            
            query = select(ChatRoom).options(
                selectinload(ChatRoom.pet).selectinload(Pet.photos),
                selectinload(ChatRoom.user)
            ).where(
                ChatRoom.shelter_id == current_user.id
            ).where(
                has_messages  # 只顯示有訊息的聊天室
            ).order_by(desc(ChatRoom.last_message_at))
        else:
            raise HTTPException(status_code=403, detail="Invalid role")
        
        result = await db.execute(query)
        rooms = result.scalars().all()
        
        print(f"✅ Found {len(rooms)} rooms with messages")
        
        # 為每個聊天室獲取最後一條訊息和未讀數量
        rooms_data = []
        for room in rooms:
            # 獲取該聊天室的最後一條訊息
            last_msg_query = select(ChatMessage).where(
                ChatMessage.room_id == room.id
            ).order_by(desc(ChatMessage.created_at)).limit(1)
            last_msg_result = await db.execute(last_msg_query)
            last_msg = last_msg_result.scalar_one_or_none()
            
            # 計算未讀訊息數量（不是當前用戶發送的且未讀的訊息）
            unread_query = select(func.count(ChatMessage.id)).where(
                and_(
                    ChatMessage.room_id == room.id,
                    ChatMessage.sender_id != current_user.id,
                    ChatMessage.is_read == False
                )
            )
            unread_result = await db.execute(unread_query)
            unread_count = unread_result.scalar() or 0
            
            # 序列化聊天室
            room_data = _serialize_room(room)
            
            # 更新未讀數量
            room_data["unread_count"] = unread_count
            
            # 添加最後一條訊息信息
            if last_msg:
                if last_msg.message_type.value == "text":
                    room_data["last_message"] = last_msg.content
                elif last_msg.message_type.value == "image":
                    room_data["last_message"] = "[圖片]"
                elif last_msg.message_type.value == "file":
                    room_data["last_message"] = "[檔案]"
                else:
                    room_data["last_message"] = "[訊息]"
                room_data["last_message_type"] = last_msg.message_type.value
            
            rooms_data.append(room_data)
        
        # 返回格式與 V1 兼容
        return {"rooms": rooms_data}
    except Exception as e:
        print(f"❌ Error in list_rooms: {e}")
        import traceback
        traceback.print_exc()
        _handle_error(e)


@router.get("/rooms/{room_id}/messages")
async def get_messages(
    room_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """獲取聊天室訊息"""
    try:
        from sqlalchemy import select
        from app.models.chat_room import ChatRoom
        from app.repositories.chat import MessageRepository
        
        print(f"📨 Getting messages for room_id={room_id}, user_id={current_user.id}")
        
        # 驗證權限：檢查用戶是否是聊天室參與者
        room_query = select(ChatRoom).where(ChatRoom.id == room_id)
        room_result = await db.execute(room_query)
        room = room_result.scalar_one_or_none()
        
        if not room:
            raise ChatRoomNotFoundError(f"Chat room {room_id} not found")
        
        if room.user_id != current_user.id and room.shelter_id != current_user.id:
            raise PermissionDeniedError("You don't have permission to access this chat room")
        
        print(f"✅ Permission verified")
        
        # 獲取訊息
        message_repo = MessageRepository(db)
        messages = await message_repo.get_room_messages(room_id, skip=skip, limit=limit)
        
        print(f"✅ Found {len(messages)} messages")
        
        return {
            "items": [_serialize_message(msg) for msg in messages],
            "total": len(messages)
        }
    except Exception as e:
        print(f"❌ Error in get_messages: {e}")
        import traceback
        traceback.print_exc()
        _handle_error(e)


@router.post("/rooms/{room_id}/messages/text")
async def send_text_message(
    room_id: int,
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """發送文字訊息（支援 WebSocket 即時推送）"""
    try:
        service = ChatServiceFactory.create(db)
        # 修正參數順序：(room_id, sender_id, content)
        message = await service.send_text_message(
            room_id,
            current_user.id,
            request.content
        )
        
        # 序列化訊息
        message_data = _serialize_message(message)
        
        # 透過 WebSocket 廣播給聊天室的其他訂閱者
        await manager.broadcast_to_room(
            {
                "type": "new_message",
                "room_id": room_id,
                "message": message_data
            },
            room_id,
            exclude_user=current_user.id
        )
        
        print(f"✅ Message sent and broadcasted in room {room_id}")
        
        return message_data
    except Exception as e:
        _handle_error(e)


@router.post("/rooms/{room_id}/messages/image")
async def send_image_message(
    room_id: int,
    request: SendImageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """發送圖片訊息（支援 WebSocket 即時推送）"""
    try:
        service = ChatServiceFactory.create(db)
        # 修正參數順序：(room_id, sender_id, file_url, file_name, file_size)
        # 從 URL 提取文件名
        file_name = request.image_url.split('/')[-1] if request.image_url else "image.jpg"
        message = await service.send_image_message(
            room_id,
            current_user.id,
            request.image_url,
            file_name,
            0  # 文件大小未知
        )
        
        # 序列化訊息
        message_data = _serialize_message(message)
        
        # 透過 WebSocket 廣播給聊天室的其他訂閱者
        await manager.broadcast_to_room(
            {
                "type": "new_message",
                "room_id": room_id,
                "message": message_data
            },
            room_id,
            exclude_user=current_user.id
        )
        
        print(f"✅ Image message sent and broadcasted in room {room_id}")
        
        return message_data
    except Exception as e:
        _handle_error(e)


@router.post("/rooms/{room_id}/messages/file")
async def send_file_message(
    room_id: int,
    request: SendFileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """發送檔案訊息（支援 WebSocket 即時推送）"""
    try:
        service = ChatServiceFactory.create(db)
        message = await service.send_file_message(
            room_id,
            current_user.id,
            request.file_url,
            request.file_name,
            request.file_size
        )
        
        # 序列化訊息
        message_data = _serialize_message(message)
        
        # 透過 WebSocket 廣播給聊天室的其他訂閱者
        await manager.broadcast_to_room(
            {
                "type": "new_message",
                "room_id": room_id,
                "message": message_data
            },
            room_id,
            exclude_user=current_user.id
        )
        
        print(f"✅ File message sent and broadcasted in room {room_id}")
        
        return message_data
    except Exception as e:
        _handle_error(e)


@router.post("/rooms/{room_id}/upload")
async def upload_file(
    room_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """上傳聊天文件（圖片或文件）"""
    try:
        from app.services.s3 import s3_service
        from sqlalchemy import select
        from app.models.chat_room import ChatRoom
        
        # 驗證聊天室權限
        room_query = select(ChatRoom).where(ChatRoom.id == room_id)
        room_result = await db.execute(room_query)
        room = room_result.scalar_one_or_none()
        
        if not room:
            raise ChatRoomNotFoundError(f"Chat room {room_id} not found")
        
        if room.user_id != current_user.id and room.shelter_id != current_user.id:
            raise PermissionDeniedError("You don't have permission to access this chat room")
        
        # 確定文件類型
        content_type = file.content_type or ""
        is_image = content_type.startswith("image/")
        
        # 上傳到 S3
        file_content = await file.read()
        
        upload_result = s3_service.upload_file(
            file_content,
            file.filename or "file",
            "chat",  # category
            content_type
        )
        
        print(f"✅ Upload result: {upload_result}")
        
        # 返回上傳結果
        return {
            "file_url": upload_result["file_url"],
            "file_name": file.filename,
            "file_size": len(file_content),
            "message_type": "image" if is_image else "file"
        }
    except Exception as e:
        print(f"❌ Upload error: {e}")
        _handle_error(e)


@router.get("/rooms/{room_id}/unread-count")
async def get_room_unread_count(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, int]:
    """獲取聊天室未讀數"""
    try:
        service = ChatServiceFactory.create(db)
        count = await service.get_unread_count(current_user.id, room_id)
        return {"unread_count": count}
    except Exception as e:
        _handle_error(e)


@router.get("/unread-count")
async def get_total_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, int]:
    """獲取總未讀數"""
    try:
        service = ChatServiceFactory.create(db)
        count = await service.get_total_unread_count(current_user.id)
        return {"unread_count": count}
    except Exception as e:
        _handle_error(e)


@router.put("/rooms/{room_id}/read")
async def mark_messages_as_read(
    room_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """標記聊天室訊息為已讀"""
    try:
        from sqlalchemy import select, update
        from app.models.chat_room import ChatRoom
        from app.models.chat_message import ChatMessage
        
        # 驗證權限
        room_query = select(ChatRoom).where(ChatRoom.id == room_id)
        room_result = await db.execute(room_query)
        room = room_result.scalar_one_or_none()
        
        if not room:
            raise ChatRoomNotFoundError(f"Chat room {room_id} not found")
        
        if room.user_id != current_user.id and room.shelter_id != current_user.id:
            raise PermissionDeniedError("You don't have permission to access this chat room")
        
        # 標記所有非當前用戶發送的訊息為已讀
        update_stmt = (
            update(ChatMessage)
            .where(ChatMessage.room_id == room_id)
            .where(ChatMessage.sender_id != current_user.id)
            .where(ChatMessage.is_read == False)
            .values(is_read=True)
        )
        
        await db.execute(update_stmt)
        await db.commit()
        
        return {"status": "success"}
    except Exception as e:
        print(f"❌ Error in mark_messages_as_read: {e}")
        _handle_error(e)
