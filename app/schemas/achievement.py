"""Achievement schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class AchievementBase(BaseModel):
    """Base achievement schema"""
    achievement_type: str
    title: str
    description: str
    icon: Optional[str] = None
    xp_awarded: int
    related_idea_id: Optional[UUID] = None


class AchievementCreate(AchievementBase):
    """Schema for creating an achievement"""
    pass


class AchievementResponse(AchievementBase):
    """Schema for achievement response"""
    id: UUID
    user_id: UUID
    unlocked_at: datetime

    class Config:
        from_attributes = True


class AchievementDefinition(BaseModel):
    """Schema for achievement definition (template)"""
    achievement_type: str
    title: str
    description: str
    icon: Optional[str] = None
    xp_awarded: int
    unlock_condition: str