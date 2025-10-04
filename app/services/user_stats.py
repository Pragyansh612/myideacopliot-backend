"""User stats service"""
from typing import Optional
from uuid import UUID
from datetime import datetime, date
from app.core.database import supabase_client, get_authenticated_client
from app.models.user_stats import UserStats
from app.schemas.user_stats import UserStatsUpdate, StatsIncrement
from app.utils.exceptions import NotFoundError, InternalServerError
from app.services.achievement import AchievementService
import logging

logger = logging.getLogger(__name__)


class UserStatsService:
    """Service for managing user statistics"""
    
    @staticmethod
    def calculate_level(total_xp: int) -> int:
        """Calculate user level based on XP (100 XP per level)"""
        return max(1, total_xp // 100 + 1)
    
    @staticmethod
    async def get_or_create_user_stats(
        user_id: UUID,
        access_token: Optional[str] = None
    ) -> UserStats:
        """Get or create user stats"""
        try:
            client = get_authenticated_client(access_token) if access_token else supabase_client
            
            # Try to get existing stats
            result = client.table("user_stats").select("*").eq(
                "user_id", str(user_id)
            ).execute()
            
            if result.data:
                return UserStats(**result.data[0])
            
            # Create new stats
            now = datetime.utcnow()
            new_stats = client.table("user_stats").insert({
                "user_id": str(user_id),
                "total_xp": 0,
                "current_level": 1,
                "current_streak": 0,
                "longest_streak": 0,
                "last_activity_date": None,
                "ideas_created": 0,
                "ideas_completed": 0,
                "ai_suggestions_applied": 0,
                "collaborations_count": 0,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat()
            }).execute()
            
            if not new_stats.data:
                raise InternalServerError("Failed to create user stats")
            
            return UserStats(**new_stats.data[0])
            
        except Exception as e:
            logger.error(f"Error getting/creating user stats: {e}")
            raise InternalServerError(f"Failed to get user stats: {str(e)}")
    
    @staticmethod
    async def update_user_stats(
        user_id: UUID,
        stats_update: UserStatsUpdate,
        access_token: Optional[str] = None
    ) -> UserStats:
        """Update user stats"""
        try:
            client = get_authenticated_client(access_token) if access_token else supabase_client
            
            # Get current stats
            current_stats = await UserStatsService.get_or_create_user_stats(user_id, access_token)
            
            # Prepare update data
            update_data = {
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if stats_update.total_xp is not None:
                update_data["total_xp"] = stats_update.total_xp
                update_data["current_level"] = UserStatsService.calculate_level(stats_update.total_xp)
            
            if stats_update.current_streak is not None:
                update_data["current_streak"] = stats_update.current_streak
                # Update longest streak if current exceeds it
                if stats_update.current_streak > current_stats.longest_streak:
                    update_data["longest_streak"] = stats_update.current_streak
            
            if stats_update.longest_streak is not None:
                update_data["longest_streak"] = stats_update.longest_streak
            
            if stats_update.last_activity_date is not None:
                update_data["last_activity_date"] = stats_update.last_activity_date.isoformat()
            
            if stats_update.ideas_created is not None:
                update_data["ideas_created"] = stats_update.ideas_created
            
            if stats_update.ideas_completed is not None:
                update_data["ideas_completed"] = stats_update.ideas_completed
            
            if stats_update.ai_suggestions_applied is not None:
                update_data["ai_suggestions_applied"] = stats_update.ai_suggestions_applied
            
            if stats_update.collaborations_count is not None:
                update_data["collaborations_count"] = stats_update.collaborations_count
            
            # Update in database
            result = client.table("user_stats").update(update_data).eq(
                "user_id", str(user_id)
            ).execute()
            
            if not result.data:
                raise InternalServerError("Failed to update user stats")
            
            updated_stats = UserStats(**result.data[0])
            
            # Check for achievements
            await AchievementService.check_and_unlock_achievements(
                user_id,
                updated_stats.dict(),
                access_token
            )
            
            return updated_stats
            
        except Exception as e:
            logger.error(f"Error updating user stats: {e}")
            raise InternalServerError(f"Failed to update user stats: {str(e)}")
    
    @staticmethod
    async def increment_stat(
        user_id: UUID,
        field: str,
        amount: int = 1,
        access_token: Optional[str] = None
    ) -> UserStats:
        """Increment a specific stat field"""
        try:
            # Get current stats
            current_stats = await UserStatsService.get_or_create_user_stats(user_id, access_token)
            
            # Create update with incremented value
            current_value = getattr(current_stats, field, 0)
            update = UserStatsUpdate(**{field: current_value + amount})
            
            # Also update last activity date
            update.last_activity_date = datetime.utcnow().date()
            
            return await UserStatsService.update_user_stats(user_id, update, access_token)
            
        except Exception as e:
            logger.error(f"Error incrementing stat: {e}")
            raise InternalServerError(f"Failed to increment stat: {str(e)}")
    
    @staticmethod
    async def award_xp(
        user_id: UUID,
        xp_amount: int,
        access_token: Optional[str] = None
    ) -> UserStats:
        """Award XP to a user"""
        try:
            current_stats = await UserStatsService.get_or_create_user_stats(user_id, access_token)
            
            new_xp = current_stats.total_xp + xp_amount
            
            update = UserStatsUpdate(
                total_xp=new_xp,
                last_activity_date=datetime.utcnow().date()
            )
            
            return await UserStatsService.update_user_stats(user_id, update, access_token)
            
        except Exception as e:
            logger.error(f"Error awarding XP: {e}")
            raise InternalServerError(f"Failed to award XP: {str(e)}")
    
    @staticmethod
    async def update_streak(
        user_id: UUID,
        access_token: Optional[str] = None
    ) -> UserStats:
        """Update user's activity streak"""
        try:
            current_stats = await UserStatsService.get_or_create_user_stats(user_id, access_token)
            
            today = date.today()
            last_activity = current_stats.last_activity_date
            
            if not last_activity:
                # First activity
                new_streak = 1
            elif last_activity == today:
                # Already updated today
                new_streak = current_stats.current_streak
            elif (today - last_activity).days == 1:
                # Consecutive day
                new_streak = current_stats.current_streak + 1
            else:
                # Streak broken
                new_streak = 1
            
            update = UserStatsUpdate(
                current_streak=new_streak,
                last_activity_date=today
            )
            
            return await UserStatsService.update_user_stats(user_id, update, access_token)
            
        except Exception as e:
            logger.error(f"Error updating streak: {e}")
            raise InternalServerError(f"Failed to update streak: {str(e)}")

