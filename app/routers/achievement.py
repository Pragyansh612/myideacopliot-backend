"""Achievement router"""
from typing import List
from fastapi import APIRouter, Request, HTTPException
from app.middleware.auth import require_auth
from app.services.achievement import AchievementService
from app.schemas.achievement import AchievementResponse, AchievementDefinition
from app.schemas.response import SuccessResponse, ErrorResponse
from app.utils.exceptions import AuthenticationError, InternalServerError
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/achievements", tags=["Achievements"])


@router.get("", response_model=SuccessResponse, summary="Get user's achievements")
async def get_achievements(request: Request):
    """
    Get all achievements unlocked by the current user
    
    Requires authentication.
    """
    try:
        user = require_auth(request)
        user_id = user.get("id")
        
        # Get access token
        access_token = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            access_token = auth_header.split(" ", 1)[1]
        
        achievements = await AchievementService.get_user_achievements(user_id, access_token)
        
        return SuccessResponse(
            message="Achievements retrieved successfully",
            data={
                "achievements": [AchievementResponse(**achievement.dict()).dict() for achievement in achievements],
                "total": len(achievements)
            }
        )
        
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting achievements: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve achievements")


@router.get("/all", response_model=SuccessResponse, summary="Get all possible achievements")
async def get_all_achievements():
    """
    Get all possible achievements (achievement definitions)
    
    Does not require authentication - shows what achievements are available.
    """
    try:
        definitions = await AchievementService.get_all_achievement_definitions()
        
        return SuccessResponse(
            message="Achievement definitions retrieved successfully",
            data={
                "achievements": [definition.dict() for definition in definitions],
                "total": len(definitions)
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting achievement definitions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve achievement definitions")
