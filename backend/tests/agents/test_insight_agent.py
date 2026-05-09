"""Tests for InsightAgent."""

from unittest.mock import AsyncMock

import pytest

from app.agents.insight_agent import InsightAgent
from app.core.schemas import PaperAnalysis
from app.services.llm_service import LLMService


@pytest.fixture
def mock_llm_service():
    llm = AsyncMock(spec=LLMService)
    llm.complete_json.return_value = {
        "research_gaps": ["Gap 1"],
        "contradictions": ["Contradiction 1"],
        "trends": ["Trend 1"],
        "future_directions": ["Direction 1"],
    }
    return llm


@pytest.fixture
def sample_analyses():
    return [
        PaperAnalysis(
            id="1",
            title="Analysis 1",
            abstract="Abstract 1",
            authors=["Author 1"],
            pdf_url="http://example.com",
            published="2024",
            source="arxiv",
            summary="Summary 1",
            methodology="Method 1",
            datasets="Dataset 1",
            key_findings="Findings 1",
            limitations="Limitation 1",
            contribution="Contribution 1",
        )
    ]


async def test_insight_agent_success(mock_llm_service, sample_analyses):
    """InsightAgent should return an InsightReport."""
    agent = InsightAgent(llm_service=mock_llm_service)
    
    report = await agent.run(analyses=sample_analyses, topic="Test Topic")
    
    assert report is not None
    assert report.research_gaps == ["Gap 1"]
    mock_llm_service.complete_json.assert_called_once()


async def test_insight_agent_empty_analyses(mock_llm_service):
    """InsightAgent should return None if given empty analyses list."""
    agent = InsightAgent(llm_service=mock_llm_service)
    
    report = await agent.run(analyses=[], topic="Test Topic")
    
    assert report is None
    mock_llm_service.complete_json.assert_not_called()


async def test_insight_agent_handles_error(mock_llm_service, sample_analyses):
    """InsightAgent should return None if LLM fails."""
    mock_llm_service.complete_json.side_effect = Exception("LLM Error")
    agent = InsightAgent(llm_service=mock_llm_service)
    
    report = await agent.run(analyses=sample_analyses, topic="Test Topic")
    
    assert report is None
