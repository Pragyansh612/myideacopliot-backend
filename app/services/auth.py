"""Authentication service"""
from typing import Dict, Any, Optional
from app.core.database import supabase_client, supabase_admin
from app.utils.exceptions import AuthenticationError, ValidationError


class AuthService:
    """Authentication service for user management"""
    
    @staticmethod
    async def sign_up_with_email(email: str, password: str, user_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Sign up a new user with email and password
        
        Args:
            email: User's email address
            password: User's password
            user_data: Additional user data for profile
            
        Returns:
            User data and session information
            
        Raises:
            ValidationError: If sign up fails
        """
        try:
            response = supabase_client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_data or {}
                }
            })
            
            if response.user:
                return {
                    "user": response.user.dict(),
                    "session": response.session.dict() if response.session else None
                }
            else:
                raise ValidationError("Failed to create user account")
                
        except Exception as e:
            raise ValidationError(f"Sign up failed: {str(e)}")
    
    @staticmethod
    async def sign_in_with_email(email: str, password: str) -> Dict[str, Any]:
        """
        Sign in user with email and password
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            User data and session information
            
        Raises:
            AuthenticationError: If sign in fails
        """
        try:
            response = supabase_client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user and response.session:
                return {
                    "user": response.user.dict(),
                    "session": response.session.dict()
                }
            else:
                raise AuthenticationError("Invalid email or password")
                
        except Exception as e:
            raise AuthenticationError(f"Sign in failed: {str(e)}")
    
    @staticmethod
    async def sign_in_with_magic_link(email: str, redirect_to: Optional[str] = None) -> Dict[str, Any]:
        """
        Send magic link for passwordless sign in
        
        Args:
            email: User's email address
            redirect_to: URL to redirect to after sign in
            
        Returns:
            Success message
            
        Raises:
            ValidationError: If sending magic link fails
        """
        try:
            response = supabase_client.auth.sign_in_with_otp({
                "email": email,
                "options": {
                    "email_redirect_to": redirect_to
                } if redirect_to else {}
            })
            
            return {"message": "Magic link sent to your email"}
            
        except Exception as e:
            raise ValidationError(f"Failed to send magic link: {str(e)}")
    
    @staticmethod
    async def sign_out(access_token: str) -> Dict[str, Any]:
        """
        Sign out user and invalidate session
        
        Args:
            access_token: User's access token
            
        Returns:
            Success message
        """
        try:
            # Set the session
            supabase_client.auth.set_session(access_token, "")
            # Sign out
            supabase_client.auth.sign_out()
            
            return {"message": "Successfully signed out"}
            
        except Exception as e:
            # Don't raise error for sign out - just log it
            return {"message": "Sign out completed"}
    
    @staticmethod
    async def refresh_token(refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token: User's refresh token
            
        Returns:
            New session data
            
        Raises:
            AuthenticationError: If refresh fails
        """
        try:
            response = supabase_client.auth.refresh_session(refresh_token)
            
            if response.session:
                return {
                    "session": response.session.dict()
                }
            else:
                raise AuthenticationError("Failed to refresh token")
                
        except Exception as e:
            raise AuthenticationError(f"Token refresh failed: {str(e)}")