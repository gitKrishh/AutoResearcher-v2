"""Search route — POST /api/search.

Accepts a search query and returns matching papers from arXiv.
No RAG, no analysis — just paper search results.
"""

import logging

from fastapi import APIRouter

from app.core.exceptions import SearchError
from app.core.schemas import APIError, APIResponse, SearchRequest
from app.tools.search_tool import search_arxiv

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/search", response_model=APIResponse)
async def search_papers(request: SearchRequest) -> APIResponse:
    """Search for academic papers matching the given query.

    Returns a list of papers with title, abstract, authors, and PDF URL.
    """
    logger.info("Search request: query='%s', max_results=%d", request.query, request.max_results)

    try:
        papers = await search_arxiv(request.query, request.max_results)

        return APIResponse(
            success=True,
            data=[paper.model_dump() for paper in papers],
            meta={"count": len(papers)},
        )

    except SearchError as e:
        logger.error("Search failed: %s", e)
        return APIResponse(
            success=False,
            error=APIError(
                code="SEARCH_FAILED",
                message="Failed to search for papers.",
                detail=str(e),
            ),
        )
