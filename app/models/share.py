"""Share model for idea collaboration"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
import uuid


class IdeaShare(BaseModel):
    """Idea share database model"""
    id: uuid.UUID
    idea_id: uuid.UUID
    owner_id: uuid.UUID
    shared_with_id: uuid.UUID
    role: str  # 'viewer' or 'editor'
    permissions: Optional[dict] = None
    shared_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True
    
    class Config:
        from_attributes = True
