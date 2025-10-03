"""Ideas router"""
from typing import Optional
from fastapi import APIRouter, Request, HTTPException, Query, status
from app.middleware.auth import require_auth, get_access_token
from app.services.idea import IdeaService
from app.schemas.idea import (
    IdeaCreate, IdeaUpdate, IdeaResponse, IdeaDetailResponse,
    IdeaListParams, PaginatedIdeaResponse, PriorityEnum, StatusEnum
)
from app.schemas.response import SuccessResponse
from app.utils.exceptions import NotFoundError, ForbiddenError, ValidationError
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ideas", tags=["Ideas"])


@router.post("", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def create_idea(request: Request, idea_data: IdeaCreate):
    """Create a new idea"""
    try:
        user = require_auth(request)
        user_id = user.get("id")
        access_token = get_access_token(request)
        
        idea = await IdeaService.create_idea(user_id, idea_data, access_token)
        
        return SuccessResponse(
            message="Idea created successfully",
            data={"idea": idea.dict()}
        )
        
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error in create_idea: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create idea")


@router.get("", response_model=SuccessResponse)
async def get_ideas(
    request: Request,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    category_id: Optional[str] = None,
    tag: Optional[str] = None,
    priority: Optional[PriorityEnum] = None,
    status: Optional[StatusEnum] = None,
    sort_by: str = Query("created_at", regex="^(created_at|updated_at|overall_score|title)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    search: Optional[str] = None
):
    """Get paginated list of ideas with filters"""
    try:
        user = require_auth(request)
        user_id = user.get("id")
        access_token = get_access_token(request)
        
        params = IdeaListParams(
            limit=limit,
            offset=offset,
            category_id=category_id,
            tag=tag,
            priority=priority,
            status=status,
            sort_by=sort_by,
            sort_order=sort_order,
            search=search
        )
        
        result = await IdeaService.get_ideas(user_id, params, access_token)
        
        return SuccessResponse(
            message="Ideas retrieved successfully",
            data=result.dict()
        )
        
    except Exception as e:
        logger.error(f"Error in get_ideas: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve ideas")


@router.get("/{idea_id}", response_model=SuccessResponse)
async def get_idea(request: Request, idea_id: str):
    """Get idea by ID with nested phases and features"""
    try:
        user = require_auth(request)
        user_id = user.get("id")
        access_token = get_access_token(request)
        
        idea = await IdeaService.get_idea_by_id(user_id, idea_id, access_token)
        
        return SuccessResponse(
            message="Idea retrieved successfully",
            data={"idea": idea.dict()}
        )
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error in get_idea: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve idea")


@router.put("/{idea_id}", response_model=SuccessResponse)
async def update_idea(request: Request, idea_id: str, idea_data: IdeaUpdate):
    """Update an idea"""
    try:
        user = require_auth(request)
        user_id = user.get("id")
        access_token = get_access_token(request)
        
        idea = await IdeaService.update_idea(user_id, idea_id, idea_data, access_token)
        
        return SuccessResponse(
            message="Idea updated successfully",
            data={"idea": idea.dict()}
        )
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error in update_idea: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update idea")


@router.delete("/{idea_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_idea(request: Request, idea_id: str):
    """Archive/soft-delete an idea"""
    try:
        user = require_auth(request)
        user_id = user.get("id")
        access_token = get_access_token(request)
        
        await IdeaService.delete_idea(user_id, idea_id, access_token)
        
        return None
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error in delete_idea: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete idea")
