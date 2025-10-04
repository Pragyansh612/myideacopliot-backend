"""AI models for suggestions and query logs"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, UUID4


class AIQueryLog(BaseModel):
    """AI Query Log model"""
    id: UUID4
    user_id: UUID4
    idea_id: Optional[UUID4] = None
    query_type: str
    user_prompt: str
    ai_response: str
    ai_model: Optional[str] = None
    tokens_used: Optional[int] = None
    response_time_ms: Optional[int] = None
    context_data: Optional[Dict[str, Any]] = None
    created_at: datetime


class AISuggestion(BaseModel):
    """AI Suggestion model"""
    id: UUID4
    idea_id: UUID4
    user_id: UUID4
    suggestion_type: str
    title: Optional[str] = None
    content: str
    confidence_score: Optional[float] = None
    is_applied: bool = False
    applied_at: Optional[datetime] = None
    ai_model: Optional[str] = None
    prompt_used: Optional[str] = None
    created_at: datetime