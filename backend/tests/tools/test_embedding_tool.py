"""Tests for tools/embedding_tool.py — vector generation."""

import numpy as np
import pytest

from app.tools.embedding_tool import create_embeddings, embed_query
from app.core.exceptions import EmbeddingError


def test_create_embeddings_returns_correct_shape():
    """create_embeddings should return shape (n_chunks, 384)."""
    chunks = [
        "This is the first chunk.",
        "Here is the second chunk.",
        "And a third one for good measure."
    ]
    
    embeddings = create_embeddings(chunks)
    
    assert isinstance(embeddings, np.ndarray)
    assert embeddings.shape == (3, 384)


def test_create_embeddings_returns_float32():
    """FAISS requires float32 dtype."""
    chunks = ["Just one chunk."]
    embeddings = create_embeddings(chunks)
    
    assert embeddings.dtype == np.float32


def test_create_embeddings_normalized():
    """Embeddings must be L2 normalized for FAISS IndexFlatIP."""
    chunks = ["This chunk needs to be normalized.", "So does this one."]
    embeddings = create_embeddings(chunks)
    
    # Calculate L2 norm for each vector (should be close to 1.0)
    norms = np.linalg.norm(embeddings, axis=1)
    
    for norm in norms:
        assert pytest.approx(norm, 0.0001) == 1.0


def test_create_embeddings_empty_list():
    """Empty list should return empty numpy array."""
    embeddings = create_embeddings([])
    
    assert isinstance(embeddings, np.ndarray)
    assert embeddings.shape == (0,)
    assert embeddings.dtype == np.float32


def test_embed_query_returns_correct_shape():
    """embed_query should return shape (1, 384)."""
    query = "What is machine learning?"
    
    embedding = embed_query(query)
    
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape == (1, 384)
    assert embedding.dtype == np.float32


def test_embed_query_normalized():
    """embed_query should also be L2 normalized."""
    query = "Another test query."
    embedding = embed_query(query)
    
    norm = np.linalg.norm(embedding[0])
    assert pytest.approx(norm, 0.0001) == 1.0


def test_embed_query_empty():
    """Empty query should raise EmbeddingError."""
    with pytest.raises(EmbeddingError, match="Cannot embed an empty query"):
        embed_query("")
        
    with pytest.raises(EmbeddingError, match="Cannot embed an empty query"):
        embed_query("   ")
