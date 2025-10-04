### filename: app/models/user_stats.py
"""User stats model"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Union
from datetime import datetime, date
from uuid import UUID


class UserStats(BaseModel):
    """User statistics model"""
    id: UUID
    user_id: UUID
    total_xp: int = 0
    current_level: int = 1
    current_streak: int = 0
    longest_streak: int = 0
    last_activity_date: Optional[date] = None
    ideas_created: int = 0
    ideas_completed: int = 0
    ai_suggestions_applied: int = 0
    collaborations_count: int = 0
    created_at: datetime
    updated_at: datetime

    @field_validator('last_activity_date', mode='before')
    @classmethod
    def parse_date(cls, v):
        """Parse date from string if needed"""
        if v is None:
            return None
        if isinstance(v, date) and not isinstance(v, datetime):
            return v
        if isinstance(v, datetime):
            return v.date()
        if isinstance(v, str):
            try:
                # Try parsing as date (YYYY-MM-DD)
                return date.fromisoformat(v)
            except ValueError:
                # If it fails, try parsing as datetime and extract date
                try:
                    dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
                    return dt.date()
                except ValueError:
                    return None
        return v

    class Config:
        from_attributes = True