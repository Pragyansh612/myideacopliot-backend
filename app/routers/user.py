"""User router for profile and settings management - FIXED"""
from typing import List
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.middleware.auth import require_auth
from app.services.user import UserService
from app.schemas.user import (
    UserProfileResponse, 
    UserProfileUpdate, 
    UserSettingResponse, 
    UserSettingCreate, 
    UserSettingUpdate,
    UserStatsResponse
)
from app.schemas.response import SuccessResponse, ErrorResponse
from app.utils.exceptions import AuthenticationError, NotFoundError, ValidationError, ConflictError, InternalServerError
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["User Management"])


# User Profile Endpoints

@router.get("/profile")
async def get_user_profile(request: Request):
    """
    Get current user's profile, creating it if it doesn't exist
    """
    try:
        # This will raise AuthenticationError if no valid user
        user = require_auth(request)
        user_id = user.get("id")
        user_email = user.get("email")
        user_metadata = user.get("user_metadata", {})
        
        # Get access token from request for authenticated operations
        access_token = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            access_token = auth_header.split(" ", 1)[1]
        
        logger.debug(f"Getting profile for user: {user_id} ({user_email})")
        
        # Get or create the user profile
        profile = await UserService.get_user_profile(
            user_id=user_id,
            user_email=user_email,
            user_metadata=user_metadata,
            access_token=access_token
        )
        
        logger.debug(f"Successfully retrieved profile for user: {user_id}")
        
        return SuccessResponse(
            message="Profile retrieved successfully",
            data={"profile": profile.dict()}
        )
        
    except AuthenticationError as e:
        logger.error(f"Auth error in get_profile: {str(e)}")
        raise HTTPException(status_code=401, detail=str(e))
    except InternalServerError as e:
        logger.error(f"Internal server error in get_profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error in get_profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve profile")


@router.put("/profile")
async def update_user_profile(request: Request, profile_data: dict):
    """
    Update current user's profile
    """
    try:
        user = require_auth(request)
        user_id = user.get("id")
        
        logger.debug(f"Updating profile for user: {user_id}")
        
        # Convert dict to UserProfileUpdate schema
        from app.schemas.user import UserProfileUpdate
        update_data = UserProfileUpdate(**profile_data)
        
        profile = await UserService.update_user_profile(user_id, update_data)
        
        return SuccessResponse(
            message="Profile updated successfully",
            data={"profile": profile.dict()}
        )
        
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error in update_profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update profile")


# User Settings Endpoints

@router.get("/settings", response_model=SuccessResponse, summary="Get all user settings")
async def get_settings(request: Request):
    """
    Get all settings for the current user.
    
    Requires authentication.
    """
    try:
        user = require_auth(request)
        user_id = user.get("id")  # FIXED: Changed from user.id to user.get("id")
        
        settings = await UserService.get_user_settings(user_id)
        
        settings_data = [UserSettingResponse(**setting.dict()).dict() for setting in settings]
        
        return SuccessResponse(
            message="Settings retrieved successfully",
            data=settings_data
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Error in get_settings: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(message="Failed to retrieve settings").dict()
        )


@router.get("/settings/{setting_key}", response_model=SuccessResponse, summary="Get specific user setting")
async def get_setting(request: Request, setting_key: str):
    """
    Get a specific setting by key for the current user.
    
    Requires authentication.
    """
    try:
        user = require_auth(request)
        user_id = user.get("id")  # FIXED: Changed from user.id to user.get("id")
        
        setting = await UserService.get_user_setting(user_id, setting_key)
        
        return SuccessResponse(
            message="Setting retrieved successfully",
            data=UserSettingResponse(**setting.dict()).dict()
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error in get_setting: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(message="Failed to retrieve setting").dict()
        )


@router.post("/settings", response_model=SuccessResponse, summary="Create new user setting")
async def create_setting(request: Request, setting_data: UserSettingCreate):
    """
    Create a new setting for the current user.
    
    Requires authentication. Setting key must be unique for the user.
    """
    try:
        user = require_auth(request)
        user_id = user.get("id")  # FIXED: Changed from user.id to user.get("id")
        
        created_setting = await UserService.create_user_setting(user_id, setting_data)
        
        return SuccessResponse(
            message="Setting created successfully",
            data=UserSettingResponse(**created_setting.dict()).dict()
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except (ConflictError, ValidationError) as e:
        return JSONResponse(
            status_code=e.status_code,
            content=ErrorResponse(message=str(e.detail)).dict()
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(message="Failed to create setting").dict()
        )


@router.put("/settings/{setting_key}", response_model=SuccessResponse, summary="Update user setting")
async def update_setting(request: Request, setting_key: str, setting_data: UserSettingUpdate):
    """
    Update an existing setting for the current user.
    
    Requires authentication. Setting must exist.
    """
    try:
        user = require_auth(request)
        user_id = user.get("id")  # FIXED: Changed from user.id to user.get("id")
        
        updated_setting = await UserService.update_user_setting(user_id, setting_key, setting_data)
        
        return SuccessResponse(
            message="Setting updated successfully",
            data=UserSettingResponse(**updated_setting.dict()).dict()
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except NotFoundError as e:
        return JSONResponse(
            status_code=e.status_code,
            content=ErrorResponse(message=str(e.detail)).dict()
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(message="Failed to update setting").dict()
        )


@router.delete("/settings/{setting_key}", response_model=SuccessResponse, summary="Delete user setting")
async def delete_setting(request: Request, setting_key: str):
    """
    Delete a setting for the current user.
    
    Requires authentication.
    """
    try:
        user = require_auth(request)
        user_id = user.get("id")  # FIXED: Changed from user.id to user.get("id")
        
        await UserService.delete_user_setting(user_id, setting_key)
        
        return SuccessResponse(
            message="Setting deleted successfully"
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except NotFoundError as e:
        return JSONResponse(
            status_code=e.status_code,
            content=ErrorResponse(message=str(e.detail)).dict()
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(message="Failed to delete setting").dict()
        )


# User Stats Endpoint

@router.get("/stats")
async def get_user_stats(request: Request):
    """
    Get current user's statistics
    """
    try:
        user = require_auth(request)
        user_id = user.get("id")
        
        stats = await UserService.get_user_stats(user_id)
        
        return SuccessResponse(
            message="Stats retrieved successfully",
            data={"stats": stats.dict()}
        )
        
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Error in get_stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve stats")