"""AI schemas for request/response"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, UUID4, Field


class AIGenerateRequest(BaseModel):
    """Request to generate AI suggestions"""
    idea_id: UUID4 = Field(..., description="ID of the idea to generate suggestions for")
    suggestion_type: str = Field(..., description="Type of suggestion (features, improvements, marketing, etc.)")
    context: Optional[str] = Field(None, description="Additional context for the AI")


class AIGenerateResponse(BaseModel):
    """Response from AI suggestion generation"""
    suggestion: Dict[str, Any]


class AIQueryLogResponse(BaseModel):
    """Response for AI query logs"""
    logs: List[Dict[str, Any]]
    total: int


class AISuggestionListResponse(BaseModel):
    """Response for listing AI suggestions"""
    suggestions: List[Dict[str, Any]]
    total: int