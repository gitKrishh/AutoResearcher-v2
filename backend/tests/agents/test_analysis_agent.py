"""Tests for AnalysisAgent."""

from unittest.mock import AsyncMock

import pytest

from app.agents.analysis_agent import AnalysisAgent
from app.core.schemas import ProcessedPaper
from app.services.llm_service import LLMService


@pytest.fixture
def mock_llm_service():
    llm = AsyncMock(spec=LLMService)
    # Default mock response for valid JSON
    llm.complete_json.return_value = {
        "summary": "Mock summary",
        "methodology": "Mock methodology",
        "datasets": "Mock datasets",
        "key_findings": "Mock findings",
        "limitations": "Mock limitations",
        "contribution": "Mock contribution",
    }
    return llm


@pytest.fixture
def sample_papers():
    return [
        ProcessedPaper(
            id="1",
            title="Paper 1",
            abstract="Abstract 1",
            authors=["Author A"],
            pdf_url="http://example.com/1.pdf",
            published="2023",
            source="arxiv",
            full_text="Full text of Paper 1...",
            page_count=10,
            text_length=1000,
        ),
        ProcessedPaper(
            id="2",
            title="Paper 2",
            abstract="Abstract 2",
            authors=["Author B"],
            pdf_url="http://example.com/2.pdf",
            published="2024",
            source="arxiv",
            full_text="Full text of Paper 2...",
            page_count=5,
            text_length=500,
        ),
    ]


async def test_analysis_agent_success(mock_llm_service, sample_papers):
    """Agent should parse papers and return PaperAnalysis objects."""
    agent = AnalysisAgent(llm_service=mock_llm_service)
    
    analyses = await agent.run(sample_papers)
    
    assert len(analyses) == 2
    assert analyses[0].summary == "Mock summary"
    assert analyses[1].title == "Paper 2"
    
    # Called LLM twice
    assert mock_llm_service.complete_json.call_count == 2


async def test_analysis_agent_handles_llm_error(mock_llm_service, sample_papers):
    """Agent should gracefully handle LLM errors without crashing the pipeline."""
    # Simulate an LLM failure for all papers
    mock_llm_service.complete_json.side_effect = Exception("LLM connection error")
    
    agent = AnalysisAgent(llm_service=mock_llm_service)
    
    analyses = await agent.run(sample_papers)
    
    assert len(analyses) == 2
    assert "Analysis failed" in analyses[0].summary
    assert analyses[0].title == "Paper 1"
    assert analyses[1].methodology == "N/A"
