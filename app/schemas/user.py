"""User-related Pydantic schemas for request/response validation"""
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator


class UserProfileResponse(BaseModel):
    """User profile response schema"""
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


class UserProfileUpdate(BaseModel):
    """User profile update schema"""
    username: Optional[str] = Field(None, max_length=50, min_length=3)
    display_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)
    theme: Optional[str] = Field(None, pattern="^(light|dark)$")
    preferences: Optional[Dict[str, Any]] = None
    timezone: Optional[str] = Field(None, max_length=50)
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if v is not None and not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v


class UserSettingResponse(BaseModel):
    """User setting response schema"""
    id: str
    setting_key: str
    setting_value: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class UserSettingCreate(BaseModel):
    """User setting creation schema"""
    setting_key: str = Field(..., max_length=100, min_length=1)
    setting_value: Dict[str, Any]
    
    @field_validator('setting_key')
    @classmethod
    def validate_setting_key(cls, v):
        if not v.replace('_', '').replace('-', '').replace('.', '').isalnum():
            raise ValueError('Setting key can only contain letters, numbers, hyphens, underscores, and dots')
        return v


class UserSettingUpdate(BaseModel):
    """User setting update schema"""
    setting_value: Dict[str, Any]


class UserStatsResponse(BaseModel):
    """User statistics response schema"""
    id: str
    total_xp: int
    current_level: int
    current_streak: int
    longest_streak: int
    last_activity_date: Optional[datetime]
    ideas_created: int
    ideas_completed: int
    ai_suggestions_applied: int
    collaborations_count: int
    created_at: datetime
    updated_at: datetime