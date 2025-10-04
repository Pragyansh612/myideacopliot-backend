"""Idea-related Pydantic schemas"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
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


# ==================== CATEGORIES ====================

class CategoryCreate(BaseModel):
    name: str = Field(..., max_length=100)
    color: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    color: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None


class CategoryResponse(BaseModel):
    id: str
    user_id: str
    name: str
    color: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== IDEAS ====================

class IdeaCreate(BaseModel):
    title: str = Field(..., max_length=200, min_length=1)
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    category_id: Optional[str] = None
    priority: PriorityEnum = PriorityEnum.medium
    status: StatusEnum = StatusEnum.new
    effort_score: Optional[int] = Field(None, ge=1, le=10)
    impact_score: Optional[int] = Field(None, ge=1, le=10)
    interest_score: Optional[int] = Field(None, ge=1, le=10)
    capture_type: str = "text"


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
    is_archived: Optional[bool] = None


class IdeaResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    capture_type: str
    tags: List[str] = []
    category_id: Optional[str] = None
    priority: str
    status: str
    effort_score: Optional[int] = None
    impact_score: Optional[int] = None
    interest_score: Optional[int] = None
    overall_score: Optional[float] = None
    progress_percentage: int = 0
    is_private: bool = True
    is_archived: bool = False
    archived_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== PHASES ====================

class PhaseCreate(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    order_index: int = 0
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
    description: Optional[str] = None
    order_index: int
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== FEATURES ====================

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
    phase_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    priority: str
    order_index: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== PAGINATION ====================

class IdeaListParams(BaseModel):
    limit: int = 50
    offset: int = 0
    category_id: Optional[str] = None
    tag: Optional[str] = None
    priority: Optional[PriorityEnum] = None
    status: Optional[StatusEnum] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"
    search: Optional[str] = None


class PaginatedIdeaResponse(BaseModel):
    ideas: List[IdeaResponse]
    total: int
    limit: int
    offset: int
    has_more: bool

    @classmethod
    def create(cls, ideas: List[IdeaResponse], total: int, limit: int, offset: int):
        return cls(
            ideas=ideas,
            total=total,
            limit=limit,
            offset=offset,
            has_more=(offset + limit) < total
        )


class IdeaDetailResponse(BaseModel):
    idea: IdeaResponse
    phases: List[PhaseResponse] = []
    features: List[FeatureResponse] = []

    class Config:
        from_attributes = True