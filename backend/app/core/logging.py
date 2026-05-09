"""Logging configuration for AutoResearcher backend.

Sets up structured logging with consistent formatting.
Use `logging.getLogger(__name__)` in every module — never `print()`.
"""

import logging
import sys

from app.core.config import settings


def setup_logging() -> None:
    """Configure root logger with format and level from settings."""
    log_format = "[%(asctime)s] %(levelname)s %(name)s: %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format=log_format,
        datefmt=date_format,
        stream=sys.stdout,
        force=True,
    )

    # Quiet noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
