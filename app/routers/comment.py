"""Comment router for threaded discussions"""
from typing import Optional
from fastapi import APIRouter, Request, HTTPException, Query
from app.middleware.auth import require_auth
from app.services.comment import CommentService
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse
from app.schemas.response import SuccessResponse
from app.utils.exceptions import AuthenticationError, NotFoundError, ValidationError, ForbiddenError
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Comments"])


@router.post("/ideas/{idea_id}/comments", status_code=201)
async def create_idea_comment(request: Request, idea_id: str, comment_data: CommentCreate):
    """
    Create a comment on an idea
    
    Args:
        idea_id: ID of the idea
        comment_data: Comment creation data
        
    Returns:
        Created comment
    """
    try:
        user = require_auth(request)
        user_id = uuid.UUID(user.get("id"))
        idea_uuid = uuid.UUID(idea_id)
        
        comment = await CommentService.create_idea_comment(idea_uuid, user_id, comment_data)
        
        return SuccessResponse(
            message="Comment created successfully",
            data={"comment": comment.dict()}
        )
        
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in create_idea_comment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create comment")


@router.post("/features/{feature_id}/comments", status_code=201)
async def create_feature_comment(request: Request, feature_id: str, comment_data: CommentCreate):
    """
    Create a comment on a feature
    
    Args:
        feature_id: ID of the feature
        comment_data: Comment creation data
        
    Returns:
        Created comment
    """
    try:
        user = require_auth(request)
        user_id = uuid.UUID(user.get("id"))
        feature_uuid = uuid.UUID(feature_id)
        
        comment = await CommentService.create_feature_comment(feature_uuid, user_id, comment_data)
        
        return SuccessResponse(
            message="Comment created successfully",
            data={"comment": comment.dict()}
        )
        
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except (NotFoundError, ForbiddenError) as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in create_feature_comment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create comment")


@router.get("/ideas/{idea_id}/comments")
async def get_idea_comments(
    request: Request, 
    idea_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Get all comments for an idea with threading
    
    Args:
        idea_id: ID of the idea
        limit: Maximum number of root comments
        offset: Offset for pagination
        
    Returns:
        List of comments with nested replies
    """
    try:
        user = require_auth(request)
        user_id = uuid.UUID(user.get("id"))
        idea_uuid = uuid.UUID(idea_id)
        
        comments = await CommentService.get_idea_comments(idea_uuid, user_id, limit, offset)
        
        return SuccessResponse(
            message="Comments retrieved successfully",
            data={"comments": [comment.dict() for comment in comments], "total": len(comments)}
        )
        
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error in get_idea_comments: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get comments")


@router.put("/comments/{comment_id}")
async def update_comment(request: Request, comment_id: str, update_data: CommentUpdate):
    """
    Update a comment
    
    Args:
        comment_id: ID of the comment
        update_data: Update data
        
    Returns:
        Updated comment
    """
    try:
        user = require_auth(request)
        user_id = uuid.UUID(user.get("id"))
        comment_uuid = uuid.UUID(comment_id)
        
        comment = await CommentService.update_comment(comment_uuid, user_id, update_data)
        
        return SuccessResponse(
            message="Comment updated successfully",
            data={"comment": comment.dict()}
        )
        
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in update_comment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update comment")


@router.delete("/comments/{comment_id}", status_code=204)
async def delete_comment(request: Request, comment_id: str):
    """
    Soft-delete a comment
    
    Args:
        comment_id: ID of the comment
    """
    try:
        user = require_auth(request)
        user_id = uuid.UUID(user.get("id"))
        comment_uuid = uuid.UUID(comment_id)
        
        await CommentService.delete_comment(comment_uuid, user_id)
        
        return None
        
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error in delete_comment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete comment")
