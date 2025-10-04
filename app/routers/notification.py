"""Notification router"""
from typing import List, Optional
from fastapi import APIRouter, Request, HTTPException, Query
from app.middleware.auth import require_auth
from app.services.notification import NotificationService
from app.schemas.notification import NotificationResponse, MotivationRequest
from app.schemas.response import SuccessResponse, ErrorResponse
from app.utils.exceptions import AuthenticationError, NotFoundError, InternalServerError
from uuid import UUID
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.get("", response_model=SuccessResponse, summary="Get user notifications")
async def get_notifications(
    request: Request,
    unread_only: bool = Query(False, description="Show only unread notifications")
):
    """
    Get all notifications for the current user
    
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
        
        notifications = await NotificationService.get_user_notifications(
            user_id,
            unread_only=unread_only,
            access_token=access_token
        )
        
        return SuccessResponse(
            message="Notifications retrieved successfully",
            data={
                "notifications": [NotificationResponse(**notif.dict()).dict() for notif in notifications],
                "total": len(notifications),
                "unread_count": sum(1 for n in notifications if not n.is_read)
            }
        )
        
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve notifications")


@router.put("/{notification_id}/read", response_model=SuccessResponse, summary="Mark notification as read")
async def mark_notification_read(request: Request, notification_id: UUID):
    """
    Mark a specific notification as read
    
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
        
        notification = await NotificationService.mark_notification_read(
            notification_id,
            user_id,
            access_token
        )
        
        return SuccessResponse(
            message="Notification marked as read",
            data={"notification": NotificationResponse(**notification.dict()).dict()}
        )
        
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error marking notification as read: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark notification as read")


@router.delete("/{notification_id}", status_code=204, summary="Delete notification")
async def delete_notification(request: Request, notification_id: UUID):
    """
    Delete a notification
    
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
        
        await NotificationService.delete_notification(
            notification_id,
            user_id,
            access_token
        )
        
        return None
        
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete notification")


@router.post("/motivation", response_model=SuccessResponse, summary="Send motivational notification")
async def send_motivation(request: Request, motivation_request: MotivationRequest):
    """
    Send a motivational notification to the current user
    
    Requires authentication.
    """
    try:
        user = require_auth(request)
        user_id = user.get("id")
        user_email = user.get("email")
        
        # Get access token
        access_token = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            access_token = auth_header.split(" ", 1)[1]
        
        notification = await NotificationService.send_motivational_notification(
            user_id,
            user_email,
            motivation_request.message_type,
            access_token
        )
        
        return SuccessResponse(
            message="Motivational notification sent successfully",
            data={"notification": NotificationResponse(**notification.dict()).dict()}
        )
        
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Error sending motivational notification: {e}")
        raise HTTPException(status_code=500, detail="Failed to send motivational notification")

