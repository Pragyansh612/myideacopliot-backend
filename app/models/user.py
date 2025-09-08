"""User domain models"""
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    """User profile model"""
    id: str
    username: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    theme: str = "light"
    preferences: Dict[str, Any] = Field(default_factory=dict)
    timezone: str = "UTC"
    created_at: datetime
    updated_at: datetime


class UserSetting(BaseModel):
    """User setting model"""
    id: str
    user_id: str
    setting_key: str
    setting_value: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class UserStats(BaseModel):
    """User statistics model"""
    id: str
    user_id: str
    total_xp: int = 0
    current_level: int = 1
    current_streak: int = 0
    longest_streak: int = 0
    last_activity_date: Optional[datetime] = None
    ideas_created: int = 0
    ideas_completed: int = 0
    ai_suggestions_applied: int = 0
    collaborations_count: int = 0
    created_at: datetime
    updated_at: datetime