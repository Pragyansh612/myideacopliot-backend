"""Idea service - Complete implementation"""
from typing import List, Optional
from datetime import datetime
from app.core.database import supabase_client, get_authenticated_client
from app.schemas.idea import (
    IdeaCreate, IdeaUpdate, CategoryCreate, CategoryUpdate,
    PhaseCreate, PhaseUpdate, FeatureCreate, FeatureUpdate,
    IdeaListParams, PaginatedIdeaResponse, IdeaDetailResponse,
    CategoryResponse, PhaseResponse, FeatureResponse, IdeaResponse
)
from app.utils.exceptions import NotFoundError, ForbiddenError, InternalServerError
import logging

logger = logging.getLogger(__name__)


class IdeaService:
    """Service for managing ideas, categories, phases, and features"""

    # ==================== CATEGORIES ====================
    
    @staticmethod
    async def get_categories(user_id: str, access_token: str = None) -> List[CategoryResponse]:
        """Get all categories for a user"""
        try:
            client = get_authenticated_client(access_token) if access_token else supabase_client
            response = client.table("categories").select("*").eq("user_id", user_id).execute()
            return [CategoryResponse(**cat) for cat in response.data]
        except Exception as e:
            logger.error(f"Error fetching categories: {str(e)}")
            raise InternalServerError(f"Failed to fetch categories: {str(e)}")
    
    @staticmethod
    async def create_category(user_id: str, category_data: CategoryCreate, access_token: str = None) -> CategoryResponse:
        """Create a new category"""
        try:
            client = get_authenticated_client(access_token) if access_token else supabase_client
            
            insert_data = {"user_id": user_id, **category_data.model_dump()}
            response = client.table("categories").insert(insert_data).execute()
            
            if not response.data:
                raise InternalServerError("Failed to create category")
            
            return CategoryResponse(**response.data[0])
        except Exception as e:
            logger.error(f"Error creating category: {e}")
            raise InternalServerError(f"Failed to create category: {str(e)}")
    
    @staticmethod
    async def get_category_by_id(user_id: str, category_id: str, access_token: str = None) -> CategoryResponse:
        """Get a category by ID"""
        try:
            client = get_authenticated_client(access_token) if access_token else supabase_client
            response = client.table("categories").select("*").eq("id", category_id).eq("user_id", user_id).execute()
            
            if not response.data:
                raise NotFoundError("Category not found")
            
            return CategoryResponse(**response.data[0])
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error fetching category: {str(e)}")
            raise InternalServerError(f"Failed to fetch category: {str(e)}")
    
    @staticmethod
    async def update_category(user_id: str, category_id: str, category_data: CategoryUpdate, access_token: str = None) -> CategoryResponse:
        """Update a category"""
        try:
            client = get_authenticated_client(access_token) if access_token else supabase_client
            
            update_dict = category_data.model_dump(exclude_unset=True)
            response = client.table("categories").update(update_dict).eq("id", category_id).eq("user_id", user_id).execute()
            
            if not response.data:
                raise NotFoundError("Category not found")
            
            return CategoryResponse(**response.data[0])
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error updating category: {str(e)}")
            raise InternalServerError(f"Failed to update category: {str(e)}")
    
    @staticmethod
    async def delete_category(user_id: str, category_id: str, access_token: str = None) -> bool:
        """Delete a category"""
        try:
            client = get_authenticated_client(access_token) if access_token else supabase_client
            response = client.table("categories").delete().eq("id", category_id).eq("user_id", user_id).execute()
            
            if not response.data:
                raise NotFoundError("Category not found")
            
            return True
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error deleting category: {str(e)}")
            raise InternalServerError(f"Failed to delete category: {str(e)}")

    # ==================== IDEAS ====================
    
    @staticmethod
    async def create_idea(user_id: str, idea_data: IdeaCreate, access_token: str = None) -> IdeaResponse:
        """Create a new idea"""
        try:
            client = get_authenticated_client(access_token) if access_token else supabase_client
            
            insert_data = {"user_id": user_id, **idea_data.model_dump(exclude_unset=True)}
            
            # Handle enum conversion
            if "priority" in insert_data and insert_data["priority"]:
                insert_data["priority"] = insert_data["priority"].value
            if "status" in insert_data and insert_data["status"]:
                insert_data["status"] = insert_data["status"].value
            
            response = client.table("ideas").insert(insert_data).execute()
            
            if not response.data:
                raise InternalServerError("Failed to create idea")
            
            return IdeaResponse(**response.data[0])
        except Exception as e:
            logger.error(f"Error creating idea: {e}")
            raise InternalServerError(f"Failed to create idea: {str(e)}")
    
    @staticmethod
    async def get_ideas(user_id: str, params: IdeaListParams, access_token: str = None) -> PaginatedIdeaResponse:
        """Get paginated list of ideas"""
        try:
            client = get_authenticated_client(access_token) if access_token else supabase_client
            
            query = client.table("ideas").select("*", count="exact").eq("user_id", user_id)
            
            # Apply filters
            if params.category_id:
                query = query.eq("category_id", params.category_id)
            if params.priority:
                query = query.eq("priority", params.priority.value)
            if params.status:
                query = query.eq("status", params.status.value)
            if params.search:
                query = query.ilike("title", f"%{params.search}%")
            
            # Apply sorting
            query = query.order(params.sort_by, desc=(params.sort_order == "desc"))
            
            # Apply pagination
            query = query.range(params.offset, params.offset + params.limit - 1)
            
            response = query.execute()
            
            ideas = [IdeaResponse(**idea) for idea in response.data]
            
            return PaginatedIdeaResponse.create(
                ideas=ideas,
                total=response.count or 0,
                limit=params.limit,
                offset=params.offset
            )
        except Exception as e:
            logger.error(f"Error fetching ideas: {str(e)}")
            raise InternalServerError(f"Failed to fetch ideas: {str(e)}")
    
    @staticmethod
    async def get_idea_by_id(user_id: str, idea_id: str, access_token: str = None) -> IdeaDetailResponse:
        """Get idea by ID with phases and features"""
        try:
            client = get_authenticated_client(access_token) if access_token else supabase_client
            
            # Verify access
            await IdeaService._verify_access(user_id, idea_id, False, access_token)
            
            idea_response = client.table("ideas").select("*").eq("id", idea_id).execute()
            if not idea_response.data:
                raise NotFoundError("Idea not found")
            
            idea = IdeaResponse(**idea_response.data[0])
            
            # Get phases and features
            phases = await IdeaService.get_phases(user_id, idea_id, access_token)
            features = await IdeaService.get_features(user_id, idea_id, access_token)
            
            return IdeaDetailResponse(idea=idea, phases=phases, features=features)
        except (NotFoundError, ForbiddenError):
            raise
        except Exception as e:
            logger.error(f"Error fetching idea: {str(e)}")
            raise InternalServerError(f"Failed to fetch idea: {str(e)}")
    
    @staticmethod
    async def update_idea(user_id: str, idea_id: str, idea_data: IdeaUpdate, access_token: str = None) -> IdeaResponse:
        """Update an idea"""
        try:
            client = get_authenticated_client(access_token) if access_token else supabase_client
            
            await IdeaService._verify_access(user_id, idea_id, True, access_token)
            
            update_dict = idea_data.model_dump(exclude_unset=True)
            
            # Handle enum conversion
            if "priority" in update_dict and update_dict["priority"]:
                update_dict["priority"] = update_dict["priority"].value
            if "status" in update_dict and update_dict["status"]:
                update_dict["status"] = update_dict["status"].value
            
            response = client.table("ideas").update(update_dict).eq("id", idea_id).execute()
            
            if not response.data:
                raise NotFoundError("Idea not found")
            
            return IdeaResponse(**response.data[0])
        except (NotFoundError, ForbiddenError):
            raise
        except Exception as e:
            logger.error(f"Error updating idea: {str(e)}")
            raise InternalServerError(f"Failed to update idea: {str(e)}")
    
    @staticmethod
    async def delete_idea(user_id: str, idea_id: str, access_token: str = None) -> bool:
        """Delete an idea"""
        try:
            client = get_authenticated_client(access_token) if access_token else supabase_client
            
            await IdeaService._verify_access(user_id, idea_id, True, access_token)
            
            response = client.table("ideas").delete().eq("id", idea_id).execute()
            
            if not response.data:
                raise NotFoundError("Idea not found")
            
            return True
        except (NotFoundError, ForbiddenError):
            raise
        except Exception as e:
            logger.error(f"Error deleting idea: {str(e)}")
            raise InternalServerError(f"Failed to delete idea: {str(e)}")

    # ==================== PHASES ====================
    
    @staticmethod
    async def create_phase(user_id: str, idea_id: str, phase_data: PhaseCreate, access_token: str = None) -> PhaseResponse:
        """Create a phase"""
        try:
            client = get_authenticated_client(access_token) if access_token else supabase_client
            
            await IdeaService._verify_access(user_id, idea_id, True, access_token)
            
            insert_data = {"idea_id": idea_id, **phase_data.model_dump()}
            response = client.table("phases").insert(insert_data).execute()
            
            if not response.data:
                raise InternalServerError("Failed to create phase")
            
            return PhaseResponse(**response.data[0])
        except (NotFoundError, ForbiddenError):
            raise
        except Exception as e:
            logger.error(f"Error creating phase: {str(e)}")
            raise InternalServerError(f"Failed to create phase: {str(e)}")
    
    @staticmethod
    async def get_phases(user_id: str, idea_id: str, access_token: str = None) -> List[PhaseResponse]:
        """Get all phases for an idea"""
        try:
            client = get_authenticated_client(access_token) if access_token else supabase_client
            
            await IdeaService._verify_access(user_id, idea_id, False, access_token)
            
            response = client.table("phases").select("*").eq("idea_id", idea_id).order("order_index").execute()
            return [PhaseResponse(**phase) for phase in response.data]
        except (NotFoundError, ForbiddenError):
            raise
        except Exception as e:
            logger.error(f"Error fetching phases: {str(e)}")
            raise InternalServerError(f"Failed to fetch phases: {str(e)}")
    
    @staticmethod
    async def update_phase(user_id: str, phase_id: str, phase_data: PhaseUpdate, access_token: str = None) -> PhaseResponse:
        """Update a phase"""
        try:
            client = get_authenticated_client(access_token) if access_token else supabase_client
            
            # Get phase to verify access
            phase_response = client.table("phases").select("idea_id").eq("id", phase_id).execute()
            if not phase_response.data:
                raise NotFoundError("Phase not found")
            
            idea_id = phase_response.data[0]["idea_id"]
            await IdeaService._verify_access(user_id, idea_id, True, access_token)
            
            update_dict = phase_data.model_dump(exclude_unset=True)
            response = client.table("phases").update(update_dict).eq("id", phase_id).execute()
            
            if not response.data:
                raise NotFoundError("Phase not found")
            
            return PhaseResponse(**response.data[0])
        except (NotFoundError, ForbiddenError):
            raise
        except Exception as e:
            logger.error(f"Error updating phase: {str(e)}")
            raise InternalServerError(f"Failed to update phase: {str(e)}")
    
    @staticmethod
    async def delete_phase(user_id: str, phase_id: str, access_token: str = None) -> bool:
        """Delete a phase"""
        try:
            client = get_authenticated_client(access_token) if access_token else supabase_client
            
            phase_response = client.table("phases").select("idea_id").eq("id", phase_id).execute()
            if not phase_response.data:
                raise NotFoundError("Phase not found")
            
            idea_id = phase_response.data[0]["idea_id"]
            await IdeaService._verify_access(user_id, idea_id, True, access_token)
            
            client.table("phases").delete().eq("id", phase_id).execute()
            return True
        except (NotFoundError, ForbiddenError):
            raise
        except Exception as e:
            logger.error(f"Error deleting phase: {str(e)}")
            raise InternalServerError(f"Failed to delete phase: {str(e)}")

    # ==================== FEATURES ====================
    
    @staticmethod
    async def create_feature_for_idea(user_id: str, idea_id: str, feature_data: FeatureCreate, access_token: str = None) -> FeatureResponse:
        """Create a feature for an idea"""
        try:
            client = get_authenticated_client(access_token) if access_token else supabase_client
            
            await IdeaService._verify_access(user_id, idea_id, True, access_token)
            
            insert_data = {"idea_id": idea_id, **feature_data.model_dump()}
            if "priority" in insert_data and insert_data["priority"]:
                insert_data["priority"] = insert_data["priority"].value
            
            response = client.table("features").insert(insert_data).execute()
            
            if not response.data:
                raise InternalServerError("Failed to create feature")
            
            return FeatureResponse(**response.data[0])
        except (NotFoundError, ForbiddenError):
            raise
        except Exception as e:
            logger.error(f"Error creating feature: {str(e)}")
            raise InternalServerError(f"Failed to create feature: {str(e)}")
    
    @staticmethod
    async def create_feature_for_phase(user_id: str, phase_id: str, feature_data: FeatureCreate, access_token: str = None) -> FeatureResponse:
        """Create a feature for a phase"""
        try:
            client = get_authenticated_client(access_token) if access_token else supabase_client
            
            phase_response = client.table("phases").select("idea_id").eq("id", phase_id).execute()
            if not phase_response.data:
                raise NotFoundError("Phase not found")
            
            idea_id = phase_response.data[0]["idea_id"]
            await IdeaService._verify_access(user_id, idea_id, True, access_token)
            
            insert_data = {"idea_id": idea_id, "phase_id": phase_id, **feature_data.model_dump()}
            if "priority" in insert_data and insert_data["priority"]:
                insert_data["priority"] = insert_data["priority"].value
            
            response = client.table("features").insert(insert_data).execute()
            
            if not response.data:
                raise InternalServerError("Failed to create feature")
            
            return FeatureResponse(**response.data[0])
        except (NotFoundError, ForbiddenError):
            raise
        except Exception as e:
            logger.error(f"Error creating feature: {str(e)}")
            raise InternalServerError(f"Failed to create feature: {str(e)}")
    
    @staticmethod
    async def get_features(user_id: str, idea_id: str, access_token: str = None) -> List[FeatureResponse]:
        """Get all features for an idea"""
        try:
            client = get_authenticated_client(access_token) if access_token else supabase_client
            
            await IdeaService._verify_access(user_id, idea_id, False, access_token)
            
            response = client.table("features").select("*").eq("idea_id", idea_id).execute()
            return [FeatureResponse(**feature) for feature in response.data]
        except (ForbiddenError, NotFoundError):
            raise
        except Exception as e:
            logger.error(f"Error fetching features: {str(e)}")
            raise InternalServerError(f"Failed to fetch features: {str(e)}")
    
    @staticmethod
    async def update_feature(user_id: str, feature_id: str, feature_data: FeatureUpdate, access_token: str = None) -> FeatureResponse:
        """Update a feature"""
        try:
            client = get_authenticated_client(access_token) if access_token else supabase_client
            
            feature_response = client.table("features").select("idea_id").eq("id", feature_id).execute()
            if not feature_response.data:
                raise NotFoundError("Feature not found")
            
            idea_id = feature_response.data[0]["idea_id"]
            await IdeaService._verify_access(user_id, idea_id, True, access_token)
            
            update_dict = feature_data.model_dump(exclude_unset=True)
            if "priority" in update_dict and update_dict["priority"]:
                update_dict["priority"] = update_dict["priority"].value
            
            response = client.table("features").update(update_dict).eq("id", feature_id).execute()
            
            if not response.data:
                raise NotFoundError("Feature not found")
            
            return FeatureResponse(**response.data[0])
        except (NotFoundError, ForbiddenError):
            raise
        except Exception as e:
            logger.error(f"Error updating feature: {str(e)}")
            raise InternalServerError(f"Failed to update feature: {str(e)}")
    
    @staticmethod
    async def delete_feature(user_id: str, feature_id: str, access_token: str = None) -> bool:
        """Delete a feature"""
        try:
            client = get_authenticated_client(access_token) if access_token else supabase_client
            
            feature_response = client.table("features").select("idea_id").eq("id", feature_id).execute()
            if not feature_response.data:
                raise NotFoundError("Feature not found")
            
            idea_id = feature_response.data[0]["idea_id"]
            await IdeaService._verify_access(user_id, idea_id, True, access_token)
            
            client.table("features").delete().eq("id", feature_id).execute()
            return True
        except (NotFoundError, ForbiddenError):
            raise
        except Exception as e:
            logger.error(f"Error deleting feature: {str(e)}")
            raise InternalServerError(f"Failed to delete feature: {str(e)}")

    # ==================== HELPER METHODS ====================
    
    @staticmethod
    async def _verify_access(user_id: str, idea_id: str, require_editor: bool = False, access_token: str = None) -> bool:
        """Verify user has access to an idea"""
        try:
            client = get_authenticated_client(access_token) if access_token else supabase_client
            
            idea_response = client.table("ideas").select("user_id").eq("id", idea_id).execute()
            if not idea_response.data:
                raise NotFoundError("Idea not found")
            
            if idea_response.data[0]["user_id"] == user_id:
                return True
            
            raise ForbiddenError("You don't have access to this idea")
        except (NotFoundError, ForbiddenError):
            raise
        except Exception as e:
            logger.error(f"Error verifying access: {e}")
            raise InternalServerError(f"Failed to verify access: {str(e)}")