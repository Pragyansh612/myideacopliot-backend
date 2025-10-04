"""Tests for Phase 5: Notifications, Gamification & Motivation"""
import pytest
import os
from httpx import AsyncClient
from app.main import app
from datetime import date, timedelta

# Global variable to store created IDs during test session
test_data = {
    "notification_id": None,
    "achievement_id": None
}


@pytest.fixture
def auth_headers():
    """Get authentication headers from environment"""
    token = os.getenv("ACCESS_TOKEN", "YOUR_TEST_TOKEN_HERE")
    return {
        "Authorization": f"Bearer {token}"
    }


# ============================================================================
# NOTIFICATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_01_get_initial_notifications(auth_headers):
    """Step 1: Get initial notifications"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/notifications",
            headers=auth_headers
        )
        
        print(f"\nStatus: {response.status_code}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "notifications" in data["data"]
        print(f"Total notifications: {data['data']['total']}")
        print(f"Unread: {data['data']['unread_count']}")


@pytest.mark.asyncio
async def test_02_send_motivational_notification(auth_headers):
    """Step 2: Send a motivational notification"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/notifications/motivation",
            headers=auth_headers,
            json={
                "message_type": "encouragement"
            }
        )
        
        print(f"\nStatus: {response.status_code}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "notification" in data["data"]
        
        test_data["notification_id"] = data["data"]["notification"]["id"]
        print(f"Created notification ID: {test_data['notification_id']}")
        print(f"Title: {data['data']['notification']['title']}")
        print(f"Message: {data['data']['notification']['message']}")


@pytest.mark.asyncio
async def test_03_get_unread_notifications(auth_headers):
    """Step 3: Get only unread notifications"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/notifications?unread_only=true",
            headers=auth_headers
        )
        
        print(f"\nStatus: {response.status_code}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        
        # Should have at least the one we just created
        assert len(data["data"]["notifications"]) >= 1
        print(f"Unread notifications: {len(data['data']['notifications'])}")


@pytest.mark.asyncio
async def test_04_mark_notification_read(auth_headers):
    """Step 4: Mark a notification as read"""
    if not test_data["notification_id"]:
        pytest.skip("No notification ID available")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.put(
            f"/api/notifications/{test_data['notification_id']}/read",
            headers=auth_headers
        )
        
        print(f"\nStatus: {response.status_code}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["data"]["notification"]["is_read"] is True
        print(f"Marked notification as read")


@pytest.mark.asyncio
async def test_05_delete_notification(auth_headers):
    """Step 5: Delete a notification"""
    if not test_data["notification_id"]:
        pytest.skip("No notification ID available")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete(
            f"/api/notifications/{test_data['notification_id']}",
            headers=auth_headers
        )
        
        print(f"\nStatus: {response.status_code}")
        assert response.status_code == 204
        print(f"Deleted notification successfully")


# ============================================================================
# USER STATS TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_06_get_initial_stats(auth_headers):
    """Step 6: Get initial user stats"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/stats",
            headers=auth_headers
        )
        
        print(f"\nStatus: {response.status_code}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "stats" in data["data"]
        
        stats = data["data"]["stats"]
        print(f"Current Level: {stats['current_level']}")
        print(f"Total XP: {stats['total_xp']}")
        print(f"Current Streak: {stats['current_streak']}")
        print(f"Ideas Created: {stats['ideas_created']}")


@pytest.mark.asyncio
async def test_07_award_xp(auth_headers):
    """Step 7: Award XP to user"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/stats/award-xp?xp_amount=50",
            headers=auth_headers
        )
        
        print(f"\nStatus: {response.status_code}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        
        stats = data["data"]["stats"]
        print(f"Awarded 50 XP")
        print(f"New Total XP: {stats['total_xp']}")
        print(f"New Level: {stats['current_level']}")


@pytest.mark.asyncio
async def test_08_increment_ideas_created(auth_headers):
    """Step 8: Increment ideas_created stat"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/stats/increment",
            headers=auth_headers,
            json={
                "field": "ideas_created",
                "amount": 1
            }
        )
        
        print(f"\nStatus: {response.status_code}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        
        stats = data["data"]["stats"]
        print(f"Incremented ideas_created")
        print(f"New count: {stats['ideas_created']}")


@pytest.mark.asyncio
async def test_09_update_stats_manually(auth_headers):
    """Step 9: Manually update multiple stats"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/stats/update",
            headers=auth_headers,
            json={
                "ai_suggestions_applied": 5,
                "collaborations_count": 2,
                "last_activity_date": date.today().isoformat()
            }
        )
        
        print(f"\nStatus: {response.status_code}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        
        stats = data["data"]["stats"]
        print(f"Updated stats manually")
        print(f"AI Suggestions Applied: {stats['ai_suggestions_applied']}")
        print(f"Collaborations: {stats['collaborations_count']}")


# ============================================================================
# ACHIEVEMENT TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_10_get_all_achievement_definitions(auth_headers):
    """Step 10: Get all possible achievements"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/achievements/all",
            headers=auth_headers
        )
        
        print(f"\nStatus: {response.status_code}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "achievements" in data["data"]
        
        print(f"\nAvailable achievements: {data['data']['total']}")
        for achievement in data["data"]["achievements"]:
            print(f"  - {achievement['title']}: {achievement['description']} ({achievement['xp_awarded']} XP)")


@pytest.mark.asyncio
async def test_11_get_user_achievements(auth_headers):
    """Step 11: Get user's unlocked achievements"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/achievements",
            headers=auth_headers
        )
        
        print(f"\nStatus: {response.status_code}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        
        print(f"\nUnlocked achievements: {data['data']['total']}")
        for achievement in data["data"]["achievements"]:
            print(f"  - {achievement['title']}: Unlocked on {achievement['unlocked_at']}")


@pytest.mark.asyncio
async def test_12_trigger_achievement_unlock(auth_headers):
    """Step 12: Trigger achievement by creating first idea (if not already created)"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Get current stats
        stats_response = await client.get("/api/stats", headers=auth_headers)
        stats = stats_response.json()["data"]["stats"]
        
        # If no ideas created yet, increment to trigger "first_idea" achievement
        if stats["ideas_created"] == 0:
            response = await client.post(
                "/api/stats/increment",
                headers=auth_headers,
                json={
                    "field": "ideas_created",
                    "amount": 1
                }
            )
            
            print(f"\nStatus: {response.status_code}")
            assert response.status_code == 200
            print("Triggered first idea achievement!")
            
            # Check if achievement was unlocked
            achievements_response = await client.get("/api/achievements", headers=auth_headers)
            achievements = achievements_response.json()["data"]["achievements"]
            
            first_idea = [a for a in achievements if a["achievement_type"] == "first_idea"]
            if first_idea:
                print(f"Achievement unlocked: {first_idea[0]['title']}")
        else:
            print(f"\nAlready have {stats['ideas_created']} ideas created")


# ============================================================================
# MOTIVATION & EMAIL TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_13_send_reminder_notification(auth_headers):
    """Step 13: Send reminder-type motivational notification"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/notifications/motivation",
            headers=auth_headers,
            json={
                "message_type": "reminder"
            }
        )
        
        print(f"\nStatus: {response.status_code}")
        assert response.status_code == 200
        
        data = response.json()
        print(f"Reminder sent: {data['data']['notification']['title']}")
        print(f"Message: {data['data']['notification']['message']}")


@pytest.mark.asyncio
async def test_14_send_streak_notification(auth_headers):
    """Step 14: Send streak-type motivational notification"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/notifications/motivation",
            headers=auth_headers,
            json={
                "message_type": "streak"
            }
        )
        
        print(f"\nStatus: {response.status_code}")
        assert response.status_code == 200
        
        data = response.json()
        print(f"Streak notification sent: {data['data']['notification']['title']}")


@pytest.mark.asyncio
async def test_15_test_inactivity_check(auth_headers):
    """Step 15: Test inactivity check by setting old last_activity_date"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Set last activity to 8 days ago
        old_date = (date.today() - timedelta(days=8)).isoformat()
        
        response = await client.post(
            "/api/stats/update",
            headers=auth_headers,
            json={
                "last_activity_date": old_date
            }
        )
        
        print(f"\nStatus: {response.status_code}")
        assert response.status_code == 200
        
        print(f"Set last_activity_date to {old_date}")
        print("In production, background task would send reminder email")


# ============================================================================
# HELPER FUNCTION
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
            print(f"pytest app/tests/test_phase5.py -v -s")
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
    print("Phase 5: Notifications, Gamification & Motivation - Test Setup")
    print("="*60)
    print("\nThis will help you get an access token for testing.")
    print()
    get_access_token()