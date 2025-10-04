"""Comment model for threaded discussions"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
import uuid


class Comment(BaseModel):
    """Comment database model"""
    id: uuid.UUID
    user_id: uuid.UUID
    idea_id: Optional[uuid.UUID] = None
    feature_id: Optional[uuid.UUID] = None
    parent_comment_id: Optional[uuid.UUID] = None
    content: str
    is_ai_generated: bool = False
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True