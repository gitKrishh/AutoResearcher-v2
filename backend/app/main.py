"""FastAPI application entry point.

Initializes the app, registers middleware, mounts routers,
and sets up the application lifespan (startup/shutdown).
"""

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.exceptions import AutoResearcherError
from app.core.logging import setup_logging
from app.core.schemas import APIError, APIResponse
from app.api.routers.health import router as health_router
from app.api.routers.search import router as search_router

# Configure logging before anything else
setup_logging()
logger = logging.getLogger(__name__)


# ============================================================
# Application Lifespan
# ============================================================


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application startup and shutdown events.

    Startup: Load FAISS index, warm up models, etc.
    Shutdown: Save state, close connections, etc.
    """
    # --- Startup ---
    logger.info("AutoResearcher backend starting up...")
    logger.info("Environment: %s", settings.environment)

    # TODO (Phase 4): Load FAISS index from disk
    # TODO (Phase 3): Pre-load embedding model

    logger.info("AutoResearcher backend ready.")
    yield

    # --- Shutdown ---
    logger.info("AutoResearcher backend shutting down...")


# ============================================================
# FastAPI App
# ============================================================

app = FastAPI(
    title="AutoResearcher API",
    description="Autonomous AI research assistant — search, analyze, and review academic papers.",
    version="0.1.0",
    lifespan=lifespan,
)


# ============================================================
# Middleware
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Exception Handlers
# ============================================================


@app.exception_handler(AutoResearcherError)
async def autoresearcher_error_handler(
    request: Request,
    exc: AutoResearcherError,
) -> JSONResponse:
    """Catch all custom exceptions and return structured error responses.

    Never let internal exceptions propagate as 500s with stack traces.
    """
    error_code = type(exc).__name__.upper()
    logger.error("Handled error [%s]: %s", error_code, str(exc))

    return JSONResponse(
        status_code=500,
        content=APIResponse(
            success=False,
            error=APIError(
                code=error_code,
                message=str(exc),
                detail=None,
            ),
        ).model_dump(),
    )


# ============================================================
# Router Registration
# ============================================================

app.include_router(health_router, prefix="/api", tags=["health"])

app.include_router(search_router, prefix="/api", tags=["search"])
# TODO (Phase 5): app.include_router(research_router, prefix="/api", tags=["research"])
# TODO (Phase 7): app.include_router(papers_router, prefix="/api", tags=["papers"])
