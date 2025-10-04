"""User stats schemas"""
from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, Union
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
    last_activity_date: Optional[Union[date, str]] = None
    ideas_created: Optional[int] = None
    ideas_completed: Optional[int] = None
    ai_suggestions_applied: Optional[int] = None
    collaborations_count: Optional[int] = None

    @field_validator('last_activity_date', mode='before')
    @classmethod
    def parse_date(cls, v) -> Optional[date]:
        """Parse date from string if needed"""
        if v is None or v == '':
            return None
        if isinstance(v, date):
            return v
        if isinstance(v, str):
            # Try to parse as date string (YYYY-MM-DD)
            if len(v) == 10 and v.count('-') == 2:
                try:
                    parts = v.split('-')
                    return date(int(parts[0]), int(parts[1]), int(parts[2]))
                except (ValueError, IndexError):
                    pass
            # Try datetime parsing
            try:
                dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
                return dt.date()
            except ValueError:
                pass
        return None


class UserStatsResponse(UserStatsBase):
    """Schema for user stats response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime


class StatsIncrement(BaseModel):
    """Schema for incrementing specific stats"""
    field: str
    amount: int = 1