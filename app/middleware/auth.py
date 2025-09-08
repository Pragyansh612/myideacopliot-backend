"""Fixed Authentication middleware with proper path handling"""
from typing import Optional
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.exceptions import AuthenticationError
import jwt
from datetime import datetime
from app.core.config import settings
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class JWTAuthService:
    """JWT validation service for Supabase tokens"""
    
    @staticmethod
    def validate_and_decode_token(token: str) -> Optional[dict]:
        """
        Validate and decode Supabase JWT token
        """
        try:
            logger.debug(f"Validating token: {token[:50]}...")
            logger.debug(f"Using JWT secret: {settings.SUPABASE_JWT_SECRET[:20]}...")
            
            # Decode the JWT token using Supabase JWT secret
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated"
            )
            
            logger.debug(f"Token decoded successfully: {payload}")
            
            # Check if token is expired
            if payload.get("exp") and datetime.utcnow().timestamp() > payload["exp"]:
                logger.warning(f"Token expired: {payload.get('exp')} < {datetime.utcnow().timestamp()}")
                return None
            
            # Return user data in a consistent format
            user_data = {
                "id": payload.get("sub"),
                "email": payload.get("email"),
                "phone": payload.get("phone", ""),
                "app_metadata": payload.get("app_metadata", {}),
                "user_metadata": payload.get("user_metadata", {}),
                "role": payload.get("role", "authenticated"),
                "aud": payload.get("aud"),
                "exp": payload.get("exp"),
                "iat": payload.get("iat"),
                "session_id": payload.get("session_id"),
                "is_anonymous": payload.get("is_anonymous", False)
            }
            
            logger.debug(f"Returning user data: {user_data}")
            return user_data
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidAudienceError as e:
            logger.error(f"Invalid audience: {e}")
            return None
        except jwt.InvalidSignatureError as e:
            logger.error(f"Invalid signature: {e}")
            return None
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {e}")
            return None
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return None


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware with proper JWT validation"""
    
    async def dispatch(self, request: Request, call_next):
        logger.debug(f"Processing request: {request.method} {request.url.path}")
        
        # Define public paths that don't require authentication
        public_paths = [
            "/docs", 
            "/redoc", 
            "/openapi.json", 
            "/health", 
            "/",
            "/api/auth/signup", 
            "/api/auth/signin", 
            "/api/auth/magic-link"
        ]
        
        # Check if current path is public - use exact matching
        is_public = False
        current_path = request.url.path
        
        for public_path in public_paths:
            if current_path == public_path or current_path.startswith(public_path + "/"):
                is_public = True
                break
        
        if is_public:
            logger.debug(f"Skipping auth for public path: {current_path}")
            return await call_next(request)
        
        logger.debug(f"Authentication required for path: {current_path}")
        
        # Extract token from Authorization header
        authorization: str = request.headers.get("Authorization", "")
        logger.debug(f"Authorization header: {authorization[:50] if authorization else 'None'}...")
        
        if not authorization or not authorization.startswith("Bearer "):
            logger.debug("No valid authorization header found")
            request.state.user = None
            request.state.access_token = None
            return await call_next(request)
        
        token = authorization.split(" ")[1]
        logger.debug(f"Extracted token: {token[:50]}...")
        
        # Validate token using JWT secret
        user_data = JWTAuthService.validate_and_decode_token(token)
        
        if user_data:
            logger.debug(f"User authenticated: {user_data.get('email')}")
            request.state.user = user_data
            request.state.access_token = token
        else:
            logger.debug("Token validation failed")
            request.state.user = None
            request.state.access_token = None
        
        return await call_next(request)


def get_current_user(request: Request) -> Optional[dict]:
    """Get current authenticated user from request state"""
    user = getattr(request.state, 'user', None)
    logger.debug(f"Getting current user: {user.get('email') if user else 'None'}")
    return user


def get_access_token(request: Request) -> Optional[str]:
    """Get access token from request state"""
    return getattr(request.state, 'access_token', None)


def require_auth(request: Request) -> dict:
    """Require authentication and return user or raise exception"""
    user = get_current_user(request)
    logger.debug(f"Requiring auth - user: {user.get('email') if user else 'None'}")
    
    if not user:
        logger.warning(f"Authentication required for path: {request.url.path}")
        raise AuthenticationError("Authentication required")
    
    return user