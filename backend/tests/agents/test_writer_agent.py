"""Tests for WriterAgent."""

from unittest.mock import AsyncMock

import pytest

from app.agents.writer_agent import WriterAgent
from app.core.schemas import PaperAnalysis
from app.services.llm_service import LLMService


@pytest.fixture
def mock_llm_service():
    llm = AsyncMock(spec=LLMService)
    
    # When complete_json is called (comparison and insights)
    async def mock_complete_json(prompt, **kwargs):
        if "common_themes" in prompt:
            # Comparison prompt
            return {
                "common_themes": ["Theme A"],
                "key_differences": ["Diff B"],
                "methodology_comparison": "Method C",
                "strongest_paper": "Paper 1",
            }
        else:
            # Insights prompt
            return {
                "research_gaps": ["Gap 1"],
                "contradictions": ["Contradiction 1"],
                "trends": ["Trend 1"],
                "future_directions": ["Direction 1"],
            }
    
    llm.complete_json = mock_complete_json
    
    # When complete is called (literature review)
    llm.complete.return_value = "# Final Literature Review\n\nThis is the markdown."
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


async def test_writer_agent_success(mock_llm_service, sample_analyses):
    """WriterAgent should generate comparison, insights, and final review."""
    agent = WriterAgent(llm_service=mock_llm_service)
    
    report = await agent.run(topic="Test Topic", analyses=sample_analyses)
    
    assert report.topic == "Test Topic"
    assert report.paper_count == 1
    assert report.literature_review == "# Final Literature Review\n\nThis is the markdown."
    
    # Insights should be populated
    assert report.insights is not None
    assert report.insights.research_gaps == ["Gap 1"]


async def test_writer_agent_empty_analyses(mock_llm_service):
    """WriterAgent should return an empty report if no analyses are provided."""
    agent = WriterAgent(llm_service=mock_llm_service)
    
    report = await agent.run(topic="Empty Topic", analyses=[])
    
    assert report.paper_count == 0
    assert "No relevant papers" in report.literature_review
    assert report.insights is None
    
    # LLM should not be called
    mock_llm_service.complete.assert_not_called()
