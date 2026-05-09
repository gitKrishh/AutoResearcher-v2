"""Tests for services/vector_store_service.py — FAISS integration."""

import pytest
import numpy as np
from app.services.vector_store_service import VectorStoreService
from app.core.exceptions import VectorStoreError


@pytest.fixture
def vector_store():
    """Provides a fresh, initialized VectorStoreService."""
    service = VectorStoreService()
    service.initialize_index(dimension=3)
    return service


def test_initialize_index(vector_store):
    """Index should be initialized with 0 chunks."""
    assert vector_store.get_total_chunks() == 0
    assert vector_store.dimension == 3


def test_add_chunks(vector_store):
    """Adding chunks should increment total chunks and return IDs."""
    chunks = ["chunk1", "chunk2"]
    embeddings = np.array([[1, 0, 0], [0, 1, 0]], dtype=np.float32)
    metadata = [{"paper_id": "1", "paper_title": "Paper 1"}, {"paper_id": "2", "paper_title": "Paper 2"}]

    chunk_ids = vector_store.add_chunks(chunks, embeddings, metadata)

    assert len(chunk_ids) == 2
    assert vector_store.get_total_chunks() == 2
    assert vector_store.metadata[0]["text"] == "chunk1"
    assert vector_store.metadata[1]["chunk_id"] == "chunk_1"


def test_add_chunks_raises_on_uninitialized():
    """Adding to an uninitialized index should raise an error."""
    service = VectorStoreService()
    with pytest.raises(VectorStoreError, match="Index not initialized"):
        service.add_chunks(["test"], np.array([[1.0]]), [{"paper_id": "1"}])


def test_add_chunks_raises_on_mismatch(vector_store):
    """Mismatched inputs should raise an error."""
    chunks = ["chunk1"]
    embeddings = np.array([[1, 0, 0], [0, 1, 0]], dtype=np.float32)  # 2 embeddings
    metadata = [{"paper_id": "1"}]

    with pytest.raises(VectorStoreError, match="Length mismatch"):
        vector_store.add_chunks(chunks, embeddings, metadata)


def test_search_returns_ordered_results(vector_store):
    """Search should return highest cosine similarity first."""
    chunks = ["apple", "car", "banana"]
    # These represent L2 normalized vectors
    embeddings = np.array([
        [1.0, 0.0, 0.0],  # apple
        [0.0, 1.0, 0.0],  # car
        [0.8, 0.6, 0.0],  # banana (closer to apple)
    ], dtype=np.float32)
    metadata = [
        {"paper_id": "1", "paper_title": "Fruit"},
        {"paper_id": "2", "paper_title": "Auto"},
        {"paper_id": "3", "paper_title": "Fruit 2"},
    ]

    vector_store.add_chunks(chunks, embeddings, metadata)

    # Query similar to apple
    query = np.array([[0.9, 0.0, 0.0]], dtype=np.float32)
    
    results = vector_store.search(query, top_k=2)
    
    assert len(results) == 2
    assert results[0].text == "apple"
    assert results[1].text == "banana"


def test_save_and_load_index(vector_store, tmp_path):
    """Index and metadata should be correctly saved and loaded."""
    chunks = ["saved chunk"]
    embeddings = np.array([[1.0, 0.0, 0.0]], dtype=np.float32)
    metadata = [{"paper_id": "saved", "paper_title": "Saved Paper"}]
    
    vector_store.add_chunks(chunks, embeddings, metadata)
    
    # Save
    vector_store.save_index(tmp_path)
    
    # Load into a new instance
    new_store = VectorStoreService()
    new_store.load_index(tmp_path)
    
    assert new_store.get_total_chunks() == 1
    assert new_store.metadata[0]["text"] == "saved chunk"
    assert new_store.dimension == 3
