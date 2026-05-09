"""Embedding tool — generate vector embeddings from text chunks.

Uses SentenceTransformers for local embedding generation.
The model is loaded as a singleton on first use to avoid repeated loading.
All embeddings are L2 normalized to be compatible with FAISS IndexFlatIP
(which uses inner product to compute cosine similarity on normalized vectors).
"""

import logging

import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.core.exceptions import EmbeddingError

logger = logging.getLogger(__name__)

# Singleton model instance
_model: SentenceTransformer | None = None


def _get_model(model_name: str | None = None) -> SentenceTransformer:
    """Lazily load the embedding model as a singleton.

    Args:
        model_name: Name of the SentenceTransformers model.
                    Defaults to settings.embedding_model.

    Returns:
        The loaded SentenceTransformer model instance.
    """
    global _model
    target_model = model_name or settings.embedding_model

    if _model is None:
        logger.info("Loading embedding model: %s (this may take a moment on first run)", target_model)
        try:
            _model = SentenceTransformer(target_model)
            logger.info("Embedding model loaded successfully.")
        except Exception as e:
            logger.error("Failed to load embedding model %s: %s", target_model, e)
            raise EmbeddingError(f"Failed to load embedding model: {e}") from e

    return _model


def _normalize_l2(embeddings: np.ndarray) -> np.ndarray:
    """L2 normalize a batch of embeddings.

    Required for cosine similarity search with FAISS IndexFlatIP.

    Args:
        embeddings: 2D numpy array of embeddings.

    Returns:
        L2 normalized 2D numpy array.
    """
    # Calculate the L2 norm for each vector along the feature axis (axis=1)
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    
    # Avoid division by zero
    norms[norms == 0] = 1e-10
    
    return embeddings / norms


def create_embeddings(
    chunks: list[str],
    model_name: str | None = None,
    batch_size: int = 32,
) -> np.ndarray:
    """Batch encode text chunks into normalized embeddings.

    Args:
        chunks: List of text strings to embed.
        model_name: Override default embedding model.
        batch_size: Batch size for encoding to control memory usage.

    Returns:
        A 2D numpy array of shape (len(chunks), embedding_dim) with dtype float32.

    Raises:
        EmbeddingError: If embedding generation fails.
    """
    if not chunks:
        logger.debug("create_embeddings called with empty chunks list")
        return np.array([], dtype=np.float32)

    model = _get_model(model_name)

    logger.debug("Generating embeddings for %d chunks (batch_size=%d)", len(chunks), batch_size)

    try:
        # SentenceTransformers encode returns a numpy array by default
        embeddings = model.encode(
            chunks,
            batch_size=batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
        )

        # Ensure correct type for FAISS
        embeddings = embeddings.astype(np.float32)

        # L2 Normalize for cosine similarity
        normalized_embeddings = _normalize_l2(embeddings)

        logger.debug("Generated embeddings shape: %s", normalized_embeddings.shape)
        return normalized_embeddings

    except Exception as e:
        logger.error("Failed to generate embeddings: %s", e)
        raise EmbeddingError(f"Embedding generation failed: {e}") from e


def embed_query(query: str, model_name: str | None = None) -> np.ndarray:
    """Embed a single query string for searching.

    Args:
        query: The search query string.
        model_name: Override default embedding model.

    Returns:
        A 2D numpy array of shape (1, embedding_dim) with dtype float32.

    Raises:
        EmbeddingError: If embedding generation fails.
    """
    if not query or not query.strip():
        raise EmbeddingError("Cannot embed an empty query")

    # Reuse batch encoding function for consistency in normalization and type
    embeddings = create_embeddings([query], model_name=model_name)
    return embeddings
