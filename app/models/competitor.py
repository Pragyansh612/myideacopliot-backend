"""Competitor research models"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, UUID4


class CompetitorResearch(BaseModel):
    """Competitor Research model"""
    id: UUID4
    idea_id: UUID4
    user_id: UUID4
    competitor_name: str
    competitor_url: Optional[str] = None
    description: Optional[str] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    differentiation_opportunities: Optional[List[str]] = None
    market_position: Optional[str] = None
    funding_info: Optional[Dict[str, Any]] = None
    research_date: datetime
    data_sources: Optional[List[str]] = None
    confidence_score: Optional[float] = None
    created_at: datetime