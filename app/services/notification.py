"""Notification service"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from app.core.database import supabase_client, get_authenticated_client
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate, NotificationUpdate
from app.utils.exceptions import NotFoundError, InternalServerError
from app.utils.email import send_email
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for managing notifications"""
    
    @staticmethod
    async def create_notification(
        user_id: UUID,
        notification_data: NotificationCreate,
        access_token: Optional[str] = None
    ) -> Notification:
        """Create a new notification"""
        try:
            client = get_authenticated_client(access_token) if access_token else supabase_client
            
            result = client.table("notifications").insert({
                "user_id": str(user_id),
                "type": notification_data.type,
                "title": notification_data.title,
                "message": notification_data.message,
                "related_idea_id": str(notification_data.related_idea_id) if notification_data.related_idea_id else None,
                "related_entity_type": notification_data.related_entity_type,
                "related_entity_id": str(notification_data.related_entity_id) if notification_data.related_entity_id else None,
                "action_url": notification_data.action_url,
                "priority": notification_data.priority,
                "expires_at": notification_data.expires_at.isoformat() if notification_data.expires_at else None,
                "is_read": False,
                "created_at": datetime.utcnow().isoformat()
            }).execute()
            
            if not result.data:
                raise InternalServerError("Failed to create notification")
            
            logger.info(f"Created notification for user {user_id}: {notification_data.title}")
            return Notification(**result.data[0])
            
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            raise InternalServerError(f"Failed to create notification: {str(e)}")
    
    @staticmethod
    async def get_user_notifications(
        user_id: UUID,
        unread_only: bool = False,
        access_token: Optional[str] = None
    ) -> List[Notification]:
        """Get notifications for a user"""
        try:
            client = get_authenticated_client(access_token) if access_token else supabase_client
            
            query = client.table("notifications").select("*").eq("user_id", str(user_id))
            
            if unread_only:
                query = query.eq("is_read", False)
            
            result = query.order("created_at", desc=True).execute()
            
            return [Notification(**item) for item in result.data]
            
        except Exception as e:
            logger.error(f"Error fetching notifications: {e}")
            raise InternalServerError(f"Failed to fetch notifications: {str(e)}")
    
    @staticmethod
    async def mark_notification_read(
        notification_id: UUID,
        user_id: UUID,
        access_token: Optional[str] = None
    ) -> Notification:
        """Mark a notification as read"""
        try:
            client = get_authenticated_client(access_token) if access_token else supabase_client
            
            result = client.table("notifications").update({
                "is_read": True,
                "read_at": datetime.utcnow().isoformat()
            }).eq("id", str(notification_id)).eq("user_id", str(user_id)).execute()
            
            if not result.data:
                raise NotFoundError("Notification not found")
            
            return Notification(**result.data[0])
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            raise InternalServerError(f"Failed to mark notification as read: {str(e)}")
    
    @staticmethod
    async def delete_notification(
        notification_id: UUID,
        user_id: UUID,
        access_token: Optional[str] = None
    ):
        """Delete a notification"""
        try:
            client = get_authenticated_client(access_token) if access_token else supabase_client
            
            result = client.table("notifications").delete().eq(
                "id", str(notification_id)
            ).eq("user_id", str(user_id)).execute()
            
            if not result.data:
                raise NotFoundError("Notification not found")
            
            logger.info(f"Deleted notification {notification_id}")
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error deleting notification: {e}")
            raise InternalServerError(f"Failed to delete notification: {str(e)}")
    
    @staticmethod
    async def send_motivational_notification(
        user_id: UUID,
        user_email: str,
        message_type: str = "encouragement",
        access_token: Optional[str] = None
    ) -> Notification:
        """Send a motivational notification"""
        try:
            messages = {
                "encouragement": {
                    "title": "Keep Going! 💪",
                    "message": "You're doing great! Your ideas are valuable. Keep building and creating!"
                },
                "reminder": {
                    "title": "We Miss You! 👋",
                    "message": "It's been a while since your last idea. Got something new brewing? Come share it!"
                },
                "streak": {
                    "title": "Maintain Your Streak! 🔥",
                    "message": "You're on a roll! Don't break your streak. Add an update to your ideas today!"
                }
            }
            
            message_data = messages.get(message_type, messages["encouragement"])
            
            # Create notification
            notification = await NotificationService.create_notification(
                user_id,
                NotificationCreate(
                    type="motivation",
                    title=message_data["title"],
                    message=message_data["message"],
                    priority="normal"
                ),
                access_token
            )
            
            # Send email
            await send_email(
                to=user_email,
                subject=message_data["title"],
                body=message_data["message"]
            )
            
            return notification
            
        except Exception as e:
            logger.error(f"Error sending motivational notification: {e}")
            raise InternalServerError(f"Failed to send motivational notification: {str(e)}")
    
    @staticmethod
    async def check_inactive_users():
        """Check for inactive users and send reminders (background task)"""
        try:
            from datetime import date, timedelta
            
            # Get users inactive for 7+ days
            seven_days_ago = (date.today() - timedelta(days=7)).isoformat()
            
            result = supabase_client.table("user_stats").select(
                "user_id, last_activity_date"
            ).lt("last_activity_date", seven_days_ago).execute()
            
            inactive_users = result.data
            
            for user_stat in inactive_users:
                user_id = user_stat["user_id"]
                
                # Get user email from profiles
                profile_result = supabase_client.table("profiles").select(
                    "email"
                ).eq("id", user_id).execute()
                
                if profile_result.data:
                    user_email = profile_result.data[0]["email"]
                    
                    # Send reminder
                    await NotificationService.send_motivational_notification(
                        UUID(user_id),
                        user_email,
                        "reminder"
                    )
                    
                    logger.info(f"Sent inactivity reminder to user {user_id}")
            
            return len(inactive_users)
            
        except Exception as e:
            logger.error(f"Error checking inactive users: {e}")
            return 0

