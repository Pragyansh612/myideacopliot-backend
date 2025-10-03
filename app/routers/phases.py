"""Phases router"""
from typing import List
from fastapi import APIRouter, Request, HTTPException, status
from app.middleware.auth import require_auth, get_access_token
from app.services.idea import IdeaService
from app.schemas.idea import PhaseCreate, PhaseUpdate, PhaseResponse
from app.schemas.response import SuccessResponse
from app.utils.exceptions import NotFoundError, ForbiddenError, ValidationError
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Phases"])


@router.post("/ideas/{idea_id}/phases", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def create_phase(request: Request, idea_id: str, phase_data: PhaseCreate):
    """Create a phase for an idea"""
    try:
        user = require_auth(request)
        user_id = user.get("id")
        access_token = get_access_token(request)
        
        phase = await IdeaService.create_phase(user_id, idea_id, phase_data, access_token)
        
        return SuccessResponse(
            message="Phase created successfully",
            data={"phase": phase.dict()}
        )
        
    except (NotFoundError, ForbiddenError) as e:
        status_code = 404 if isinstance(e, NotFoundError) else 403
        raise HTTPException(status_code=status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error in create_phase: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create phase")


@router.get("/ideas/{idea_id}/phases", response_model=SuccessResponse)
async def get_phases(request: Request, idea_id: str):
    """Get all phases for an idea"""
    try:
        user = require_auth(request)
        user_id = user.get("id")
        access_token = get_access_token(request)
        
        phases = await IdeaService.get_phases(user_id, idea_id, access_token)
        
        return SuccessResponse(
            message="Phases retrieved successfully",
            data={"phases": [phase.dict() for phase in phases]}
        )
        
    except (NotFoundError, ForbiddenError) as e:
        status_code = 404 if isinstance(e, NotFoundError) else 403
        raise HTTPException(status_code=status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error in get_phases: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve phases")


@router.put("/phases/{phase_id}", response_model=SuccessResponse)
async def update_phase(request: Request, phase_id: str, phase_data: PhaseUpdate):
    """Update a phase"""
    try:
        user = require_auth(request)
        user_id = user.get("id")
        access_token = get_access_token(request)
        
        phase = await IdeaService.update_phase(user_id, phase_id, phase_data, access_token)
        
        return SuccessResponse(
            message="Phase updated successfully",
            data={"phase": phase.dict()}
        )
        
    except (NotFoundError, ForbiddenError) as e:
        status_code = 404 if isinstance(e, NotFoundError) else 403
        raise HTTPException(status_code=status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error in update_phase: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update phase")


@router.delete("/phases/{phase_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_phase(request: Request, phase_id: str):
    """Delete a phase"""
    try:
        user = require_auth(request)
        user_id = user.get("id")
        access_token = get_access_token(request)
        
        await IdeaService.delete_phase(user_id, phase_id, access_token)
        
        return None
        
    except (NotFoundError, ForbiddenError) as e:
        status_code = 404 if isinstance(e, NotFoundError) else 403
        raise HTTPException(status_code=status_code, detail=str(e))
    except Exception as e:
        logger.error(f"Error in delete_phase: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete phase")


