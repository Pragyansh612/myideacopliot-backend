#!/usr/bin/env python3
"""
Standalone script to export access token for API testing
Run this with: python export_token.py
"""

import requests
import sys

# Test credentials
TEST_EMAIL = "pragy@gmail.com"
TEST_PASSWORD = "test123456"
API_URL = "http://localhost:8000"


def get_access_token():
    """Get access token from the API"""
    try:
        print("Attempting to authenticate...")
        response = requests.post(
            f"{API_URL}/api/auth/signin",
            json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            },
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data["data"]["session"]["access_token"]
            return token
        else:
            print(f"Authentication failed: {response.json()}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("\nERROR: Cannot connect to server at", API_URL)
        print("\nMake sure the server is running:")
        print("  uvicorn app.main:app --reload")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def main():
    print("=" * 70)
    print("ACCESS TOKEN EXPORT UTILITY")
    print("=" * 70)
    print()
    
    token = get_access_token()
    
    if token:
        print("\n✓ Authentication successful!")
        print("\n" + "=" * 70)
        print("EXPORT COMMAND")
        print("=" * 70)
        print(f"\nexport ACCESS_TOKEN='{token}'")
        print("\n" + "=" * 70)
        print("USAGE EXAMPLES")
        print("=" * 70)
        print("\n# Get user profile:")
        print('curl -H "Authorization: Bearer $ACCESS_TOKEN" http://localhost:8000/api/profile')
        print("\n# Get user settings:")
        print('curl -H "Authorization: Bearer $ACCESS_TOKEN" http://localhost:8000/api/settings')
        print("\n# Get user stats:")
        print('curl -H "Authorization: Bearer $ACCESS_TOKEN" http://localhost:8000/api/stats')
        print("\n# Get current user:")
        print('curl -H "Authorization: Bearer $ACCESS_TOKEN" http://localhost:8000/api/auth/me')
        print("\n" + "=" * 70)
        print("\nTo use in pytest fixtures, add this to your test file:")
        print("=" * 70)
        print(f'\nACCESS_TOKEN = "{token}"')
        print("\n" + "=" * 70)
        return 0
    else:
        print("\n✗ Failed to get access token")
        print("\nTroubleshooting:")
        print("1. Make sure the server is running: uvicorn app.main:app --reload")
        print("2. Verify the credentials are correct")
        print("3. Check the server logs for errors")
        return 1


if __name__ == "__main__":
    sys.exit(main())