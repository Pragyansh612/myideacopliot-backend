"""Competitor research router"""
from typing import List
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.services.competitor import CompetitorService
from app.schemas.competitor import (
    CompetitorScrapeRequest,
    CompetitorScrapeResponse,
    CompetitorListResponse
)
from app.schemas.response import SuccessResponse, ErrorResponse
from app.middleware.auth import require_auth
from app.utils.exceptions import ValidationError

router = APIRouter(prefix="/api/competitor", tags=["Competitor Research"])


@router.post("/scrape", response_model=SuccessResponse, summary="Scrape competitor websites")
async def scrape_competitors(request: Request, data: CompetitorScrapeRequest):
    """
    Scrape and analyze competitor websites.
    
    Extracts:
    - Page title, description, and content
    - Key features and CTAs
    - Visual structure
    
    If analyze=true, provides AI-powered insights:
    - Strengths and weaknesses
    - Differentiation opportunities
    - Market positioning
    """
    try:
        user = require_auth(request)
        
        # Convert HttpUrl objects to strings
        urls = [str(url) for url in data.urls]
        
        research = await CompetitorService.scrape_and_analyze(
            user_id=user["id"],
            idea_id=str(data.idea_id),
            urls=urls,
            analyze=data.analyze
        )
        
        return SuccessResponse(
            message=f"Successfully scraped and analyzed {len(research)} competitor(s)",
            data={
                "research": research,
                "total": len(research)
            }
        )
        
    except ValidationError as e:
        return JSONResponse(
            status_code=e.status_code,
            content=ErrorResponse(message=str(e.detail)).dict()
        )
    except Exception as e:
        print(f"Error scraping competitors: {e}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(message="Failed to scrape competitors").dict()
        )


@router.get("/{idea_id}", response_model=SuccessResponse, summary="Get competitor research")
async def get_competitor_research(request: Request, idea_id: str):
    """
    Get all competitor research for a specific idea.
    """
    try:
        user = require_auth(request)
        
        research = await CompetitorService.get_research(
            user_id=user["id"],
            idea_id=idea_id
        )
        
        return SuccessResponse(
            message="Competitor research retrieved successfully",
            data={
                "research": research,
                "total": len(research)
            }
        )
        
    except ValidationError as e:
        return JSONResponse(
            status_code=e.status_code,
            content=ErrorResponse(message=str(e.detail)).dict()
        )
    except Exception as e:
        print(f"Error getting competitor research: {e}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(message="Failed to retrieve competitor research").dict()
        )
