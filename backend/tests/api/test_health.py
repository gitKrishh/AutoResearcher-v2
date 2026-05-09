"""Tests for GET /api/health endpoint."""


async def test_health_returns_200(async_client):
    """Health endpoint should return HTTP 200."""
    response = await async_client.get("/api/health")
    assert response.status_code == 200


async def test_health_response_structure(async_client):
    """Health response should have correct JSON structure."""
    response = await async_client.get("/api/health")
    data = response.json()

    assert data["success"] is True
    assert data["data"]["status"] == "healthy"
    assert data["error"] is None
