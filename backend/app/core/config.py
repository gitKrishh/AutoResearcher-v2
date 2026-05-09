"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """AutoResearcher backend settings.

    All values are loaded from .env file or environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM (OpenAI SDK for text generation)
    openai_api_key: str = ""

    # NVIDIA API (used ONLY for embeddings — not for chat/completions)
    nvidia_api_key: str = ""
    nvidia_model: str = "meta/llama-3.1-70b-instruct"

    # LLM Models
    default_llm_model: str = "gpt-4o-mini"
    heavy_llm_model: str = "gpt-4o"

    # Embeddings
    embedding_model: str = "all-MiniLM-L6-v2"

    # Vector Store
    faiss_index_path: str = "vector_store/index"

    # PDF
    pdf_cache_dir: str = "data/pdfs"
    max_pdf_pages: int = 50

    # Chunking
    chunk_size: int = 512
    chunk_overlap: int = 64

    # Search
    max_papers_per_search: int = 10

    # Server
    environment: str = "development"
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    """Return cached Settings instance (singleton)."""
    return Settings()


settings = get_settings()
