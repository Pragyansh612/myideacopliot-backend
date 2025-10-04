"""AI service for generating suggestions and managing queries"""
import os
import time
import uuid
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
import google.generativeai as genai
from app.core.database import supabase_client 
from app.utils.exceptions import ValidationError
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

# Configure Gemini
GEMINI_API_KEY = settings.GEMINI_API_KEY
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY not found in environment variables")


class AIService:
    """Service for AI operations"""
    
    @staticmethod
    async def generate_suggestions(
        user_id: str,
        idea_id: str,
        suggestion_type: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate AI suggestions for an idea using Gemini
        """
        try:
            if not GEMINI_API_KEY:
                raise ValidationError("Gemini API key not configured")
            
            supabase = supabase_client
            
            # Get the idea details
            idea_response = supabase.table("ideas").select("*").eq("id", idea_id).eq("user_id", user_id).single().execute()
            
            if not idea_response.data:
                raise ValidationError("Idea not found or access denied")
            
            idea = idea_response.data
            
            # Construct prompt based on suggestion type
            prompts = {
                "features": f"""
                Analyze this product idea and suggest 5 innovative features that would make it stand out:
                
                Title: {idea['title']}
                Description: {idea.get('description', '')}
                Tags: {', '.join(idea.get('tags', []))}
                
                Additional Context: {context or 'None'}
                
                Provide features that are:
                1. Innovative yet practical
                2. Aligned with the core value proposition
                3. Technically feasible
                4. User-centric
                
                Format your response as a JSON array of objects with: title, description, priority (high/medium/low), estimated_effort (1-10)
                """,
                
                "improvements": f"""
                Review this product idea and suggest 5 specific improvements:
                
                Title: {idea['title']}
                Description: {idea.get('description', '')}
                Current Features: {json.dumps(idea.get('features', []))}
                
                Additional Context: {context or 'None'}
                
                Focus on:
                1. User experience enhancements
                2. Performance optimizations
                3. Scalability considerations
                4. Market differentiation
                
                Format your response as a JSON array of objects with: title, description, impact (high/medium/low), effort (low/medium/high)
                """,
                
                "marketing": f"""
                Create a marketing strategy for this product idea:
                
                Title: {idea['title']}
                Description: {idea.get('description', '')}
                Target Market: {idea.get('target_market', 'General audience')}
                
                Additional Context: {context or 'None'}
                
                Provide:
                1. Value proposition (1-2 sentences)
                2. Target audience segments (3-4)
                3. Marketing channels (5)
                4. Key messaging points (5)
                5. Launch strategy overview
                
                Format your response as a JSON object with these keys.
                """,
                
                "validation": f"""
                Evaluate this product idea for market viability:
                
                Title: {idea['title']}
                Description: {idea.get('description', '')}
                Target Market: {idea.get('target_market', 'General audience')}
                
                Additional Context: {context or 'None'}
                
                Provide:
                1. Market opportunity assessment
                2. Potential challenges (3-5)
                3. Competitive advantage points (3-5)
                4. Recommended next steps (5)
                5. Risk factors (3-5)
                
                Format your response as a JSON object with these keys.
                """
            }
            
            prompt = prompts.get(suggestion_type)
            if not prompt:
                raise ValidationError(f"Invalid suggestion type: {suggestion_type}")
            
            # Generate content using Gemini
            start_time = time.time()
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            end_time = time.time()
            
            response_time_ms = int((end_time - start_time) * 1000)
            
            # Parse the response
            ai_response = response.text
            
            # Try to extract JSON from the response
            try:
                # Remove markdown code blocks if present
                if "```json" in ai_response:
                    ai_response = ai_response.split("```json")[1].split("```")[0].strip()
                elif "```" in ai_response:
                    ai_response = ai_response.split("```")[1].split("```")[0].strip()
                
                content_data = json.loads(ai_response)
            except json.JSONDecodeError:
                # If JSON parsing fails, use the raw response
                content_data = {"raw_response": ai_response}
            
            # Log the query
            query_log = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "idea_id": idea_id,
                "query_type": f"suggestion_{suggestion_type}",
                "user_prompt": prompt,
                "ai_response": ai_response,
                "ai_model": "gemini-pro",
                "tokens_used": len(prompt.split()) + len(ai_response.split()),  # Rough estimate
                "response_time_ms": response_time_ms,
                "context_data": {"suggestion_type": suggestion_type, "context": context}
            }
            
            supabase.table("ai_query_logs").insert(query_log).execute()
            
            # Save the suggestion
            suggestion = {
                "id": str(uuid.uuid4()),
                "idea_id": idea_id,
                "user_id": user_id,
                "suggestion_type": suggestion_type,
                "title": f"{suggestion_type.title()} Suggestions",
                "content": json.dumps(content_data),
                "confidence_score": 0.85,  # Could be calculated based on response quality
                "is_applied": False,
                "ai_model": "gemini-pro",
                "prompt_used": prompt[:500]  # Store truncated prompt
            }
            
            result = supabase.table("ai_suggestions").insert(suggestion).execute()
            
            return result.data[0]
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            raise
    
    @staticmethod
    async def get_suggestions(user_id: str, idea_id: str) -> List[Dict[str, Any]]:
        """Get all AI suggestions for an idea"""
        try:
            supabase = supabase_client
            
            response = supabase.table("ai_suggestions")\
                .select("*")\
                .eq("idea_id", idea_id)\
                .order("created_at", desc=True)\
                .execute()
            
            suggestions = response.data
            
            # Parse content JSON
            for suggestion in suggestions:
                try:
                    suggestion["content"] = json.loads(suggestion["content"])
                except:
                    pass
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting suggestions: {e}")
            raise
    
    @staticmethod
    async def get_query_logs(user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get AI query logs for a user"""
        try:
            supabase = supabase_client
            
            response = supabase.table("ai_query_logs")\
                .select("*")\
                .eq("user_id", user_id)\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            return response.data
            
        except Exception as e:
            logger.error(f"Error getting query logs: {e}")
            raise
