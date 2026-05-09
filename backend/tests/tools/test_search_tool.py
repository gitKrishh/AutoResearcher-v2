"""Tests for tools/search_tool.py — arXiv search functionality."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.tools.search_tool import search_arxiv, _parse_arxiv_response
from app.core.exceptions import SearchError


# Sample arXiv XML response for mocking
SAMPLE_ARXIV_XML = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/2303.08774v6</id>
    <title>GPT-4 Technical Report</title>
    <summary>We report the development of GPT-4, a large-scale multimodal model.</summary>
    <author><name>OpenAI</name></author>
    <author><name>Josh Achiam</name></author>
    <link href="https://arxiv.org/pdf/2303.08774v6" title="pdf" type="application/pdf"/>
    <published>2023-03-15T17:15:04Z</published>
  </entry>
  <entry>
    <id>http://arxiv.org/abs/2305.10403v1</id>
    <title>Tree of Thoughts: Deliberate Problem Solving with LLMs</title>
    <summary>We introduce a new framework for language model reasoning.</summary>
    <author><name>Shunyu Yao</name></author>
    <link href="https://arxiv.org/pdf/2305.10403v1" title="pdf" type="application/pdf"/>
    <published>2023-05-17T13:05:23Z</published>
  </entry>
</feed>"""


# --- search_arxiv tests ---


async def test_search_arxiv_returns_papers_on_valid_query():
    """search_arxiv should return a list of Paper objects."""
    mock_response = MagicMock()
    mock_response.text = SAMPLE_ARXIV_XML
    mock_response.raise_for_status = MagicMock()

    with patch("app.tools.search_tool.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_class.return_value.__aexit__ = AsyncMock(return_value=False)

        papers = await search_arxiv("AI agents", max_results=5)

    assert len(papers) == 2
    assert papers[0].title == "GPT-4 Technical Report"
    assert papers[0].id == "2303.08774"
    assert papers[0].source == "arxiv"


async def test_search_arxiv_raises_on_empty_query():
    """search_arxiv should raise ValueError for empty query."""
    with pytest.raises(ValueError, match="Query must not be empty"):
        await search_arxiv("", max_results=5)

    with pytest.raises(ValueError, match="Query must not be empty"):
        await search_arxiv("   ", max_results=5)


async def test_search_arxiv_raises_search_error_on_network_failure():
    """search_arxiv should raise SearchError when arXiv is unreachable."""
    import httpx

    with patch("app.tools.search_tool.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.HTTPError("Connection refused")
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_class.return_value.__aexit__ = AsyncMock(return_value=False)

        with pytest.raises(SearchError, match="arXiv request failed"):
            await search_arxiv("test query", max_results=5)


# --- _parse_arxiv_response tests ---


def test_parse_arxiv_response_extracts_fields():
    """Parser should extract all Paper fields correctly from XML."""
    papers = _parse_arxiv_response(SAMPLE_ARXIV_XML)

    assert len(papers) == 2

    # First paper
    p1 = papers[0]
    assert p1.id == "2303.08774"
    assert p1.title == "GPT-4 Technical Report"
    assert "multimodal model" in p1.abstract
    assert "OpenAI" in p1.authors
    assert "Josh Achiam" in p1.authors
    assert "2303.08774" in p1.pdf_url
    assert p1.published == "2023-03-15"
    assert p1.source == "arxiv"

    # Second paper
    p2 = papers[1]
    assert p2.id == "2305.10403"
    assert "Tree of Thoughts" in p2.title


def test_parse_arxiv_response_handles_empty_feed():
    """Parser should return empty list for a feed with no entries."""
    empty_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom"></feed>"""

    papers = _parse_arxiv_response(empty_xml)
    assert papers == []


def test_parse_arxiv_response_raises_on_invalid_xml():
    """Parser should raise SearchError for malformed XML."""
    with pytest.raises(SearchError, match="Failed to parse arXiv XML"):
        _parse_arxiv_response("not xml at all <><>")
