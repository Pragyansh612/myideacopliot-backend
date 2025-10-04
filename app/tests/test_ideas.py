"""Tests for ideas endpoints"""
import pytest
import os
from httpx import AsyncClient
from app.main import app

# Global variable to store created IDs during test session
test_data = {
    "category_id": None,
    "idea_id": None,
    "phase_id": None,
    "feature_id": None
}


@pytest.fixture
def auth_headers():
    """Get authentication headers from environment"""
    token = os.getenv("ACCESS_TOKEN", "YOUR_TEST_TOKEN_HERE")
    return {
        "Authorization": f"Bearer {token}"
    }


@pytest.mark.asyncio
async def test_create_category(auth_headers):
    """Test creating a category"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/categories",
            headers=auth_headers,
            json={
                "name": "Test Category",
                "color": "#FF5733",
                "description": "A test category"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "category" in data["data"]
        
        # Store category ID for later tests
        test_data["category_id"] = data["data"]["category"]["id"]
        print(f"Created category ID: {test_data['category_id']}")


@pytest.mark.asyncio
async def test_get_categories(auth_headers):
    """Test getting categories"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/categories",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "categories" in data["data"]


@pytest.mark.asyncio
async def test_create_idea(auth_headers):
    """Test creating an idea"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/ideas",
            headers=auth_headers,
            json={
                "title": "Test Idea",
                "description": "A brilliant test idea",
                "tags": ["test", "demo"],
                "priority": "high",
                "effort_score": 5,
                "impact_score": 8,
                "interest_score": 9
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "idea" in data["data"]
        
        # Store idea ID for later tests
        test_data["idea_id"] = data["data"]["idea"]["id"]
        print(f"Created idea ID: {test_data['idea_id']}")


@pytest.mark.asyncio
async def test_get_ideas_with_filters(auth_headers):
    """Test getting ideas with filters"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/ideas?priority=high&sort_by=overall_score&limit=10",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "ideas" in data["data"]
        assert "total" in data["data"]


@pytest.mark.asyncio
async def test_get_idea_by_id(auth_headers):
    """Test getting a specific idea"""
    # Skip if no idea was created
    if not test_data["idea_id"]:
        pytest.skip("No idea ID available, create idea first")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            f"/api/ideas/{test_data['idea_id']}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "idea" in data["data"]


@pytest.mark.asyncio
async def test_update_idea(auth_headers):
    """Test updating an idea"""
    # Skip if no idea was created
    if not test_data["idea_id"]:
        pytest.skip("No idea ID available, create idea first")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.put(
            f"/api/ideas/{test_data['idea_id']}",
            headers=auth_headers,
            json={
                "title": "Updated Idea Title",
                "status": "in_progress"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["idea"]["title"] == "Updated Idea Title"


@pytest.mark.asyncio
async def test_create_phase(auth_headers):
    """Test creating a phase"""
    # Skip if no idea was created
    if not test_data["idea_id"]:
        pytest.skip("No idea ID available, create idea first")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            f"/api/ideas/{test_data['idea_id']}/phases",
            headers=auth_headers,
            json={
                "name": "Phase 1: Planning",
                "description": "Initial planning phase",
                "order_index": 0
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "phase" in data["data"]
        
        # Store phase ID for later tests
        test_data["phase_id"] = data["data"]["phase"]["id"]
        print(f"Created phase ID: {test_data['phase_id']}")


@pytest.mark.asyncio
async def test_create_feature(auth_headers):
    """Test creating a feature"""
    # Skip if no idea was created
    if not test_data["idea_id"]:
        pytest.skip("No idea ID available, create idea first")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            f"/api/ideas/{test_data['idea_id']}/features",
            headers=auth_headers,
            json={
                "title": "Feature 1",
                "description": "A cool feature",
                "priority": "high"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "feature" in data["data"]
        
        # Store feature ID for later tests
        test_data["feature_id"] = data["data"]["feature"]["id"]
        print(f"Created feature ID: {test_data['feature_id']}")


@pytest.mark.asyncio
async def test_get_phases(auth_headers):
    """Test getting phases for an idea"""
    if not test_data["idea_id"]:
        pytest.skip("No idea ID available")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            f"/api/ideas/{test_data['idea_id']}/phases",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "phases" in data["data"]


@pytest.mark.asyncio
async def test_get_features(auth_headers):
    """Test getting features for an idea"""
    if not test_data["idea_id"]:
        pytest.skip("No idea ID available")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            f"/api/ideas/{test_data['idea_id']}/features",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "features" in data["data"]


@pytest.mark.asyncio
async def test_update_feature(auth_headers):
    """Test updating a feature"""
    if not test_data["feature_id"]:
        pytest.skip("No feature ID available")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.put(
            f"/api/features/{test_data['feature_id']}",
            headers=auth_headers,
            json={
                "title": "Updated Feature",
                "is_completed": True
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


@pytest.mark.asyncio
async def test_delete_feature(auth_headers):
    """Test deleting a feature"""
    if not test_data["feature_id"]:
        pytest.skip("No feature ID available")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete(
            f"/api/features/{test_data['feature_id']}",
            headers=auth_headers
        )
        assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_phase(auth_headers):
    """Test deleting a phase"""
    if not test_data["phase_id"]:
        pytest.skip("No phase ID available")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete(
            f"/api/phases/{test_data['phase_id']}",
            headers=auth_headers
        )
        assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_idea(auth_headers):
    """Test deleting an idea"""
    if not test_data["idea_id"]:
        pytest.skip("No idea ID available")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete(
            f"/api/ideas/{test_data['idea_id']}",
            headers=auth_headers
        )
        assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_category(auth_headers):
    """Test deleting a category"""
    if not test_data["category_id"]:
        pytest.skip("No category ID available")
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete(
            f"/api/categories/{test_data['category_id']}",
            headers=auth_headers
        )
        assert response.status_code == 204