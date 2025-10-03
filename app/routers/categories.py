"""Categories router"""
from typing import List
from fastapi import APIRouter, Request, HTTPException, status
from app.middleware.auth import require_auth, get_access_token
from app.services.idea import IdeaService
from app.schemas.idea import CategoryCreate, CategoryUpdate, CategoryResponse
from app.schemas.response import SuccessResponse
from app.utils.exceptions import NotFoundError, ValidationError, InternalServerError
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/categories", tags=["Categories"])


@router.get("", response_model=SuccessResponse)
async def get_categories(request: Request):
    """Get all categories for the current user"""
    try:
        user = require_auth(request)
        user_id = user.get("id")
        access_token = get_access_token(request)
        
        categories = await IdeaService.get_categories(user_id, access_token)
        
        return SuccessResponse(
            message="Categories retrieved successfully",
            data={"categories": [cat.dict() for cat in categories]}
        )
        
    except Exception as e:
        logger.error(f"Error in get_categories: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve categories")


@router.post("", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def create_category(request: Request, category_data: CategoryCreate):
    """Create a new category"""
    try:
        user = require_auth(request)
        user_id = user.get("id")
        access_token = get_access_token(request)
        
        category = await IdeaService.create_category(user_id, category_data, access_token)
        
        return SuccessResponse(
            message="Category created successfully",
            data={"category": category.dict()}
        )
        
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Error in create_category: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create category")


@router.put("/{category_id}", response_model=SuccessResponse)
async def update_category(request: Request, category_id: str, category_data: CategoryUpdate):
    """Update a category"""
    try:
        user = require_auth(request)
        user_id = user.get("id")
        access_token = get_access_token(request)
        
        category = await IdeaService.update_category(user_id, category_id, category_data, access_token)
        
        return SuccessResponse(
            message="Category updated successfully",
            data={"category": category.dict()}
        )
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error in update_category: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update category")


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(request: Request, category_id: str):
    """Delete a category"""
    try:
        user = require_auth(request)
        user_id = user.get("id")
        access_token = get_access_token(request)
        
        await IdeaService.delete_category(user_id, category_id, access_token)
        
        return None
        
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error in delete_category: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete category")
