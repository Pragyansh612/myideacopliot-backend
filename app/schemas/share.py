"""Share schemas for request/response"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
import uuid


class ShareRole:
    """Available share roles"""
    VIEWER = "viewer"
    EDITOR = "editor"


class ShareCreate(BaseModel):
    """Schema for creating a share"""
    shared_with_email: str = Field(..., description="Email of user to share with")
    role: str = Field(default=ShareRole.VIEWER, description="Role: viewer or editor")
    expires_at: Optional[datetime] = Field(None, description="Optional expiration date")
    
    @validator('role')
    def validate_role(cls, v):
        if v not in [ShareRole.VIEWER, ShareRole.EDITOR]:
            raise ValueError(f"Role must be '{ShareRole.VIEWER}' or '{ShareRole.EDITOR}'")
        return v


class ShareUpdate(BaseModel):
    """Schema for updating a share"""
    role: Optional[str] = None
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None
    
    @validator('role')
    def validate_role(cls, v):
        if v is not None and v not in [ShareRole.VIEWER, ShareRole.EDITOR]:
            raise ValueError(f"Role must be '{ShareRole.VIEWER}' or '{ShareRole.EDITOR}'")
        return v


class ShareResponse(BaseModel):
    """Schema for share response"""
    id: uuid.UUID
    idea_id: uuid.UUID
    owner_id: uuid.UUID
    shared_with_id: uuid.UUID
    shared_with_email: Optional[str] = None
    role: str
    permissions: Optional[dict] = None
    shared_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool
    
    class Config:
        from_attributes = True
