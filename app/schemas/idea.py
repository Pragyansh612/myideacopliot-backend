"""Idea request/response schemas"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class StatusEnum(str, Enum):
    new = "new"
    in_progress = "in_progress"
    completed = "completed"
    archived = "archived"
    paused = "paused"


class CaptureTypeEnum(str, Enum):
    text = "text"
    voice = "voice"
    clipper = "clipper"
    screenshot = "screenshot"


# Category Schemas
class CategoryCreate(BaseModel):
    name: str = Field(..., max_length=100)
    color: Optional[str] = Field(None, max_length=7)
    description: Optional[str] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    color: Optional[str] = Field(None, max_length=7)
    description: Optional[str] = None


class CategoryResponse(BaseModel):
    id: str
    user_id: str
    name: str
    color: Optional[str]
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Idea Schemas
class IdeaCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    tags: List[str] = []
    category_id: Optional[str] = None
    priority: PriorityEnum = PriorityEnum.medium
    capture_type: CaptureTypeEnum = CaptureTypeEnum.text
    voice_transcription: Optional[str] = None
    effort_score: Optional[int] = Field(None, ge=1, le=10)
    impact_score: Optional[int] = Field(None, ge=1, le=10)
    interest_score: Optional[int] = Field(None, ge=1, le=10)
    reminder_date: Optional[datetime] = None


class IdeaUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    category_id: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    status: Optional[StatusEnum] = None
    effort_score: Optional[int] = Field(None, ge=1, le=10)
    impact_score: Optional[int] = Field(None, ge=1, le=10)
    interest_score: Optional[int] = Field(None, ge=1, le=10)
    is_private: Optional[bool] = None
    is_archived: Optional[bool] = None
    reminder_date: Optional[datetime] = None


class IdeaResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str]
    capture_type: str
    voice_transcription: Optional[str]
    tags: List[str]
    category_id: Optional[str]
    priority: str
    status: str
    effort_score: Optional[int]
    impact_score: Optional[int]
    interest_score: Optional[int]
    overall_score: Optional[float]
    progress_percentage: int
    is_private: bool
    is_archived: bool
    archived_at: Optional[datetime]
    reminder_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    last_accessed_at: datetime
    version: int

    class Config:
        from_attributes = True


class IdeaDetailResponse(IdeaResponse):
    """Idea with nested phases and features"""
    phases: List['PhaseResponse'] = []
    features: List['FeatureResponse'] = []


# Phase Schemas
class PhaseCreate(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    order_index: Optional[int] = None
    due_date: Optional[datetime] = None


class PhaseUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    order_index: Optional[int] = None
    is_completed: Optional[bool] = None
    due_date: Optional[datetime] = None


class PhaseResponse(BaseModel):
    id: str
    idea_id: str
    name: str
    description: Optional[str]
    order_index: int
    is_completed: bool
    completed_at: Optional[datetime]
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Feature Schemas
class FeatureCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    priority: PriorityEnum = PriorityEnum.medium
    order_index: Optional[int] = None


class FeatureUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    priority: Optional[PriorityEnum] = None
    order_index: Optional[int] = None


class FeatureResponse(BaseModel):
    id: str
    idea_id: str
    phase_id: Optional[str]
    title: str
    description: Optional[str]
    is_completed: bool
    completed_at: Optional[datetime]
    priority: str
    order_index: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# List/Filter Schemas
class IdeaListParams(BaseModel):
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)
    category_id: Optional[str] = None
    tag: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    status: Optional[StatusEnum] = None
    sort_by: str = Field("created_at", pattern="^(created_at|updated_at|overall_score|title)$")
    sort_order: str = Field("desc", pattern="^(asc|desc)$")
    search: Optional[str] = None


class PaginatedIdeaResponse(BaseModel):
    ideas: List[IdeaResponse]
    total: int
    limit: int
    offset: int
    has_more: bool


# Forward references
IdeaDetailResponse.model_rebuild()
