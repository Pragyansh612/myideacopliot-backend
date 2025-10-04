"""Tests for AI Assistance & Competitor Research"""
import pytest
import os
from httpx import AsyncClient
from app.main import app

# Global variable to store test data
test_data = {
    "idea_id": None,
    "suggestion_id": None,
    "research_id": None
}


@pytest.fixture
def auth_headers():
    """Get authentication headers from environment"""
    token = os.getenv("ACCESS_TOKEN", "YOUR_TEST_TOKEN_HERE")
    return {
        "Authorization": f"Bearer {token}"
    }


# ============================================================================
# SETUP: Create test idea
# ============================================================================

@pytest.mark.asyncio
async def test_01_create_test_idea(auth_headers):
    """Step 1: Create a test idea for AI suggestions"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/ideas",
            headers=auth_headers,
            json={
                "title": "AI-Powered Task Manager",
                "description": "A smart task management app that uses AI to prioritize tasks, suggest optimal schedules, and provide productivity insights",
                "tags": ["productivity", "ai", "automation"],
                "priority": "high",
                "effort_score": 8,
                "impact_score": 9,
                "interest_score": 9
            }
        )
        
        print(f"\nStatus: {response.status_code}")
        assert response.status_code == 201, f"Failed to create idea: {response.text}"
        
        data = response.json()
        test_data["idea_id"] = data["data"]["idea"]["id"]
        print(f"✓ Created idea with ID: {test_data['idea_id']}")


# ============================================================================
# AI SUGGESTIONS TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_02_generate_feature_suggestions(auth_headers):
    """Step 2: Generate AI feature suggestions"""
    if not test_data["idea_id"]:
        pytest.skip("No idea ID available")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/ai/suggest",
            headers=auth_headers,
            json={
                "idea_id": test_data["idea_id"],
                "suggestion_type": "features",
                "context": "Focus on mobile-first experience and integration with calendar apps"
            }
        )
        
        print(f"\nStatus: {response.status_code}")
        print(f"Response: {response.json()}")
        
        assert response.status_code == 200, f"Failed to generate suggestions: {response.text}"
        
        data = response.json()
        assert data["success"] is True
        test_data["suggestion_id"] = data["data"]["suggestion"]["id"]
        print(f"✓ Generated feature suggestions with ID: {test_data['suggestion_id']}")
        
        # Print sample of suggestions
        content = data["data"]["suggestion"].get("content")
        if isinstance(content, str):
            print(f"  Content preview: {content[:200]}...")
        else:
            print(f"  Generated {len(content) if isinstance(content, list) else 'N/A'} suggestions")


@pytest.mark.asyncio
async def test_03_generate_marketing_suggestions(auth_headers):
    """Step 3: Generate marketing strategy suggestions"""
    if not test_data["idea_id"]:
        pytest.skip("No idea ID available")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/ai/suggest",
            headers=auth_headers,
            json={
                "idea_id": test_data["idea_id"],
                "suggestion_type": "marketing",
                "context": "Target audience is busy professionals aged 25-45"
            }
        )
        
        print(f"\nStatus: {response.status_code}")
        assert response.status_code == 200, f"Failed to generate marketing: {response.text}"
        
        data = response.json()
        print(f"✓ Generated marketing strategy")


@pytest.mark.asyncio
async def test_04_generate_validation_suggestions(auth_headers):
    """Step 4: Generate market validation suggestions"""
    if not test_data["idea_id"]:
        pytest.skip("No idea ID available")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/ai/suggest",
            headers=auth_headers,
            json={
                "idea_id": test_data["idea_id"],
                "suggestion_type": "validation"
            }
        )
        
        print(f"\nStatus: {response.status_code}")
        assert response.status_code == 200, f"Failed to generate validation: {response.text}"
        
        data = response.json()
        print(f"✓ Generated validation insights")


@pytest.mark.asyncio
async def test_05_get_all_suggestions(auth_headers):
    """Step 5: Get all suggestions for the idea"""
    if not test_data["idea_id"]:
        pytest.skip("No idea ID available")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            f"/api/ai/suggestions/{test_data['idea_id']}",
            headers=auth_headers
        )
        
        print(f"\nStatus: {response.status_code}")
        assert response.status_code == 200, f"Failed to get suggestions: {response.text}"
        
        data = response.json()
        assert data["success"] is True
        print(f"✓ Retrieved {data['data']['total']} suggestion(s)")
        
        # Show suggestion types
        for suggestion in data["data"]["suggestions"]:
            print(f"  - {suggestion['suggestion_type']}: {suggestion.get('title', 'Untitled')}")


@pytest.mark.asyncio
async def test_06_get_query_logs(auth_headers):
    """Step 6: Get AI query logs"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/ai/logs",
            headers=auth_headers,
            params={"limit": 10}
        )
        
        print(f"\nStatus: {response.status_code}")
        assert response.status_code == 200, f"Failed to get logs: {response.text}"
        
        data = response.json()
        assert data["success"] is True
        print(f"✓ Retrieved {data['data']['total']} query log(s)")
        
        # Show recent queries
        for log in data["data"]["logs"][:3]:
            print(f"  - {log['query_type']} (Model: {log.get('ai_model', 'N/A')}, "
                  f"Time: {log.get('response_time_ms', 'N/A')}ms)")


# ============================================================================
# COMPETITOR RESEARCH TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_07_scrape_competitors_basic(auth_headers):
    """Step 7: Scrape competitor websites without analysis"""
    if not test_data["idea_id"]:
        pytest.skip("No idea ID available")
    
    async with AsyncClient(app=app, base_url="http://test", timeout=60.0) as client:
        response = await client.post(
            "/api/competitor/scrape",
            headers=auth_headers,
            json={
                "idea_id": test_data["idea_id"],
                "urls": ["https://keytake.vercel.app/"],
                "analyze": False
            }
        )
        
        print(f"\nStatus: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            print(f"✓ Scraped {data['data']['total']} website(s)")
        else:
            print(f"⚠ Scraping returned status {response.status_code}")
            pytest.skip("Scraping service may be unavailable")


@pytest.mark.asyncio
async def test_08_scrape_and_analyze_competitors(auth_headers):
    """Step 8: Scrape and analyze competitor websites with AI"""
    if not test_data["idea_id"]:
        pytest.skip("No idea ID available")
    
    async with AsyncClient(app=app, base_url="http://test", timeout=120.0) as client:
        response = await client.post(
            "/api/competitor/scrape",
            headers=auth_headers,
            json={
                "idea_id": test_data["idea_id"],
                "urls": [
                    "https://keytake.vercel.app/",
                    "https://websyncai.vercel.app/"
                ],
                "analyze": True
            }
        )
        
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            
            if data["data"]["research"]:
                test_data["research_id"] = data["data"]["research"][0]["id"]
                print(f"✓ Scraped and analyzed {data['data']['total']} competitor(s)")
                
                # Show analysis summary
                for research in data["data"]["research"]:
                    print(f"\n  Competitor: {research['competitor_name']}")
                    print(f"  Market Position: {research.get('market_position', 'N/A')}")
                    print(f"  Strengths: {len(research.get('strengths', []))} identified")
                    print(f"  Weaknesses: {len(research.get('weaknesses', []))} identified")
                    print(f"  Opportunities: {len(research.get('differentiation_opportunities', []))} identified")
            else:
                print(f"⚠ No research data returned")
        else:
            print(f"⚠ Analysis returned status {response.status_code}: {response.text}")
            pytest.skip("AI analysis may be unavailable")


@pytest.mark.asyncio
async def test_09_get_competitor_research(auth_headers):
    """Step 9: Get all competitor research for the idea"""
    if not test_data["idea_id"]:
        pytest.skip("No idea ID available")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            f"/api/competitor/{test_data['idea_id']}",
            headers=auth_headers
        )
        
        print(f"\nStatus: {response.status_code}")
        assert response.status_code == 200, f"Failed to get research: {response.text}"
        
        data = response.json()
        assert data["success"] is True
        print(f"✓ Retrieved {data['data']['total']} research record(s)")
        
        # Show detailed analysis
        for research in data["data"]["research"]:
            print(f"\n{'='*60}")
            print(f"Competitor: {research['competitor_name']}")
            print(f"URL: {research.get('competitor_url', 'N/A')}")
            print(f"{'='*60}")
            
            if research.get('description'):
                print(f"\nDescription:\n{research['description']}")
            
            if research.get('strengths'):
                print(f"\nStrengths:")
                for strength in research['strengths'][:3]:
                    print(f"  • {strength}")
            
            if research.get('weaknesses'):
                print(f"\nWeaknesses:")
                for weakness in research['weaknesses'][:3]:
                    print(f"  • {weakness}")
            
            if research.get('differentiation_opportunities'):
                print(f"\nDifferentiation Opportunities:")
                for opp in research['differentiation_opportunities'][:3]:
                    print(f"  • {opp}")
            
            print(f"\nConfidence Score: {research.get('confidence_score', 'N/A')}")


# ============================================================================
# EDGE CASES & ERROR HANDLING
# ============================================================================

@pytest.mark.asyncio
async def test_10_invalid_suggestion_type(auth_headers):
    """Step 10: Test invalid suggestion type"""
    if not test_data["idea_id"]:
        pytest.skip("No idea ID available")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/ai/suggest",
            headers=auth_headers,
            json={
                "idea_id": test_data["idea_id"],
                "suggestion_type": "invalid_type"
            }
        )
        
        print(f"\nStatus: {response.status_code}")
        assert response.status_code in [400, 422], "Should reject invalid suggestion type"
        print(f"✓ Correctly rejected invalid suggestion type")


@pytest.mark.asyncio
async def test_11_invalid_idea_id(auth_headers):
    """Step 11: Test with non-existent idea ID"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/ai/suggest",
            headers=auth_headers,
            json={
                "idea_id": "00000000-0000-0000-0000-000000000000",
                "suggestion_type": "features"
            }
        )
        
        print(f"\nStatus: {response.status_code}")
        assert response.status_code in [400, 422, 404], "Should reject invalid idea ID"
        print(f"✓ Correctly rejected invalid idea ID")


@pytest.mark.asyncio
async def test_12_invalid_url(auth_headers):
    """Step 12: Test scraping with invalid URL"""
    if not test_data["idea_id"]:
        pytest.skip("No idea ID available")
    
    async with AsyncClient(app=app, base_url="http://test", timeout=30.0) as client:
        response = await client.post(
            "/api/competitor/scrape",
            headers=auth_headers,
            json={
                "idea_id": test_data["idea_id"],
                "urls": ["https://this-site-definitely-does-not-exist-12345.com/"],
                "analyze": False
            }
        )
        
        print(f"\nStatus: {response.status_code}")
        # Should still return 200 but with error in research data
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Handled invalid URL gracefully")
        else:
            print(f"⚠ Returned status {response.status_code}")


# ============================================================================
# CLEANUP
# ============================================================================

@pytest.mark.asyncio
async def test_13_cleanup(auth_headers):
    """Step 13: Clean up test data"""
    print("\n=== Cleanup ===")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Delete idea (cascade will handle suggestions and research)
        if test_data["idea_id"]:
            response = await client.delete(
                f"/api/ideas/{test_data['idea_id']}",
                headers=auth_headers
            )
            print(f"✓ Deleted idea: {response.status_code}")


# ============================================================================
# HELPER FUNCTION - Get access token
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
            print(f"pytest app/tests/test_phase4.py -v -s")
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
    print("Phase 4: AI Assistance & Competitor Research - Test Setup")
    print("="*60)
    print("\nThis will help you get an access token for testing.")
    print()
    get_access_token()

