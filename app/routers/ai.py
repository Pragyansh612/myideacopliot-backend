"""AI assistance router"""
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.services.ai import AIService
from app.schemas.ai import (
    AIGenerateRequest,
    AIGenerateResponse,
    AIQueryLogResponse,
    AISuggestionListResponse
)
from app.schemas.response import SuccessResponse, ErrorResponse
from app.middleware.auth import require_auth
from app.utils.exceptions import ValidationError

router = APIRouter(prefix="/api/ai", tags=["AI Assistance"])


@router.post("/suggest", response_model=SuccessResponse, summary="Generate AI suggestions")
async def generate_suggestions(request: Request, data: AIGenerateRequest):
    """
    Generate AI-powered suggestions for an idea using Gemini.
    
    Suggestion types:
    - features: Suggest innovative features
    - improvements: Suggest improvements to existing idea
    - marketing: Generate marketing strategy
    - validation: Validate market viability
    """
    try:
        user = require_auth(request)
        
        suggestion = await AIService.generate_suggestions(
            user_id=user["id"],
            idea_id=str(data.idea_id),
            suggestion_type=data.suggestion_type,
            context=data.context
        )
        
        return SuccessResponse(
            message=f"{data.suggestion_type.title()} suggestions generated successfully",
            data={"suggestion": suggestion}
        )
        
    except ValidationError as e:
        return JSONResponse(
            status_code=e.status_code,
            content=ErrorResponse(message=str(e.detail)).dict()
        )
    except Exception as e:
        print(f"Error generating suggestions: {e}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(message="Failed to generate suggestions").dict()
        )


@router.get("/suggestions/{idea_id}", response_model=SuccessResponse, summary="List AI suggestions")
async def get_suggestions(request: Request, idea_id: str):
    """
    Get all AI suggestions for a specific idea.
    """
    try:
        user = require_auth(request)
        
        suggestions = await AIService.get_suggestions(
            user_id=user["id"],
            idea_id=idea_id
        )
        
        return SuccessResponse(
            message="Suggestions retrieved successfully",
            data={
                "suggestions": suggestions,
                "total": len(suggestions)
            }
        )
        
    except ValidationError as e:
        return JSONResponse(
            status_code=e.status_code,
            content=ErrorResponse(message=str(e.detail)).dict()
        )
    except Exception as e:
        print(f"Error getting suggestions: {e}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(message="Failed to retrieve suggestions").dict()
        )


@router.get("/logs", response_model=SuccessResponse, summary="List AI query logs")
async def get_query_logs(request: Request, limit: int = 50):
    """
    Get AI query logs for the current user.
    Shows history of all AI interactions.
    """
    try:
        user = require_auth(request)
        
        logs = await AIService.get_query_logs(
            user_id=user["id"],
            limit=limit
        )
        
        return SuccessResponse(
            message="Query logs retrieved successfully",
            data={
                "logs": logs,
                "total": len(logs)
            }
        )
        
    except Exception as e:
        print(f"Error getting query logs: {e}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(message="Failed to retrieve query logs").dict()
        )
