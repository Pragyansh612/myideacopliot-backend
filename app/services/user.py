"""User service for profile and settings management - With proper authentication"""
from typing import Dict, Any, List, Optional
from app.core.database import supabase_client, supabase_admin, get_authenticated_client
from app.models.user import UserProfile, UserSetting, UserStats
from app.schemas.user import UserProfileUpdate, UserSettingCreate, UserSettingUpdate
from app.utils.exceptions import NotFoundError, ValidationError, ConflictError, InternalServerError
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Service for managing user profiles and settings"""

    @staticmethod
    async def get_user_profile(
        user_id: str,
        user_email: str = None,
        user_metadata: dict = None,
        access_token: str = None
    ) -> UserProfile:
        """
        Get user profile by user ID, creating it if it doesn't exist

        Args:
            user_id: User's ID
            user_email: User's email (for profile creation fallback)
            user_metadata: User metadata (for profile creation fallback)
            access_token: JWT access token for authenticated operations

        Returns:
            User profile data

        Raises:
            InternalServerError: If profile cannot be retrieved or created
        """
        try:
            # Use authenticated client if token is provided
            client = get_authenticated_client(access_token) if access_token else supabase_client

            # Try to get existing profile
            response = client.table("user_profiles").select("*").eq("id", user_id).execute()

            if response.data and len(response.data) > 0:
                logger.debug(f"Found existing profile for user {user_id}")
                return UserProfile(**response.data[0])

            # Profile doesn't exist, try to create it
            logger.info(f"Profile not found for user {user_id}, attempting to create...")

            # Extract display name from metadata or use email
            display_name = "User"
            if user_metadata and isinstance(user_metadata, dict):
                display_name = user_metadata.get("display_name") or user_metadata.get("email", "User")
            elif user_email:
                display_name = user_email

            # Create profile using admin client (bypasses RLS for initial creation)
            profile_data = {
                "id": user_id,
                "display_name": display_name
            }

            try:
                profile_response = supabase_admin.table("user_profiles").insert(profile_data).execute()

                if not profile_response.data:
                    raise InternalServerError("Failed to create user profile")

                # Create user stats as well using admin client
                try:
                    stats_data = {"user_id": user_id}
                    supabase_admin.table("user_stats").insert(stats_data).execute()
                    logger.info(f"Created user stats for {user_id}")
                except Exception as e:
                    logger.warning(f"Failed to create user stats for {user_id}: {e}")

                logger.info(f"Successfully created profile for user {user_id}")
                return UserProfile(**profile_response.data[0])

            except Exception as create_error:
                # Check if it's a duplicate key error (race condition with trigger)
                error_str = str(create_error).lower()
                if "duplicate key" in error_str or "already exists" in error_str or "23505" in error_str:
                    logger.info(
                        f"Profile creation failed due to race condition for user {user_id}, retrying fetch..."
                    )

                    # The trigger likely created the profile, so try to fetch it again
                    retry_response = client.table("user_profiles").select("*").eq("id", user_id).execute()

                    if retry_response.data and len(retry_response.data) > 0:
                        logger.info(f"Successfully retrieved profile created by trigger for user {user_id}")
                        return UserProfile(**retry_response.data[0])
                    else:
                        # Still not found - this is a real problem
                        logger.error(f"Profile still not found after duplicate key error for user {user_id}")
                        raise InternalServerError(
                            "Failed to retrieve user profile after creation conflict"
                        )
                else:
                    # Different error, re-raise
                    raise InternalServerError(f"Failed to create user profile: {str(create_error)}")

        except InternalServerError:
            # Re-raise our custom errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error in get_user_profile for {user_id}: {str(e)}")
            raise InternalServerError(f"Failed to retrieve user profile: {str(e)}")
    
    @staticmethod
    async def update_user_profile(user_id: str, profile_data: UserProfileUpdate, access_token: str = None) -> UserProfile:
        """
        Update user profile
        
        Args:
            user_id: User's ID
            profile_data: Profile update data
            access_token: JWT access token for authenticated operations
            
        Returns:
            Updated user profile
            
        Raises:
            NotFoundError: If profile not found
            ConflictError: If username already exists
            ValidationError: If validation fails
        """
        try:
            # Use authenticated client if token is provided
            client = get_authenticated_client(access_token) if access_token else supabase_client
            
            # Check if username is being updated and if it already exists
            update_dict = profile_data.dict(exclude_unset=True)
            
            if "username" in update_dict and update_dict["username"]:
                existing_user = client.table("user_profiles").select("id").eq("username", update_dict["username"]).neq("id", user_id).execute()
                
                if existing_user.data:
                    raise ConflictError("Username already exists")
            
            # Update profile
            response = client.table("user_profiles").update(update_dict).eq("id", user_id).execute()
            
            if not response.data:
                raise NotFoundError("User profile not found")
            
            return UserProfile(**response.data[0])
            
        except ConflictError:
            raise
        except Exception as e:
            if "not found" in str(e).lower():
                raise NotFoundError("User profile not found")
            raise InternalServerError(f"Failed to update user profile: {str(e)}")
    
    @staticmethod
    async def get_user_settings(user_id: str, access_token: str = None) -> List[UserSetting]:
        """
        Get all settings for a user
        
        Args:
            user_id: User's ID
            access_token: JWT access token for authenticated operations
            
        Returns:
            List of user settings
        """
        try:
            client = get_authenticated_client(access_token) if access_token else supabase_client
            response = client.table("user_settings").select("*").eq("user_id", user_id).order("setting_key").execute()
            
            return [UserSetting(**setting) for setting in response.data]
            
        except Exception as e:
            raise InternalServerError(f"Failed to fetch user settings: {str(e)}")
    
    @staticmethod
    async def get_user_setting(user_id: str, setting_key: str, access_token: str = None) -> UserSetting:
        """
        Get a specific setting for a user
        
        Args:
            user_id: User's ID
            setting_key: Setting key
            access_token: JWT access token for authenticated operations
            
        Returns:
            User setting
            
        Raises:
            NotFoundError: If setting not found
        """
        try:
            client = get_authenticated_client(access_token) if access_token else supabase_client
            response = client.table("user_settings").select("*").eq("user_id", user_id).eq("setting_key", setting_key).single().execute()
            
            if not response.data:
                raise NotFoundError("Setting not found")
            
            return UserSetting(**response.data)
            
        except Exception as e:
            if "not found" in str(e).lower():
                raise NotFoundError("Setting not found")
            raise InternalServerError(f"Failed to fetch setting: {str(e)}")
    
    @staticmethod
    async def create_user_setting(user_id: str, setting_data: UserSettingCreate, access_token: str = None) -> UserSetting:
        """
        Create a new user setting
        
        Args:
            user_id: User's ID
            setting_data: Setting creation data
            access_token: JWT access token for authenticated operations
            
        Returns:
            Created user setting
            
        Raises:
            ConflictError: If setting already exists
        """
        try:
            client = get_authenticated_client(access_token) if access_token else supabase_client
            
            # Check if setting already exists
            existing_setting = client.table("user_settings").select("id").eq("user_id", user_id).eq("setting_key", setting_data.setting_key).execute()
            
            if existing_setting.data:
                raise ConflictError("Setting with this key already exists")
            
            # Create new setting
            insert_data = {
                "user_id": user_id,
                "setting_key": setting_data.setting_key,
                "setting_value": setting_data.setting_value
            }
            
            response = client.table("user_settings").insert(insert_data).execute()
            
            if not response.data:
                raise InternalServerError("Failed to create setting")
            
            return UserSetting(**response.data[0])
            
        except ConflictError:
            raise
        except Exception as e:
            raise InternalServerError(f"Failed to create setting: {str(e)}")
    
    @staticmethod
    async def update_user_setting(user_id: str, setting_key: str, setting_data: UserSettingUpdate, access_token: str = None) -> UserSetting:
        """
        Update a user setting
        
        Args:
            user_id: User's ID
            setting_key: Setting key
            setting_data: Setting update data
            access_token: JWT access token for authenticated operations
            
        Returns:
            Updated user setting
            
        Raises:
            NotFoundError: If setting not found
        """
        try:
            client = get_authenticated_client(access_token) if access_token else supabase_client
            response = client.table("user_settings").update({"setting_value": setting_data.setting_value}).eq("user_id", user_id).eq("setting_key", setting_key).execute()
            
            if not response.data:
                raise NotFoundError("Setting not found")
            
            return UserSetting(**response.data[0])
            
        except Exception as e:
            if "not found" in str(e).lower():
                raise NotFoundError("Setting not found")
            raise InternalServerError(f"Failed to update setting: {str(e)}")
    
    @staticmethod
    async def delete_user_setting(user_id: str, setting_key: str, access_token: str = None) -> bool:
        """
        Delete a user setting
        
        Args:
            user_id: User's ID
            setting_key: Setting key
            access_token: JWT access token for authenticated operations
            
        Returns:
            True if deleted successfully
            
        Raises:
            NotFoundError: If setting not found
        """
        try:
            client = get_authenticated_client(access_token) if access_token else supabase_client
            response = client.table("user_settings").delete().eq("user_id", user_id).eq("setting_key", setting_key).execute()
            
            if not response.data:
                raise NotFoundError("Setting not found")
            
            return True
            
        except Exception as e:
            if "not found" in str(e).lower():
                raise NotFoundError("Setting not found")
            raise InternalServerError(f"Failed to delete setting: {str(e)}")
    
    @staticmethod
    async def get_user_stats(user_id: str, access_token: str = None) -> UserStats:
        """
        Get user statistics, creating if it doesn't exist
        
        Args:
            user_id: User's ID
            access_token: JWT access token for authenticated operations
            
        Returns:
            User statistics
        """
        try:
            client = get_authenticated_client(access_token) if access_token else supabase_client
            response = client.table("user_stats").select("*").eq("user_id", user_id).execute()
            
            if response.data and len(response.data) > 0:
                return UserStats(**response.data[0])
            
            # Create user stats if they don't exist using admin client
            logger.info(f"Creating user stats for {user_id}")
            stats_data = {"user_id": user_id}
            create_response = supabase_admin.table("user_stats").insert(stats_data).execute()
            
            if not create_response.data:
                raise InternalServerError("Failed to create user stats")
            
            return UserStats(**create_response.data[0])
            
        except Exception as e:
            logger.error(f"Failed to get/create user stats for {user_id}: {str(e)}")
            raise InternalServerError(f"Failed to fetch user stats: {str(e)}")