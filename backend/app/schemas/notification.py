from pydantic import BaseModel
from datetime import datetime
from typing import List

class NotificationBase(BaseModel):
    title: str
    message: str

class NotificationCreate(NotificationBase):
    user_id: int

class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    notification_type: str | None = None
    link: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True

class NotificationListResponse(BaseModel):
    total: int
    unread_count: int
    notifications: List[NotificationResponse]
