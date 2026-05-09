"""Tests for POST /api/search route."""

from unittest.mock import patch, AsyncMock

from app.core.schemas import Paper


# Sample paper for mocking
MOCK_PAPERS = [
    Paper(
        id="2303.08774",
        title="GPT-4 Technical Report",
        abstract="We report the development of GPT-4.",
        authors=["OpenAI"],
        pdf_url="https://arxiv.org/pdf/2303.08774.pdf",
        published="2023-03-15",
        source="arxiv",
    ),
]


async def test_post_search_returns_200_with_paper_list(async_client):
    """POST /api/search with valid query should return 200 with papers."""
    with patch(
        "app.api.routers.search.search_arxiv",
        new_callable=AsyncMock,
        return_value=MOCK_PAPERS,
    ):
        response = await async_client.post(
            "/api/search",
            json={"query": "AI agents", "max_results": 5},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["data"]) == 1
    assert data["data"][0]["title"] == "GPT-4 Technical Report"
    assert data["meta"]["count"] == 1


async def test_post_search_returns_422_on_empty_query(async_client):
    """POST /api/search with empty query should return 422 validation error."""
    response = await async_client.post(
        "/api/search",
        json={"query": "   ", "max_results": 5},
    )
    assert response.status_code == 422
