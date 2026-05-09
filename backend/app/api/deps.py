"""Shared FastAPI dependencies for dependency injection.

All service instantiation happens here.
Route handlers use Depends() to inject these.
"""

from functools import lru_cache

from app.core.config import Settings, get_settings
from app.services.llm_service import LLMService


def get_app_settings() -> Settings:
    """Return application settings (cached singleton)."""
    return get_settings()


@lru_cache
def get_llm_service() -> LLMService:
    """Return LLM service instance (cached singleton).

    Uses OpenAI API key from settings.
    """
    _settings = get_settings()
    return LLMService(api_key=_settings.openai_api_key)
from app.services.vector_store_service import VectorStoreService

@lru_cache
def get_vector_store() -> VectorStoreService:
    """Return a singleton instance of the VectorStoreService."""
    return VectorStoreService()
