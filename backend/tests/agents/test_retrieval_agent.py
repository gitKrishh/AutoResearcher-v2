"""Tests for agents/retrieval_agent.py — RAG question answering."""

from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest

from app.agents.retrieval_agent import RetrievalAgent
from app.core.schemas import ChunkResult
from app.services.llm_service import LLMService
from app.services.vector_store_service import VectorStoreService


@pytest.fixture
def mock_vector_store():
    store = MagicMock(spec=VectorStoreService)
    # Default search mock: return some fake chunks
    store.search.return_value = [
        ChunkResult(
            text="Transformer models use self-attention.",
            score=0.95,
            paper_id="1",
            paper_title="Attention is All You Need",
        )
    ]
    return store


@pytest.fixture
def mock_llm_service():
    llm = AsyncMock(spec=LLMService)
    llm.complete.return_value = "Mocked LLM answer about transformers."
    return llm


async def test_retrieval_agent_success(mock_llm_service, mock_vector_store):
    """Agent should embed, search, format context, and call LLM."""
    agent = RetrievalAgent(llm_service=mock_llm_service, vector_store=mock_vector_store)

    with patch("app.agents.retrieval_agent.embed_query") as mock_embed:
        mock_embed.return_value = np.array([[0.1, 0.2]])

        answer = await agent.run("How do transformers work?", top_k=3)

        assert answer == "Mocked LLM answer about transformers."
        
        # Verify vector search called with top_k
        mock_vector_store.search.assert_called_once()
        args, kwargs = mock_vector_store.search.call_args
        assert kwargs["top_k"] == 3
        
        # Verify LLM called with context formatted
        mock_llm_service.complete.assert_called_once()
        prompt = mock_llm_service.complete.call_args[0][0]
        assert "How do transformers work?" in prompt
        assert "Transformer models use self-attention." in prompt
        assert "[Source 1: Attention is All You Need]" in prompt


async def test_retrieval_agent_empty_results(mock_llm_service, mock_vector_store):
    """If no chunks found, agent should return early without calling LLM."""
    mock_vector_store.search.return_value = []
    agent = RetrievalAgent(llm_service=mock_llm_service, vector_store=mock_vector_store)

    with patch("app.agents.retrieval_agent.embed_query") as mock_embed:
        mock_embed.return_value = np.array([[0.1, 0.2]])

        answer = await agent.run("Query with no results")

        assert "do not contain enough information" in answer
        mock_llm_service.complete.assert_not_called()
