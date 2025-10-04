"""Comment service for threaded discussions"""
from typing import List, Optional
from app.core.database import supabase_admin
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse
from app.services.share import ShareService
from app.utils.exceptions import NotFoundError, ValidationError, ForbiddenError
import uuid
import logging

logger = logging.getLogger(__name__)


class CommentService:
    """Service for managing comments"""
    
    @staticmethod
    async def create_idea_comment(idea_id: uuid.UUID, user_id: uuid.UUID, comment_data: CommentCreate) -> CommentResponse:
        """
        Create a comment on an idea
        
        Args:
            idea_id: ID of the idea
            user_id: ID of the user creating comment
            comment_data: Comment creation data
            
        Returns:
            Created comment
        """
        try:
            # Check access
            has_access, role = await ShareService.check_idea_access(idea_id, user_id)
            if not has_access:
                raise ForbiddenError("You don't have access to this idea")
            
            # Create comment
            comment_insert = {
                "user_id": str(user_id),
                "idea_id": str(idea_id),
                "content": comment_data.content,
                "is_ai_generated": False
            }
            
            if comment_data.parent_comment_id:
                comment_insert["parent_comment_id"] = str(comment_data.parent_comment_id)
            
            response = supabase_admin.table("comments").insert(comment_insert).execute()
            
            if not response.data:
                raise ValidationError("Failed to create comment")
            
            comment = response.data[0]
            
            # Get author email
            try:
                user = supabase_admin.auth.admin.get_user_by_id(str(user_id))
                comment["author_email"] = user.user.email
            except:
                comment["author_email"] = "unknown"
            
            comment["replies"] = []
            
            return CommentResponse(**comment)
            
        except (ForbiddenError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Error creating comment: {str(e)}")
            raise ValidationError(f"Failed to create comment: {str(e)}")
    
    @staticmethod
    async def create_feature_comment(feature_id: uuid.UUID, user_id: uuid.UUID, comment_data: CommentCreate) -> CommentResponse:
        """
        Create a comment on a feature
        
        Args:
            feature_id: ID of the feature
            user_id: ID of the user creating comment
            comment_data: Comment creation data
            
        Returns:
            Created comment
        """
        try:
            # Get feature's idea_id
            feature_response = supabase_admin.table("features").select("idea_id").eq("id", str(feature_id)).execute()
            
            if not feature_response.data:
                raise NotFoundError("Feature not found")
            
            idea_id = feature_response.data[0]["idea_id"]
            
            # Check access
            has_access, role = await ShareService.check_idea_access(uuid.UUID(idea_id), user_id)
            if not has_access:
                raise ForbiddenError("You don't have access to this feature")
            
            # Create comment
            comment_insert = {
                "user_id": str(user_id),
                "feature_id": str(feature_id),
                "content": comment_data.content,
                "is_ai_generated": False
            }
            
            if comment_data.parent_comment_id:
                comment_insert["parent_comment_id"] = str(comment_data.parent_comment_id)
            
            response = supabase_admin.table("comments").insert(comment_insert).execute()
            
            if not response.data:
                raise ValidationError("Failed to create comment")
            
            comment = response.data[0]
            
            # Get author email
            try:
                user = supabase_admin.auth.admin.get_user_by_id(str(user_id))
                comment["author_email"] = user.user.email
            except:
                comment["author_email"] = "unknown"
            
            comment["replies"] = []
            
            return CommentResponse(**comment)
            
        except (NotFoundError, ForbiddenError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Error creating comment: {str(e)}")
            raise ValidationError(f"Failed to create comment: {str(e)}")
    
    @staticmethod
    async def get_idea_comments(idea_id: uuid.UUID, user_id: uuid.UUID, limit: int = 50, offset: int = 0) -> List[CommentResponse]:
        """
        Get all comments for an idea with threading
        
        Args:
            idea_id: ID of the idea
            user_id: ID of the requesting user
            limit: Maximum number of comments
            offset: Offset for pagination
            
        Returns:
            List of comments with nested replies
        """
        try:
            # Check access
            has_access, role = await ShareService.check_idea_access(idea_id, user_id)
            if not has_access:
                raise ForbiddenError("You don't have access to this idea")
            
            # Get all comments
            response = supabase_admin.table("comments").select("*").eq("idea_id", str(idea_id)).order("created_at", desc=False).execute()
            
            if not response.data:
                return []
            
            # Build comment tree
            comments_dict = {}
            root_comments = []
            
            for comment_data in response.data:
                # Get author email
                try:
                    user = supabase_admin.auth.admin.get_user_by_id(comment_data["user_id"])
                    comment_data["author_email"] = user.user.email
                except:
                    comment_data["author_email"] = "unknown"
                
                comment_data["replies"] = []
                comment = CommentResponse(**comment_data)
                comments_dict[str(comment.id)] = comment
                
                if comment.parent_comment_id is None:
                    root_comments.append(comment)
            
            # Build tree structure
            for comment in comments_dict.values():
                if comment.parent_comment_id and str(comment.parent_comment_id) in comments_dict:
                    parent = comments_dict[str(comment.parent_comment_id)]
                    parent.replies.append(comment)
            
            # Apply pagination to root comments
            return root_comments[offset:offset + limit]
            
        except ForbiddenError:
            raise
        except Exception as e:
            logger.error(f"Error getting comments: {str(e)}")
            raise ValidationError(f"Failed to get comments: {str(e)}")
    
    @staticmethod
    async def update_comment(comment_id: uuid.UUID, user_id: uuid.UUID, update_data: CommentUpdate) -> CommentResponse:
        """
        Update a comment
        
        Args:
            comment_id: ID of the comment
            user_id: ID of the user
            update_data: Update data
            
        Returns:
            Updated comment
        """
        try:
            # Verify comment belongs to user
            comment_response = supabase_admin.table("comments").select("*").eq("id", str(comment_id)).eq("user_id", str(user_id)).execute()
            
            if not comment_response.data:
                raise ForbiddenError("You don't have permission to update this comment")
            
            # Update comment
            response = supabase_admin.table("comments").update({"content": update_data.content}).eq("id", str(comment_id)).execute()
            
            if not response.data:
                raise ValidationError("Failed to update comment")
            
            comment = response.data[0]
            
            # Get author email
            try:
                user = supabase_admin.auth.admin.get_user_by_id(str(user_id))
                comment["author_email"] = user.user.email
            except:
                comment["author_email"] = "unknown"
            
            comment["replies"] = []
            
            return CommentResponse(**comment)
            
        except (ForbiddenError, ValidationError):
            raise
        except Exception as e:
            logger.error(f"Error updating comment: {str(e)}")
            raise ValidationError(f"Failed to update comment: {str(e)}")
    
    @staticmethod
    async def delete_comment(comment_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """
        Soft-delete a comment
        
        Args:
            comment_id: ID of the comment
            user_id: ID of the user
        """
        try:
            # Verify comment belongs to user
            comment_response = supabase_admin.table("comments").select("*").eq("id", str(comment_id)).eq("user_id", str(user_id)).execute()
            
            if not comment_response.data:
                raise ForbiddenError("You don't have permission to delete this comment")
            
            # Soft delete by updating content
            supabase_admin.table("comments").update({"content": "[deleted]"}).eq("id", str(comment_id)).execute()
            
        except ForbiddenError:
            raise
        except Exception as e:
            logger.error(f"Error deleting comment: {str(e)}")
            raise ValidationError(f"Failed to delete comment: {str(e)}")
