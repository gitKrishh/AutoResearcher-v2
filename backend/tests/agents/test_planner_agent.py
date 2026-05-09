"""Tests for PlannerAgent."""

from unittest.mock import AsyncMock

import pytest

from app.agents.planner_agent import PlannerAgent
from app.services.llm_service import LLMService


@pytest.fixture
def mock_llm_service():
    llm = AsyncMock(spec=LLMService)
    llm.complete_json.return_value = ["sub-topic 1", "sub-topic 2", "sub-topic 3"]
    return llm


async def test_planner_agent_success(mock_llm_service):
    """PlannerAgent should return a list of sub-topics from the LLM."""
    agent = PlannerAgent(llm_service=mock_llm_service)
    
    sub_topics = await agent.run("Main Topic")
    
    assert len(sub_topics) == 3
    assert sub_topics[0] == "sub-topic 1"
    mock_llm_service.complete_json.assert_called_once()


async def test_planner_agent_fallback_on_invalid_format(mock_llm_service):
    """PlannerAgent should fallback to original topic if LLM returns non-list."""
    mock_llm_service.complete_json.return_value = {"not": "a list"}
    agent = PlannerAgent(llm_service=mock_llm_service)
    
    sub_topics = await agent.run("Main Topic")
    
    assert sub_topics == ["Main Topic"]


async def test_planner_agent_fallback_on_error(mock_llm_service):
    """PlannerAgent should fallback to original topic if LLM raises error."""
    mock_llm_service.complete_json.side_effect = Exception("LLM failure")
    agent = PlannerAgent(llm_service=mock_llm_service)
    
    sub_topics = await agent.run("Main Topic")
    
    assert sub_topics == ["Main Topic"]
