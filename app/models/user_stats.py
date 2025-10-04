"""User stats model"""
from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, Union
from datetime import datetime, date
from uuid import UUID


class UserStats(BaseModel):
    """User statistics model"""
    model_config = ConfigDict(from_attributes=True)
    
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