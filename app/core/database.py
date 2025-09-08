"""Database connection and utilities"""
from supabase import create_client, Client
from app.core.config import settings

def get_supabase_client(use_service_role: bool = False) -> Client:
    """
    Create and return a Supabase client instance
    
    Args:
        use_service_role: If True, use service role key (bypasses RLS)
    
    Returns:
        Supabase client instance
    """
    key = settings.SUPABASE_SERVICE_ROLE_KEY if use_service_role else settings.SUPABASE_ANON_KEY
    return create_client(settings.SUPABASE_URL, key)

def get_authenticated_client(access_token: str) -> Client:
    """
    Create a Supabase client with an authenticated session
    
    Args:
        access_token: JWT access token
    
    Returns:
        Authenticated Supabase client instance
    """
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    
    # Set the session with the access token
    # Note: This is a workaround since we don't have the refresh token
    # The client will use this token for authenticated requests
    client.options.headers["Authorization"] = f"Bearer {access_token}"
    
    return client

# Default client instances
supabase_client = get_supabase_client()
supabase_admin = get_supabase_client(use_service_role=True)