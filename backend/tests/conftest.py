"""Shared pytest fixtures for all backend tests.

Provides: async HTTP client, mock LLM service, sample data.
"""

import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock

from app.main import app


@pytest.fixture
async def async_client():
    """Async HTTP client for testing FastAPI routes.

    Usage:
        async def test_something(async_client):
            response = await async_client.get("/api/health")
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_llm_service():
    """Mock LLM service for testing agents without real API calls.

    Returns an AsyncMock with pre-configured return values.
    """
    service = AsyncMock()
    service.complete.return_value = "Mock LLM response"
    service.complete_json.return_value = {"summary": "Mock summary"}
    return service
