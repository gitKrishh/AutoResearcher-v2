"""FastAPI application entry point.

Initializes the app, registers middleware, mounts routers,
and sets up the application lifespan (startup/shutdown).
"""

import logging
import time
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.exceptions import AutoResearcherError
from app.core.logging import setup_logging
from app.core.schemas import APIError, APIResponse
from app.api.routers.health import router as health_router
from app.api.routers.search import router as search_router
from app.api.routers.research import router as research_router
from app.api.routers.chat import router as chat_router

# Configure logging before anything else
setup_logging()
logger = logging.getLogger(__name__)

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address)

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

    # Load FAISS index from disk
    from app.api.deps import get_vector_store
    
    vector_store = get_vector_store()
    vector_dir = Path(settings.faiss_index_path).parent
    
    try:
        vector_store.load_index(vector_dir)
    except Exception:
        logger.info("No existing vector store found, initializing a new one.")
        vector_store.initialize_index()

    # Pre-load embedding model
    from app.tools.embedding_tool import _get_model
    try:
        _get_model()
    except Exception as e:
        logger.warning("Could not pre-load embedding model: %s", e)

    logger.info("AutoResearcher backend ready.")
    yield

    # --- Shutdown ---
    logger.info("AutoResearcher backend shutting down...")
    
    # Save FAISS index
    try:
        vector_store.save_index(vector_dir)
    except Exception as e:
        logger.error("Failed to save FAISS index on shutdown: %s", e)


# ============================================================
# FastAPI App
# ============================================================

app = FastAPI(
    title="AutoResearcher API",
    description="Autonomous AI research assistant — search, analyze, and review academic papers.",
    version="1.0.0",
    lifespan=lifespan,
)

# Rate Limiter Configuration
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ============================================================
# Middleware
# ============================================================

# Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(
        "Request: %s %s - Status: %d - Duration: %.2fs",
        request.method,
        request.url.path,
        response.status_code,
        duration,
    )
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
    """Catch all custom exceptions and return structured error responses."""
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
app.include_router(research_router, prefix="/api", tags=["research"])
app.include_router(chat_router, prefix="/api", tags=["chat"])
