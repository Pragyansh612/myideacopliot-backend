"""Achievement service"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from app.core.database import supabase_client, get_authenticated_client
from app.models.achievement import Achievement
from app.schemas.achievement import AchievementCreate, AchievementDefinition
from app.utils.exceptions import NotFoundError, InternalServerError
import logging

logger = logging.getLogger(__name__)


class AchievementService:
    """Service for managing achievements"""
    
    # Achievement definitions
    ACHIEVEMENT_DEFINITIONS = [
        {
            "achievement_type": "first_idea",
            "title": "Idea Spark",
            "description": "Created your first idea",
            "icon": "💡",
            "xp_awarded": 10,
            "unlock_condition": "Create 1 idea"
        },
        {
            "achievement_type": "idea_master_10",
            "title": "Idea Master",
            "description": "Created 10 ideas",
            "icon": "🌟",
            "xp_awarded": 50,
            "unlock_condition": "Create 10 ideas"
        },
        {
            "achievement_type": "first_completion",
            "title": "Finisher",
            "description": "Completed your first idea",
            "icon": "✅",
            "xp_awarded": 25,
            "unlock_condition": "Complete 1 idea"
        },
        {
            "achievement_type": "week_streak",
            "title": "Consistent Creator",
            "description": "Maintained a 7-day streak",
            "icon": "🔥",
            "xp_awarded": 30,
            "unlock_condition": "7-day activity streak"
        },
        {
            "achievement_type": "collaborator",
            "title": "Team Player",
            "description": "Shared an idea with someone",
            "icon": "🤝",
            "xp_awarded": 15,
            "unlock_condition": "Share 1 idea"
        },
        {
            "achievement_type": "ai_adopter",
            "title": "AI Enthusiast",
            "description": "Applied 5 AI suggestions",
            "icon": "🤖",
            "xp_awarded": 20,
            "unlock_condition": "Apply 5 AI suggestions"
        }
    ]
    
    @staticmethod
    async def unlock_achievement(
        user_id: UUID,
        achievement_data: AchievementCreate,
        access_token: Optional[str] = None
    ) -> Achievement:
        """Unlock an achievement for a user"""
        try:
            client = get_authenticated_client(access_token) if access_token else supabase_client
            
            # Check if already unlocked
            existing = client.table("achievements").select("*").eq(
                "user_id", str(user_id)
            ).eq(
                "achievement_type", achievement_data.achievement_type
            ).execute()
            
            if existing.data:
                logger.info(f"Achievement {achievement_data.achievement_type} already unlocked for user {user_id}")
                return Achievement(**existing.data[0])
            
            # Create achievement
            result = client.table("achievements").insert({
                "user_id": str(user_id),
                "achievement_type": achievement_data.achievement_type,
                "title": achievement_data.title,
                "description": achievement_data.description,
                "icon": achievement_data.icon,
                "xp_awarded": achievement_data.xp_awarded,
                "unlocked_at": datetime.utcnow().isoformat(),
                "related_idea_id": str(achievement_data.related_idea_id) if achievement_data.related_idea_id else None
            }).execute()
            
            if not result.data:
                raise InternalServerError("Failed to unlock achievement")
            
            logger.info(f"Unlocked achievement {achievement_data.achievement_type} for user {user_id}")
            return Achievement(**result.data[0])
            
        except Exception as e:
            logger.error(f"Error unlocking achievement: {e}")
            raise InternalServerError(f"Failed to unlock achievement: {str(e)}")
    
    @staticmethod
    async def get_user_achievements(
        user_id: UUID,
        access_token: Optional[str] = None
    ) -> List[Achievement]:
        """Get all achievements for a user"""
        try:
            client = get_authenticated_client(access_token) if access_token else supabase_client
            
            result = client.table("achievements").select("*").eq(
                "user_id", str(user_id)
            ).order("unlocked_at", desc=True).execute()
            
            return [Achievement(**item) for item in result.data]
            
        except Exception as e:
            logger.error(f"Error fetching achievements: {e}")
            raise InternalServerError(f"Failed to fetch achievements: {str(e)}")
    
    @staticmethod
    async def get_all_achievement_definitions() -> List[AchievementDefinition]:
        """Get all possible achievement definitions"""
        return [AchievementDefinition(**achievement) for achievement in AchievementService.ACHIEVEMENT_DEFINITIONS]
    
    @staticmethod
    async def check_and_unlock_achievements(
        user_id: UUID,
        stats: dict,
        access_token: Optional[str] = None
    ):
        """Check user stats and unlock relevant achievements"""
        try:
            unlocked = []
            
            # First idea
            if stats.get("ideas_created") == 1:
                achievement = await AchievementService.unlock_achievement(
                    user_id,
                    AchievementCreate(
                        achievement_type="first_idea",
                        title="Idea Spark",
                        description="Created your first idea",
                        icon="💡",
                        xp_awarded=10
                    ),
                    access_token
                )
                unlocked.append(achievement)
            
            # 10 ideas
            if stats.get("ideas_created") == 10:
                achievement = await AchievementService.unlock_achievement(
                    user_id,
                    AchievementCreate(
                        achievement_type="idea_master_10",
                        title="Idea Master",
                        description="Created 10 ideas",
                        icon="🌟",
                        xp_awarded=50
                    ),
                    access_token
                )
                unlocked.append(achievement)
            
            # First completion
            if stats.get("ideas_completed") == 1:
                achievement = await AchievementService.unlock_achievement(
                    user_id,
                    AchievementCreate(
                        achievement_type="first_completion",
                        title="Finisher",
                        description="Completed your first idea",
                        icon="✅",
                        xp_awarded=25
                    ),
                    access_token
                )
                unlocked.append(achievement)
            
            # Week streak
            if stats.get("current_streak") == 7:
                achievement = await AchievementService.unlock_achievement(
                    user_id,
                    AchievementCreate(
                        achievement_type="week_streak",
                        title="Consistent Creator",
                        description="Maintained a 7-day streak",
                        icon="🔥",
                        xp_awarded=30
                    ),
                    access_token
                )
                unlocked.append(achievement)
            
            # Collaborator
            if stats.get("collaborations_count") == 1:
                achievement = await AchievementService.unlock_achievement(
                    user_id,
                    AchievementCreate(
                        achievement_type="collaborator",
                        title="Team Player",
                        description="Shared an idea with someone",
                        icon="🤝",
                        xp_awarded=15
                    ),
                    access_token
                )
                unlocked.append(achievement)
            
            # AI adopter
            if stats.get("ai_suggestions_applied") == 5:
                achievement = await AchievementService.unlock_achievement(
                    user_id,
                    AchievementCreate(
                        achievement_type="ai_adopter",
                        title="AI Enthusiast",
                        description="Applied 5 AI suggestions",
                        icon="🤖",
                        xp_awarded=20
                    ),
                    access_token
                )
                unlocked.append(achievement)
            
            return unlocked
            
        except Exception as e:
            logger.error(f"Error checking achievements: {e}")
            return []
