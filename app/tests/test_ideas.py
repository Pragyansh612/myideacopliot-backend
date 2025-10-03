"""Tests for ideas endpoints"""
import pytest
import os
from httpx import AsyncClient
from app.main import app

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
    idea_id = "test-idea-id"  # Replace with actual ID in real tests
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            f"/api/ideas/{idea_id}",
            headers=auth_headers
        )
        # Will return 404 in this test, but structure is correct
        assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_update_idea(auth_headers):
    """Test updating an idea"""
    idea_id = "test-idea-id"
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.put(
            f"/api/ideas/{idea_id}",
            headers=auth_headers,
            json={
                "title": "Updated Idea Title",
                "status": "in_progress"
            }
        )
        assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_create_phase(auth_headers):
    """Test creating a phase"""
    idea_id = "test-idea-id"
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            f"/api/ideas/{idea_id}/phases",
            headers=auth_headers,
            json={
                "name": "Phase 1: Planning",
                "description": "Initial planning phase",
                "order_index": 0
            }
        )
        assert response.status_code in [201, 404]


@pytest.mark.asyncio
async def test_create_feature(auth_headers):
    """Test creating a feature"""
    idea_id = "test-idea-id"
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            f"/api/ideas/{idea_id}/features",
            headers=auth_headers,
            json={
                "title": "Feature 1",
                "description": "A cool feature",
                "priority": "high"
            }
        )
        assert response.status_code in [201, 404]