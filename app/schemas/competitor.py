"""Competitor research schemas"""
from typing import Optional, List
from pydantic import BaseModel, UUID4, Field, HttpUrl


class CompetitorScrapeRequest(BaseModel):
    """Request to scrape competitor website"""
    idea_id: UUID4 = Field(..., description="ID of the idea to associate research with")
    urls: List[HttpUrl] = Field(..., description="List of competitor URLs to scrape")
    analyze: bool = Field(True, description="Whether to analyze and summarize the data")


class CompetitorScrapeResponse(BaseModel):
    """Response from competitor scraping"""
    research: List[dict]
    total: int


class CompetitorListResponse(BaseModel):
    """Response for listing competitor research"""
    research: List[dict]
    total: int
