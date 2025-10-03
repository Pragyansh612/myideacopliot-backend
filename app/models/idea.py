"""Idea domain models"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class IdeaModel(BaseModel):
    """Idea domain model"""
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    capture_type: str = "text"
    voice_transcription: Optional[str] = None
    tags: List[str] = []
    category_id: Optional[str] = None
    priority: str = "medium"
    status: str = "new"
    effort_score: Optional[int] = None
    impact_score: Optional[int] = None
    interest_score: Optional[int] = None
    overall_score: Optional[float] = None
    progress_percentage: int = 0
    is_private: bool = True
    is_archived: bool = False
    archived_at: Optional[datetime] = None
    reminder_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    last_accessed_at: datetime
    version: int = 1


class CategoryModel(BaseModel):
    """Category domain model"""
    id: str
    user_id: str
    name: str
    color: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime


class PhaseModel(BaseModel):
    """Phase domain model"""
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


class FeatureModel(BaseModel):
    """Feature domain model"""
    id: str
    idea_id: str
    phase_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    priority: str = "medium"
    order_index: Optional[int] = None
    created_at: datetime
    updated_at: datetime
