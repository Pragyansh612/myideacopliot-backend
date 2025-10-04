"""Achievement model"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class Achievement(BaseModel):
    """Achievement model"""
    id: UUID
    user_id: UUID
    achievement_type: str
    title: str
    description: str
    icon: Optional[str] = None
    xp_awarded: int
    unlocked_at: datetime
    related_idea_id: Optional[UUID] = None

    class Config:
        from_attributes = True
