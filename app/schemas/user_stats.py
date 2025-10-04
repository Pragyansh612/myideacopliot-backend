"""User stats schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from uuid import UUID


class UserStatsBase(BaseModel):
    """Base user stats schema"""
    total_xp: int = 0
    current_level: int = 1
    current_streak: int = 0
    longest_streak: int = 0
    last_activity_date: Optional[date] = None
    ideas_created: int = 0
    ideas_completed: int = 0
    ai_suggestions_applied: int = 0
    collaborations_count: int = 0


class UserStatsUpdate(BaseModel):
    """Schema for updating user stats"""
    total_xp: Optional[int] = None
    current_level: Optional[int] = None
    current_streak: Optional[int] = None
    longest_streak: Optional[int] = None
    last_activity_date: Optional[date] = None
    ideas_created: Optional[int] = None
    ideas_completed: Optional[int] = None
    ai_suggestions_applied: Optional[int] = None
    collaborations_count: Optional[int] = None


class UserStatsResponse(UserStatsBase):
    """Schema for user stats response"""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StatsIncrement(BaseModel):
    """Schema for incrementing specific stats"""
    field: str
    amount: int = 1
