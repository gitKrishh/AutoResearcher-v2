"""Search tool — fetch academic papers from arXiv API.

This is a pure tool function (no LLM calls, no agent logic).
Agents call this tool; this tool does not call agents.
"""

import asyncio
import logging
from xml.etree import ElementTree

import httpx

from app.core.exceptions import SearchError
from app.core.schemas import Paper

logger = logging.getLogger(__name__)

# arXiv Atom XML namespaces
ATOM_NS = "{http://www.w3.org/2005/Atom}"
ARXIV_NS = "{http://arxiv.org/schemas/atom}"

ARXIV_API_URL = "https://export.arxiv.org/api/query"


async def search_arxiv(query: str, max_results: int = 10) -> list[Paper]:
    """Fetch papers from arXiv API for a given query.

    Args:
        query: Search query string (e.g. "transformer attention mechanisms").
        max_results: Maximum number of papers to return (1–50).

    Returns:
        List of Paper objects parsed from arXiv response.

    Raises:
        ValueError: If query is empty.
        SearchError: If the arXiv API request fails.
    """
    if not query.strip():
        raise ValueError("Query must not be empty")

    params = {
        "search_query": f"all:{query}",
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    }

    logger.info("Searching arXiv: query='%s', max_results=%d", query, max_results)

    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            response = await client.get(ARXIV_API_URL, params=params)
            response.raise_for_status()
    except httpx.HTTPError as e:
        logger.error("arXiv request failed: %s", e)
        raise SearchError(f"arXiv request failed: {e}") from e

    papers = _parse_arxiv_response(response.text)
    logger.info("arXiv returned %d papers for query='%s'", len(papers), query)

    # Rate limiting: arXiv allows ~3 req/sec
    await asyncio.sleep(0.4)

    return papers


def _parse_arxiv_response(xml_text: str) -> list[Paper]:
    """Parse arXiv Atom XML response into Paper objects.

    Args:
        xml_text: Raw XML string from arXiv API.

    Returns:
        List of Paper objects extracted from the XML.
    """
    papers: list[Paper] = []

    try:
        root = ElementTree.fromstring(xml_text)
    except ElementTree.ParseError as e:
        logger.error("Failed to parse arXiv XML: %s", e)
        raise SearchError(f"Failed to parse arXiv XML: {e}") from e

    entries = root.findall(f"{ATOM_NS}entry")

    for entry in entries:
        try:
            paper = _parse_entry(entry)
            if paper is not None:
                papers.append(paper)
        except Exception as e:
            # Skip malformed entries, don't crash the whole search
            title = entry.findtext(f"{ATOM_NS}title", default="unknown")
            logger.warning("Skipping malformed entry '%s': %s", title, e)
            continue

    return papers


def _parse_entry(entry: ElementTree.Element) -> Paper | None:
    """Parse a single arXiv <entry> element into a Paper.

    Args:
        entry: XML Element representing one arXiv paper.

    Returns:
        Paper object, or None if critical fields are missing.
    """
    # Extract ID (e.g. "http://arxiv.org/abs/2303.08774v6" → "2303.08774")
    raw_id = entry.findtext(f"{ATOM_NS}id", default="")
    if not raw_id:
        return None
    arxiv_id = raw_id.split("/abs/")[-1].split("v")[0]

    # Title — clean up whitespace
    title = entry.findtext(f"{ATOM_NS}title", default="")
    title = " ".join(title.split())

    # Abstract — clean up whitespace
    abstract = entry.findtext(f"{ATOM_NS}summary", default="")
    abstract = " ".join(abstract.split())

    # Authors
    authors: list[str] = []
    for author_elem in entry.findall(f"{ATOM_NS}author"):
        name = author_elem.findtext(f"{ATOM_NS}name", default="")
        if name:
            authors.append(name)

    # PDF URL — find link with title="pdf"
    pdf_url = ""
    for link in entry.findall(f"{ATOM_NS}link"):
        if link.get("title") == "pdf":
            pdf_url = link.get("href", "")
            break
    # Fallback: construct from ID
    if not pdf_url and arxiv_id:
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

    # Published date
    published = entry.findtext(f"{ATOM_NS}published", default="")
    if published:
        published = published[:10]  # "2023-03-15T..." → "2023-03-15"

    if not title or not abstract:
        return None

    return Paper(
        id=arxiv_id,
        title=title,
        abstract=abstract,
        authors=authors,
        pdf_url=pdf_url,
        published=published,
        source="arxiv",
    )
