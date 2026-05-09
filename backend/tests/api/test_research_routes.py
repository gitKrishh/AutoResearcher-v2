"""Tests for the Research Router."""

from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_orchestrator_service
from app.core.schemas import FinalReport, InsightReport, PaperAnalysis
from app.main import app
from app.services.orchestrator_service import OrchestratorService


@pytest.fixture
def mock_orchestrator():
    orchestrator = AsyncMock(spec=OrchestratorService)
    
    # Mock the return of the orchestrator to simulate full pipeline success
    orchestrator.run_research.return_value = FinalReport(
        topic="Test Topic",
        paper_count=2,
        papers=[
            PaperAnalysis(
                id="1",
                title="Paper 1",
                abstract="A",
                authors=["B"],
                pdf_url="http://c.com",
                published="2024",
                source="arxiv",
                summary="Sum 1",
                methodology="Meth 1",
                datasets="Data 1",
                key_findings="Find 1",
                limitations="Lim 1",
                contribution="Contrib 1",
            )
        ],
        literature_review="# Final Review\nMarkdown content.",
        insights=InsightReport(
            research_gaps=["Gap 1"],
            contradictions=["Contradiction 1"],
            trends=["Trend 1"],
            future_directions=["Dir 1"]
        ),
        generated_at="2024-01-01T00:00:00Z"
    )
    return orchestrator


@pytest.fixture
def client(mock_orchestrator):
    # Override the dependency to use our mock
    app.dependency_overrides[get_orchestrator_service] = lambda: mock_orchestrator
    with TestClient(app) as c:
        yield c
    # Clean up override
    app.dependency_overrides.clear()


def test_conduct_research_success(client, mock_orchestrator):
    """POST /api/research should trigger orchestrator and return FinalReport."""
    response = client.post("/api/research", json={"topic": "Test Topic", "max_papers": 3})
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["topic"] == "Test Topic"
    assert data["data"]["paper_count"] == 2
    assert "Final Review" in data["data"]["literature_review"]
    
    # Verify orchestrator was called with correct arguments
    mock_orchestrator.run_research.assert_called_once_with(topic="Test Topic", max_papers=3)


def test_conduct_research_no_results(client, mock_orchestrator):
    """Should return structured error if orchestrator raises ValueError (e.g. no papers)."""
    mock_orchestrator.run_research.side_effect = ValueError("No papers found")
    
    response = client.post("/api/research", json={"topic": "Obscure Topic", "max_papers": 5})
    
    assert response.status_code == 200  # API returns 200 with success=False
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "NO_RESULTS"
    assert "No papers found" in data["error"]["message"]
