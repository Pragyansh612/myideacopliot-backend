"""Authentication router with proper JWT handling"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, Body
from fastapi.responses import JSONResponse
from app.services.auth import AuthService
from app.schemas.response import SuccessResponse, ErrorResponse
from app.utils.exceptions import AuthenticationError, ValidationError
from app.middleware.auth import require_auth, get_current_user, get_access_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/signup", response_model=SuccessResponse, summary="Sign up with email and password")
async def sign_up(
    email: str = Body(..., description="User's email address"),
    password: str = Body(..., description="User's password", min_length=6),
    display_name: Optional[str] = Body(None, description="User's display name")
):
    """
    Create a new user account with email and password.
    
    After successful registration, the user will receive a confirmation email.
    """
    try:
        user_data = {"display_name": display_name} if display_name else None
        result = await AuthService.sign_up_with_email(email, password, user_data)
        
        return SuccessResponse(
            message="Account created successfully. Please check your email for confirmation.",
            data=result
        )
    except ValidationError as e:
        return JSONResponse(
            status_code=e.status_code,
            content=ErrorResponse(message=str(e.detail)).dict()
        )
    except Exception as e:
        print(f"Signup error: {e}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(message="Internal server error during signup").dict()
        )

@router.post("/signin", response_model=SuccessResponse, summary="Sign in with email and password")
async def sign_in(
    email: str = Body(..., description="User's email address"),
    password: str = Body(..., description="User's password")
):
    """
    Sign in with email and password.
    
    Returns access token and refresh token for authenticated requests.
    """
    try:
        result = await AuthService.sign_in_with_email(email, password)
        
        return SuccessResponse(
            message="Successfully signed in",
            data=result
        )
    except AuthenticationError as e:
        return JSONResponse(
            status_code=e.status_code,
            content=ErrorResponse(message=str(e.detail)).dict()
        )
    except Exception as e:
        print(f"Signin error: {e}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(message="Internal server error during signin").dict()
        )

@router.post("/magic-link", response_model=SuccessResponse, summary="Send magic link for passwordless login")
async def send_magic_link(
    email: str = Body(..., description="User's email address"),
    redirect_to: Optional[str] = Body(None, description="URL to redirect after sign in")
):
    """
    Send a magic link to the user's email for passwordless authentication.
    """
    try:
        result = await AuthService.sign_in_with_magic_link(email, redirect_to)
        
        return SuccessResponse(
            message="Magic link sent successfully",
            data=result
        )
    except ValidationError as e:
        return JSONResponse(
            status_code=e.status_code,
            content=ErrorResponse(message=str(e.detail)).dict()
        )
    except Exception as e:
        print(f"Magic link error: {e}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(message="Internal server error sending magic link").dict()
        )

@router.post("/signout", response_model=SuccessResponse, summary="Sign out current user")
async def sign_out(request: Request):
    """
    Sign out the current user and invalidate their session.
    """
    try:
        # Get the access token from the request state (set by middleware)
        access_token = get_access_token(request)
        if not access_token:
            # If no token in state, try to extract from header directly
            authorization: str = request.headers.get("Authorization", "")
            access_token = authorization.replace("Bearer ", "") if authorization.startswith("Bearer ") else ""
        
        result = await AuthService.sign_out(access_token)
        
        return SuccessResponse(
            message="Successfully signed out",
            data=result
        )
    except Exception as e:
        print(f"Signout error: {e}")
        # Don't fail signout - always return success
        return SuccessResponse(
            message="Successfully signed out"
        )

@router.post("/refresh", response_model=SuccessResponse, summary="Refresh access token")
async def refresh_token(
    refresh_token: str = Body(..., description="Refresh token")
):
    """
    Refresh the access token using a valid refresh token.
    """
    try:
        result = await AuthService.refresh_token(refresh_token)
        
        return SuccessResponse(
            message="Token refreshed successfully",
            data=result
        )
    except AuthenticationError as e:
        return JSONResponse(
            status_code=e.status_code,
            content=ErrorResponse(message=str(e.detail)).dict()
        )
    except Exception as e:
        print(f"Token refresh error: {e}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(message="Internal server error during token refresh").dict()
        )

@router.get("/me", response_model=SuccessResponse, summary="Get current user info")
async def get_current_user_info(request: Request):
    """
    Get information about the currently authenticated user.
    
    Requires valid authentication token in Authorization header.
    """
    try:
        # Use require_auth to validate token and get user
        user = require_auth(request)
        
        # Format user data for response
        user_data = {
            "id": user.get("id"),
            "email": user.get("email"),
            "phone": user.get("phone", ""),
            "app_metadata": user.get("app_metadata", {}),
            "user_metadata": user.get("user_metadata", {}),
            "role": user.get("role"),
            "is_anonymous": user.get("is_anonymous", False),
            "session_id": user.get("session_id")
        }
        
        return SuccessResponse(
            message="User info retrieved successfully",
            data={"user": user_data}
        )
    except AuthenticationError as e:
        print(f"Auth error in /me: {e}")
        return JSONResponse(
            status_code=e.status_code,
            content=ErrorResponse(message=str(e.detail)).dict()
        )
    except Exception as e:
        print(f"Error in /me endpoint: {e}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(message="Failed to get user info").dict()
        )