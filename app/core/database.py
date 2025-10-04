"""Database configuration and Supabase client"""
from supabase import create_client, Client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Service role client for admin operations
supabase_client: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_ROLE_KEY
)

# Admin client alias (same as service role client)
supabase_admin: Client = supabase_client

# Anon client for user operations
supabase_anon_client: Client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_ANON_KEY
)


def get_authenticated_client(access_token: str) -> Client:
    """Get Supabase client with user authentication"""
    if not access_token:
        return supabase_anon_client
    
    # Create client with user's access token
    client = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_ANON_KEY
    )
    
    # Set the auth token for RLS
    client.postgrest.auth(access_token)
    
    return client