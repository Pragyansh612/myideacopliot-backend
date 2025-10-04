"""Comment schemas for request/response"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
import uuid


class CommentCreate(BaseModel):
    """Schema for creating a comment"""
    content: str = Field(..., min_length=1, max_length=5000, description="Comment content")
    parent_comment_id: Optional[uuid.UUID] = Field(None, description="Parent comment for threading")


class CommentUpdate(BaseModel):
    """Schema for updating a comment"""
    content: str = Field(..., min_length=1, max_length=5000, description="Updated comment content")


class CommentResponse(BaseModel):
    """Schema for comment response"""
    id: uuid.UUID
    user_id: uuid.UUID
    author_email: Optional[str] = None
    idea_id: Optional[uuid.UUID] = None
    feature_id: Optional[uuid.UUID] = None
    parent_comment_id: Optional[uuid.UUID] = None
    content: str
    is_ai_generated: bool
    created_at: datetime
    updated_at: datetime
    replies: Optional[List['CommentResponse']] = []
    
    class Config:
        from_attributes = True

