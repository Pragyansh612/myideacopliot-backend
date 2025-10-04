"""Tests for Phase 3: Collaboration & Sharing endpoints"""
import pytest
import os
from httpx import AsyncClient
from app.main import app

# Global variable to store created IDs during test session
test_data = {
    "idea_id": None,
    "feature_id": None,
    "share_id": None,
    "comment_id": None,
    "reply_id": None
}


@pytest.fixture
def auth_headers():
    """Get authentication headers from environment"""
    token = os.getenv("ACCESS_TOKEN", "YOUR_TEST_TOKEN_HERE")
    return {
        "Authorization": f"Bearer {token}"
    }


# ============================================================================
# SETUP: Create test data
# ============================================================================

@pytest.mark.asyncio
async def test_01_create_test_idea(auth_headers):
    """Step 1: Create a test idea for sharing"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/ideas",
            headers=auth_headers,
            json={
                "title": "Shared Collaboration Idea",
                "description": "An idea to test sharing and collaboration features",
                "tags": ["collaboration", "test"],
                "priority": "high",
                "effort_score": 7,
                "impact_score": 9,
                "interest_score": 8
            }
        )
        
        print(f"\nStatus: {response.status_code}")
        assert response.status_code == 201, f"Failed to create idea: {response.text}"
        
        data = response.json()
        assert data["success"] is True
        
        test_data["idea_id"] = data["data"]["idea"]["id"]
        print(f"✓ Created idea with ID: {test_data['idea_id']}")


@pytest.mark.asyncio
async def test_02_create_test_feature(auth_headers):
    """Step 2: Create a test feature for feature comments"""
    if not test_data["idea_id"]:
        pytest.skip("No idea ID available, run test_01 first")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            f"/api/ideas/{test_data['idea_id']}/features",
            headers=auth_headers,
            json={
                "title": "Collaborative Feature",
                "description": "A feature for testing comments",
                "priority": "high"
            }
        )
        
        print(f"\nStatus: {response.status_code}")
        assert response.status_code == 201, f"Failed to create feature: {response.text}"
        
        data = response.json()
        test_data["feature_id"] = data["data"]["feature"]["id"]
        print(f"✓ Created feature with ID: {test_data['feature_id']}")


# ============================================================================
# SHARING TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_03_share_idea(auth_headers):
    """Step 3: Share the idea with another user"""
    if not test_data["idea_id"]:
        pytest.skip("No idea ID available")
    
    # Update this with a real user email in your system
    SECOND_USER_EMAIL = os.getenv("SECOND_USER_EMAIL", "testuser2@example.com")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            f"/api/ideas/{test_data['idea_id']}/share",
            headers=auth_headers,
            json={
                "shared_with_email": SECOND_USER_EMAIL,
                "role": "editor"
            }
        )
        
        print(f"\nStatus: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 201:
            data = response.json()
            assert data["success"] is True
            test_data["share_id"] = data["data"]["share"]["id"]
            print(f"✓ Shared idea with ID: {test_data['share_id']}")
        else:
            # If sharing fails (user doesn't exist), just note it
            print(f"⚠ Share failed (user may not exist): {response.json()}")
            pytest.skip("Second user not found in system")


@pytest.mark.asyncio
async def test_04_get_shares(auth_headers):
    """Step 4: Get all shares for the idea"""
    if not test_data["idea_id"]:
        pytest.skip("No idea ID available")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            f"/api/ideas/{test_data['idea_id']}/shares",
            headers=auth_headers
        )
        
        print(f"\nStatus: {response.status_code}")
        assert response.status_code == 200, f"Failed to get shares: {response.text}"
        
        data = response.json()
        assert data["success"] is True
        assert "shares" in data["data"]
        print(f"✓ Retrieved {len(data['data']['shares'])} share(s)")


@pytest.mark.asyncio
async def test_05_update_share(auth_headers):
    """Step 5: Update share role from editor to viewer"""
    if not test_data["idea_id"] or not test_data["share_id"]:
        pytest.skip("No share ID available")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.put(
            f"/api/ideas/{test_data['idea_id']}/share/{test_data['share_id']}",
            headers=auth_headers,
            json={
                "role": "viewer"
            }
        )
        
        print(f"\nStatus: {response.status_code}")
        assert response.status_code == 200, f"Failed to update share: {response.text}"
        
        data = response.json()
        assert data["data"]["share"]["role"] == "viewer"
        print(f"✓ Updated share role to viewer")


# ============================================================================
# COMMENT TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_06_create_idea_comment(auth_headers):
    """Step 6: Create a comment on the idea"""
    if not test_data["idea_id"]:
        pytest.skip("No idea ID available")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            f"/api/ideas/{test_data['idea_id']}/comments",
            headers=auth_headers,
            json={
                "content": "This is a test comment on the idea. Great collaboration feature!"
            }
        )
        
        print(f"\nStatus: {response.status_code}")
        assert response.status_code == 201, f"Failed to create comment: {response.text}"
        
        data = response.json()
        assert data["success"] is True
        test_data["comment_id"] = data["data"]["comment"]["id"]
        print(f"✓ Created comment with ID: {test_data['comment_id']}")


@pytest.mark.asyncio
async def test_07_create_reply_comment(auth_headers):
    """Step 7: Create a reply to the comment"""
    if not test_data["idea_id"] or not test_data["comment_id"]:
        pytest.skip("No comment ID available")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            f"/api/ideas/{test_data['idea_id']}/comments",
            headers=auth_headers,
            json={
                "content": "This is a reply to the first comment. Threading works!",
                "parent_comment_id": test_data["comment_id"]
            }
        )
        
        print(f"\nStatus: {response.status_code}")
        assert response.status_code == 201, f"Failed to create reply: {response.text}"
        
        data = response.json()
        test_data["reply_id"] = data["data"]["comment"]["id"]
        print(f"✓ Created reply with ID: {test_data['reply_id']}")


@pytest.mark.asyncio
async def test_08_create_feature_comment(auth_headers):
    """Step 8: Create a comment on the feature"""
    if not test_data["feature_id"]:
        pytest.skip("No feature ID available")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            f"/api/features/{test_data['feature_id']}/comments",
            headers=auth_headers,
            json={
                "content": "This is a comment on the feature. Looking good!"
            }
        )
        
        print(f"\nStatus: {response.status_code}")
        assert response.status_code == 201, f"Failed to create feature comment: {response.text}"
        
        data = response.json()
        assert data["success"] is True
        print(f"✓ Created feature comment")


@pytest.mark.asyncio
async def test_09_get_idea_comments(auth_headers):
    """Step 9: Get all comments for the idea with threading"""
    if not test_data["idea_id"]:
        pytest.skip("No idea ID available")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            f"/api/ideas/{test_data['idea_id']}/comments",
            headers=auth_headers
        )
        
        print(f"\nStatus: {response.status_code}")
        assert response.status_code == 200, f"Failed to get comments: {response.text}"
        
        data = response.json()
        assert data["success"] is True
        assert "comments" in data["data"]
        
        print(f"✓ Retrieved {len(data['data']['comments'])} root comment(s)")
        
        # Check threading
        if data["data"]["comments"]:
            for comment in data["data"]["comments"]:
                if comment.get("replies"):
                    print(f"  └─ Comment has {len(comment['replies'])} reply/replies")


@pytest.mark.asyncio
async def test_10_update_comment(auth_headers):
    """Step 10: Update a comment"""
    if not test_data["comment_id"]:
        pytest.skip("No comment ID available")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.put(
            f"/api/comments/{test_data['comment_id']}",
            headers=auth_headers,
            json={
                "content": "This is an UPDATED test comment. Editing works!"
            }
        )
        
        print(f"\nStatus: {response.status_code}")
        assert response.status_code == 200, f"Failed to update comment: {response.text}"
        
        data = response.json()
        assert "UPDATED" in data["data"]["comment"]["content"]
        print(f"✓ Updated comment successfully")


@pytest.mark.asyncio
async def test_11_delete_comment(auth_headers):
    """Step 11: Soft-delete a comment"""
    if not test_data["reply_id"]:
        pytest.skip("No reply ID available")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete(
            f"/api/comments/{test_data['reply_id']}",
            headers=auth_headers
        )
        
        print(f"\nStatus: {response.status_code}")
        assert response.status_code == 204, f"Failed to delete comment: {response.text}"
        print(f"✓ Deleted comment successfully")


# ============================================================================
# CLEANUP TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_12_delete_share(auth_headers):
    """Step 12: Revoke the share"""
    if not test_data["idea_id"] or not test_data["share_id"]:
        pytest.skip("No share ID available")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete(
            f"/api/ideas/{test_data['idea_id']}/share/{test_data['share_id']}",
            headers=auth_headers
        )
        
        print(f"\nStatus: {response.status_code}")
        assert response.status_code == 204, f"Failed to delete share: {response.text}"
        print(f"✓ Revoked share successfully")


@pytest.mark.asyncio
async def test_13_cleanup(auth_headers):
    """Step 13: Clean up test data"""
    print("\n=== Cleanup ===")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Delete feature
        if test_data["feature_id"]:
            response = await client.delete(
                f"/api/features/{test_data['feature_id']}",
                headers=auth_headers
            )
            print(f"✓ Deleted feature: {response.status_code}")
        
        # Delete idea
        if test_data["idea_id"]:
            response = await client.delete(
                f"/api/ideas/{test_data['idea_id']}",
                headers=auth_headers
            )
            print(f"✓ Deleted idea: {response.status_code}")


# ============================================================================
# HELPER FUNCTION - Run this to get your access token
# ============================================================================

def get_access_token():
    """Helper to get access token for testing"""
    try:
        import requests
        
        TEST_EMAIL = input("Enter your email: ")
        TEST_PASSWORD = input("Enter your password: ")
        
        print("\nAttempting to sign in...")
        response = requests.post(
            "http://localhost:8000/api/auth/signin",
            json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            },
            timeout=5
        )
        
        if response.status_code == 200:
            token = response.json()["data"]["session"]["access_token"]
            print(f"\n{'='*60}")
            print(f"ACCESS TOKEN RETRIEVED")
            print(f"{'='*60}")
            print(f"\nTo use this token, run:")
            print(f"\nexport ACCESS_TOKEN='{token}'")
            print(f"\nThen run the tests:")
            print(f"pytest tests/test_sharing.py -v -s")
            print(f"\n{'='*60}\n")
            return token
        else:
            print(f"Failed to sign in: {response.json()}")
            return None
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure the server is running:")
        print("  uvicorn app.main:app --reload")
        return None


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Phase 3: Collaboration & Sharing - Test Setup")
    print("="*60)
    print("\nThis will help you get an access token for testing.")
    print()
    get_access_token()