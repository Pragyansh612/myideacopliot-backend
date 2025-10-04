"""Share service for collaboration features"""
from typing import List, Optional
from app.core.database import supabase_admin
from app.models.share import IdeaShare
from app.schemas.share import ShareCreate, ShareUpdate, ShareResponse
from app.utils.exceptions import NotFoundError, ValidationError, ForbiddenError
import uuid
import logging

logger = logging.getLogger(__name__)


class ShareService:
    """Service for managing idea shares"""
    
    @staticmethod
    async def create_share(idea_id: uuid.UUID, owner_id: uuid.UUID, share_data: ShareCreate) -> ShareResponse:
        """
        Share an idea with another user
        
        Args:
            idea_id: ID of the idea to share
            owner_id: ID of the idea owner
            share_data: Share creation data
            
        Returns:
            Created share information
        """
        try:
            # First verify the idea belongs to the owner
            idea_response = supabase_admin.table("ideas").select("*").eq("id", str(idea_id)).eq("user_id", str(owner_id)).execute()
            
            if not idea_response.data:
                raise ForbiddenError("You don't have permission to share this idea")
            
            # Find user by email
            user_response = supabase_admin.auth.admin.list_users()
            shared_user = None
            for user in user_response:
                if user.email == share_data.shared_with_email:
                    shared_user = user
                    break
            
            if not shared_user:
                raise NotFoundError(f"User with email {share_data.shared_with_email} not found")
            
            # Check if share already exists
            existing_share = supabase_admin.table("idea_shares").select("*").eq("idea_id", str(idea_id)).eq("shared_with_id", shared_user.id).execute()
            
            if existing_share.data:
                raise ValidationError("This idea is already shared with this user")
            
            # Create the share
            share_insert = {
                "idea_id": str(idea_id),
                "owner_id": str(owner_id),
                "shared_with_id": shared_user.id,
                "role": share_data.role,
                "is_active": True
            }
            
            if share_data.expires_at:
                share_insert["expires_at"] = share_data.expires_at.isoformat()
            
            response = supabase_admin.table("idea_shares").insert(share_insert).execute()
            
            if not response.data:
                raise ValidationError("Failed to create share")
            
            share = response.data[0]
            share["shared_with_email"] = shared_user.email
            
            return ShareResponse(**share)
            
        except (NotFoundError, ValidationError, ForbiddenError):
            raise
        except Exception as e:
            logger.error(f"Error creating share: {str(e)}")
            raise ValidationError(f"Failed to create share: {str(e)}")
    
    @staticmethod
    async def get_idea_shares(idea_id: uuid.UUID, user_id: uuid.UUID) -> List[ShareResponse]:
        """
        Get all shares for an idea
        
        Args:
            idea_id: ID of the idea
            user_id: ID of the requesting user
            
        Returns:
            List of shares
        """
        try:
            # Verify user owns the idea
            idea_response = supabase_admin.table("ideas").select("*").eq("id", str(idea_id)).eq("user_id", str(user_id)).execute()
            
            if not idea_response.data:
                raise ForbiddenError("You don't have permission to view shares for this idea")
            
            # Get all shares
            response = supabase_admin.table("idea_shares").select("*").eq("idea_id", str(idea_id)).order("shared_at", desc=True).execute()
            
            shares = []
            for share in response.data:
                # Get user email for each share
                try:
                    user = supabase_admin.auth.admin.get_user_by_id(share["shared_with_id"])
                    share["shared_with_email"] = user.user.email
                except:
                    share["shared_with_email"] = "unknown"
                
                shares.append(ShareResponse(**share))
            
            return shares
            
        except ForbiddenError:
            raise
        except Exception as e:
            logger.error(f"Error getting shares: {str(e)}")
            raise ValidationError(f"Failed to get shares: {str(e)}")
    
    @staticmethod
    async def update_share(share_id: uuid.UUID, owner_id: uuid.UUID, update_data: ShareUpdate) -> ShareResponse:
        """
        Update a share
        
        Args:
            share_id: ID of the share
            owner_id: ID of the idea owner
            update_data: Update data
            
        Returns:
            Updated share
        """
        try:
            # Verify share belongs to owner
            share_response = supabase_admin.table("idea_shares").select("*").eq("id", str(share_id)).eq("owner_id", str(owner_id)).execute()
            
            if not share_response.data:
                raise ForbiddenError("You don't have permission to update this share")
            
            # Prepare update data
            update_dict = update_data.dict(exclude_unset=True)
            
            if update_dict:
                response = supabase_admin.table("idea_shares").update(update_dict).eq("id", str(share_id)).execute()
                
                if not response.data:
                    raise ValidationError("Failed to update share")
                
                share = response.data[0]
                
                # Get user email
                try:
                    user = supabase_admin.auth.admin.get_user_by_id(share["shared_with_id"])
                    share["shared_with_email"] = user.user.email
                except:
                    share["shared_with_email"] = "unknown"
                
                return ShareResponse(**share)
            
            return ShareResponse(**share_response.data[0])
            
        except ForbiddenError:
            raise
        except Exception as e:
            logger.error(f"Error updating share: {str(e)}")
            raise ValidationError(f"Failed to update share: {str(e)}")
    
    @staticmethod
    async def delete_share(share_id: uuid.UUID, owner_id: uuid.UUID) -> None:
        """
        Delete (revoke) a share
        
        Args:
            share_id: ID of the share
            owner_id: ID of the idea owner
        """
        try:
            # Verify share belongs to owner
            share_response = supabase_admin.table("idea_shares").select("*").eq("id", str(share_id)).eq("owner_id", str(owner_id)).execute()
            
            if not share_response.data:
                raise ForbiddenError("You don't have permission to delete this share")
            
            # Delete the share
            supabase_admin.table("idea_shares").delete().eq("id", str(share_id)).execute()
            
        except ForbiddenError:
            raise
        except Exception as e:
            logger.error(f"Error deleting share: {str(e)}")
            raise ValidationError(f"Failed to delete share: {str(e)}")
    
    @staticmethod
    async def check_idea_access(idea_id: uuid.UUID, user_id: uuid.UUID) -> tuple[bool, str]:
        """
        Check if user has access to an idea
        
        Args:
            idea_id: ID of the idea
            user_id: ID of the user
            
        Returns:
            Tuple of (has_access, role) where role is 'owner', 'editor', or 'viewer'
        """
        try:
            # Check if user owns the idea
            idea_response = supabase_admin.table("ideas").select("*").eq("id", str(idea_id)).eq("user_id", str(user_id)).execute()
            
            if idea_response.data:
                return True, "owner"
            
            # Check if idea is shared with user
            share_response = supabase_admin.table("idea_shares").select("*").eq("idea_id", str(idea_id)).eq("shared_with_id", str(user_id)).eq("is_active", True).execute()
            
            if share_response.data:
                return True, share_response.data[0]["role"]
            
            return False, None
            
        except Exception as e:
            logger.error(f"Error checking access: {str(e)}")
            return False, None

