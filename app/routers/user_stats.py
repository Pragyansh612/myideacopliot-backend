"""User stats router"""
from fastapi import APIRouter, Request, HTTPException
from app.middleware.auth import require_auth
from app.services.user_stats import UserStatsService
from app.schemas.user_stats import UserStatsResponse, UserStatsUpdate, StatsIncrement
from app.schemas.response import SuccessResponse, ErrorResponse
from app.utils.exceptions import AuthenticationError, InternalServerError
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/stats", tags=["User Statistics"])


@router.get("", response_model=SuccessResponse, summary="Get user statistics")
async def get_stats(request: Request):
    """
    Get statistics for the current user
    
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
        
        stats = await UserStatsService.get_or_create_user_stats(user_id, access_token)
        
        return SuccessResponse(
            message="Stats retrieved successfully",
            data={"stats": UserStatsResponse(**stats.dict()).dict()}
        )
        
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve stats")


@router.post("/update", response_model=SuccessResponse, summary="Update user statistics")
async def update_stats(request: Request, stats_update: UserStatsUpdate):
    """
    Update user statistics
    
    Requires authentication. Used internally by other services.
    """
    try:
        user = require_auth(request)
        user_id = user.get("id")
        
        # Get access token
        access_token = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            access_token = auth_header.split(" ", 1)[1]
        
        stats = await UserStatsService.update_user_stats(user_id, stats_update, access_token)
        
        return SuccessResponse(
            message="Stats updated successfully",
            data={"stats": UserStatsResponse(**stats.dict()).dict()}
        )
        
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to update stats")


@router.post("/increment", response_model=SuccessResponse, summary="Increment specific stat")
async def increment_stat(request: Request, increment_data: StatsIncrement):
    """
    Increment a specific stat field
    
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
        
        stats = await UserStatsService.increment_stat(
            user_id,
            increment_data.field,
            increment_data.amount,
            access_token
        )
        
        return SuccessResponse(
            message=f"Stat '{increment_data.field}' incremented successfully",
            data={"stats": UserStatsResponse(**stats.dict()).dict()}
        )
        
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Error incrementing stat: {e}")
        raise HTTPException(status_code=500, detail="Failed to increment stat")


@router.post("/award-xp", response_model=SuccessResponse, summary="Award XP to user")
async def award_xp(request: Request, xp_amount: int):
    """
    Award XP to the current user
    
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
        
        stats = await UserStatsService.award_xp(user_id, xp_amount, access_token)
        
        return SuccessResponse(
            message=f"Awarded {xp_amount} XP",
            data={"stats": UserStatsResponse(**stats.dict()).dict()}
        )
        
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Error awarding XP: {e}")
        raise HTTPException(status_code=500, detail="Failed to award XP")

