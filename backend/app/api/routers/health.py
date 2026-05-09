"""Health check route.

GET /api/health — returns service status.
Used by monitoring, load balancers, and frontend to verify backend is alive.
"""

import logging

from fastapi import APIRouter

from app.core.schemas import APIResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=APIResponse)
async def health_check() -> APIResponse:
    """Return service health status."""
    logger.debug("Health check requested")
    return APIResponse(
        success=True,
        data={"status": "healthy"},
    )
