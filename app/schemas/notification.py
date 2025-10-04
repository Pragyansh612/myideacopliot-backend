"""Notification schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class NotificationBase(BaseModel):
    """Base notification schema"""
    type: str
    title: str
    message: str
    related_idea_id: Optional[UUID] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[UUID] = None
    action_url: Optional[str] = None
    priority: Optional[str] = "normal"
    expires_at: Optional[datetime] = None


class NotificationCreate(NotificationBase):
    """Schema for creating a notification"""
    pass


class NotificationUpdate(BaseModel):
    """Schema for updating a notification"""
    is_read: Optional[bool] = None


class NotificationResponse(NotificationBase):
    """Schema for notification response"""
    id: UUID
    user_id: UUID
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MotivationRequest(BaseModel):
    """Schema for motivation request"""
    message_type: Optional[str] = "encouragement"
