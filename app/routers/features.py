"""Features router"""
from typing import List
from fastapi import APIRouter, Request, HTTPException, status
from app.middleware.auth import require_auth, get_access_token
from app.services.idea import IdeaService
from app.schemas.idea import FeatureCreate, FeatureUpdate, FeatureResponse
from app.schemas.response import SuccessResponse
from app.utils.exceptions import NotFoundError, ForbiddenError, ValidationError
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Features"])


@router.post("/ideas/{idea_id}/features", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def create_feature_for_idea(request: Request, idea_id: str, feature_data: FeatureCreate):
    """Create a feature directly under an idea"""
    try:
        user = require_auth(request)
        user_id = user.get("id")
        access_token = get_access_token(request)
        
        feature = await IdeaService.create_feature_for_idea(user_id, idea_id, feature_data, access_token)
        
        return SuccessResponse(
            message="Feature created successfully",
            data={"feature": feature.dict()}
        )
        
    except (NotFoundError, ForbiddenError) as e:
        status_code = 404 if isinstance(e, NotFoundError) else 403
        raise HTTPException(status_code=status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error in create_feature_for_idea: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create feature")


@router.post("/phases/{phase_id}/features", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def create_feature_for_phase(request: Request, phase_id: str, feature_data: FeatureCreate):
    """Create a feature under a phase"""
    try:
        user = require_auth(request)
        user_id = user.get("id")
        access_token = get_access_token(request)
        
        feature = await IdeaService.create_feature_for_phase(user_id, phase_id, feature_data, access_token)
        
        return SuccessResponse(
            message="Feature created successfully",
            data={"feature": feature.dict()}
        )
        
    except (NotFoundError, ForbiddenError) as e:
        status_code = 404 if isinstance(e, NotFoundError) else 403
        raise HTTPException(status_code=status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error in create_feature_for_phase: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create feature")


@router.get("/ideas/{idea_id}/features", response_model=SuccessResponse)
async def get_features(request: Request, idea_id: str):
    """Get all features for an idea"""
    try:
        user = require_auth(request)
        user_id = user.get("id")
        access_token = get_access_token(request)
        
        features = await IdeaService.get_features(user_id, idea_id, access_token)
        
        return SuccessResponse(
            message="Features retrieved successfully",
            data={"features": [feature.dict() for feature in features]}
        )
        
    except (NotFoundError, ForbiddenError) as e:
        status_code = 404 if isinstance(e, NotFoundError) else 403
        raise HTTPException(status_code=status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error in get_features: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve features")


@router.put("/features/{feature_id}", response_model=SuccessResponse)
async def update_feature(request: Request, feature_id: str, feature_data: FeatureUpdate):
    """Update a feature"""
    try:
        user = require_auth(request)
        user_id = user.get("id")
        access_token = get_access_token(request)
        
        feature = await IdeaService.update_feature(user_id, feature_id, feature_data, access_token)
        
        return SuccessResponse(
            message="Feature updated successfully",
            data={"feature": feature.dict()}
        )
        
    except (NotFoundError, ForbiddenError) as e:
        status_code = 404 if isinstance(e, NotFoundError) else 403
        raise HTTPException(status_code=status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error in update_feature: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update feature")


@router.delete("/features/{feature_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feature(request: Request, feature_id: str):
    """Delete a feature"""
    try:
        user = require_auth(request)
        user_id = user.get("id")
        access_token = get_access_token(request)
        
        await IdeaService.delete_feature(user_id, feature_id, access_token)
        
        return None
        
    except (NotFoundError, ForbiddenError) as e:
        status_code = 404 if isinstance(e, NotFoundError) else 403
        raise HTTPException(status_code=status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error in delete_feature: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete feature")
