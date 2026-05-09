"""Research route — POST /api/research.

This uses the OrchestratorService to run the full multi-agent pipeline.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_orchestrator_service
from app.core.exceptions import AutoResearcherError
from app.core.schemas import APIError, APIResponse, ResearchRequest
from app.services.orchestrator_service import OrchestratorService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/research", response_model=APIResponse)
async def conduct_research(
    request: ResearchRequest,
    orchestrator: OrchestratorService = Depends(get_orchestrator_service),
) -> APIResponse:
    """End-to-end multi-agent research pipeline.

    Decomposes topic, searches, extracts, embeds, analyzes, extracts insights, 
    and writes a final literature review.
    """
    logger.info("Handling POST /api/research for topic: '%s'", request.topic)

    try:
        final_report = await orchestrator.run_research(
            topic=request.topic, 
            max_papers=request.max_papers
        )

        return APIResponse(
            success=True,
            data=final_report.model_dump(),
            meta={
                "pipeline": "full_orchestrator"
            }
        )

    except ValueError as e:
        # Expected errors like no papers found
        logger.warning("Research pipeline stopped: %s", e)
        return APIResponse(
            success=False,
            error=APIError(
                code="NO_RESULTS",
                message=str(e),
            ),
        )
    except AutoResearcherError as e:
        logger.error("Research pipeline failed with domain error: %s", e)
        return APIResponse(
            success=False,
            error=APIError(
                code=type(e).__name__.upper(),
                message=str(e),
            ),
        )
    except Exception as e:
        logger.error("Unexpected error in research pipeline: %s", e, exc_info=True)
        return APIResponse(
            success=False,
            error=APIError(
                code="INTERNAL_ERROR",
                message=f"An unexpected error occurred: {e}",
            ),
        )


# We could also add GET /api/papers/{id} here if needed, but the plan step 4
# says "Add GET /api/papers/{id} route"
# For now, we will just return a 501 Not Implemented or skip it since we don't
# persist individual paper JSONs to a database yet.
@router.get("/papers/{paper_id}", response_model=APIResponse)
async def get_paper(paper_id: str) -> APIResponse:
    """Retrieve a previously analyzed paper. (Placeholder)"""
    return APIResponse(
        success=False,
        error=APIError(
            code="NOT_IMPLEMENTED",
            message="Database persistence for individual papers is not yet implemented in Phase 7."
        )
    )
