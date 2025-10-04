"""Notification model"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class Notification(BaseModel):
    """Notification model"""
    id: UUID
    user_id: UUID
    type: str
    title: str
    message: str
    related_idea_id: Optional[UUID] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[UUID] = None
    action_url: Optional[str] = None
    is_read: bool = False
    read_at: Optional[datetime] = None
    priority: Optional[str] = "normal"
    expires_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True