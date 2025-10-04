"""Share router for collaboration endpoints"""
from typing import List
from fastapi import APIRouter, Request, HTTPException
from app.middleware.auth import require_auth
from app.services.share import ShareService
from app.schemas.share import ShareCreate, ShareUpdate, ShareResponse
from app.schemas.response import SuccessResponse
from app.utils.exceptions import AuthenticationError, NotFoundError, ValidationError, ForbiddenError
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ideas", tags=["Collaboration"])


@router.post("/{idea_id}/share", status_code=201)
async def create_share(request: Request, idea_id: str, share_data: ShareCreate):
    """
    Share an idea with another user
    
    Args:
        idea_id: ID of the idea to share
        share_data: Share creation data (email, role)
        
    Returns:
        Created share information
    """
    try:
        user = require_auth(request)
        user_id = uuid.UUID(user.get("id"))
        idea_uuid = uuid.UUID(idea_id)
        
        share = await ShareService.create_share(idea_uuid, user_id, share_data)
        
        return SuccessResponse(
            message="Idea shared successfully",
            data={"share": share.dict()}
        )
        
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except (NotFoundError, ValidationError, ForbiddenError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in create_share: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to share idea")


@router.get("/{idea_id}/shares")
async def get_shares(request: Request, idea_id: str):
    """
    Get all shares for an idea
    
    Args:
        idea_id: ID of the idea
        
    Returns:
        List of shares
    """
    try:
        user = require_auth(request)
        user_id = uuid.UUID(user.get("id"))
        idea_uuid = uuid.UUID(idea_id)
        
        shares = await ShareService.get_idea_shares(idea_uuid, user_id)
        
        return SuccessResponse(
            message="Shares retrieved successfully",
            data={"shares": [share.dict() for share in shares]}
        )
        
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error in get_shares: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get shares")


@router.put("/{idea_id}/share/{share_id}")
async def update_share(request: Request, idea_id: str, share_id: str, update_data: ShareUpdate):
    """
    Update a share (change role or status)
    
    Args:
        idea_id: ID of the idea
        share_id: ID of the share
        update_data: Update data
        
    Returns:
        Updated share
    """
    try:
        user = require_auth(request)
        user_id = uuid.UUID(user.get("id"))
        share_uuid = uuid.UUID(share_id)
        
        share = await ShareService.update_share(share_uuid, user_id, update_data)
        
        return SuccessResponse(
            message="Share updated successfully",
            data={"share": share.dict()}
        )
        
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in update_share: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update share")


@router.delete("/{idea_id}/share/{share_id}", status_code=204)
async def delete_share(request: Request, idea_id: str, share_id: str):
    """
    Revoke a share
    
    Args:
        idea_id: ID of the idea
        share_id: ID of the share
    """
    try:
        user = require_auth(request)
        user_id = uuid.UUID(user.get("id"))
        share_uuid = uuid.UUID(share_id)
        
        await ShareService.delete_share(share_uuid, user_id)
        
        return None
        
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"Error in delete_share: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete share")