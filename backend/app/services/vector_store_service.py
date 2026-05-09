"""Vector Store Service — FAISS wrapper for similarity search.

Manages the FAISS index and associated metadata (text chunks, paper info).
Uses IndexFlatIP (inner product) which, when used with L2 normalized vectors,
computes cosine similarity.
"""

import json
import logging
from pathlib import Path
from typing import Any

import faiss
import numpy as np

from app.core.exceptions import VectorStoreError
from app.core.schemas import ChunkResult

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Service to manage FAISS vector store and metadata."""

    def __init__(self) -> None:
        """Initialize empty index and metadata lists."""
        self.index: faiss.Index | None = None
        self.metadata: list[dict[str, Any]] = []
        self.dimension: int = 0

    def initialize_index(self, dimension: int = 384) -> None:
        """Create a new empty FAISS index.

        Args:
            dimension: The size of the embedding vectors.
        """
        self.dimension = dimension
        # IndexFlatIP calculates inner product. With L2 normalized vectors, this is Cosine Similarity.
        self.index = faiss.IndexFlatIP(dimension)
        self.metadata = []
        logger.info("Initialized new FAISS index with dimension %d", dimension)

    def add_chunks(
        self,
        chunks: list[str],
        embeddings: np.ndarray,
        chunk_metadata: list[dict[str, Any]],
    ) -> list[str]:
        """Add vectors and their corresponding text/metadata to the index.

        Args:
            chunks: List of text chunks.
            embeddings: 2D numpy array of embeddings for the chunks.
            chunk_metadata: List of dicts containing paper_id, paper_title, page_num.

        Returns:
            List of generated chunk IDs (string indices).

        Raises:
            VectorStoreError: If inputs are mismatched or index is not initialized.
        """
        if self.index is None:
            raise VectorStoreError("Index not initialized. Call initialize_index() first.")

        if len(chunks) != embeddings.shape[0] or len(chunks) != len(chunk_metadata):
            raise VectorStoreError(
                f"Length mismatch: {len(chunks)} chunks, {embeddings.shape[0]} embeddings, {len(chunk_metadata)} metadata"
            )

        if len(chunks) == 0:
            return []

        try:
            # Ensure float32 dtype for FAISS
            if embeddings.dtype != np.float32:
                embeddings = embeddings.astype(np.float32)

            self.index.add(embeddings)
            
            chunk_ids = []
            start_idx = len(self.metadata)
            
            for i, (text, meta) in enumerate(zip(chunks, chunk_metadata)):
                chunk_id = f"chunk_{start_idx + i}"
                chunk_ids.append(chunk_id)
                
                # Store text inside metadata so it's retrievable
                meta_copy = dict(meta)
                meta_copy["text"] = text
                meta_copy["chunk_id"] = chunk_id
                
                self.metadata.append(meta_copy)

            logger.info("Added %d chunks to FAISS index. Total: %d", len(chunks), self.get_total_chunks())
            return chunk_ids

        except Exception as e:
            raise VectorStoreError(f"Failed to add chunks to index: {e}") from e

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> list[ChunkResult]:
        """Search the index for the most similar chunks.

        Args:
            query_embedding: 2D numpy array of shape (1, dimension).
            top_k: Number of results to return.

        Returns:
            List of ChunkResult objects ordered by descending similarity score.

        Raises:
            VectorStoreError: If index is empty or search fails.
        """
        if self.index is None or self.get_total_chunks() == 0:
            logger.warning("Search called on empty or uninitialized index.")
            return []

        try:
            # Ensure float32
            if query_embedding.dtype != np.float32:
                query_embedding = query_embedding.astype(np.float32)

            # limit top_k to total available chunks
            k = min(top_k, self.get_total_chunks())
            
            # search returns distances (scores) and indices
            scores, indices = self.index.search(query_embedding, k)
            
            results = []
            # Flatten arrays since query_embedding is (1, d)
            for score, idx in zip(scores[0], indices[0]):
                if idx == -1:  # FAISS returns -1 if not enough results
                    continue
                    
                meta = self.metadata[idx]
                results.append(
                    ChunkResult(
                        text=meta["text"],
                        score=float(score),
                        paper_id=meta["paper_id"],
                        paper_title=meta["paper_title"],
                        page_num=meta.get("page_num"),
                    )
                )

            return results

        except Exception as e:
            logger.error("FAISS search failed: %s", e)
            raise VectorStoreError(f"Search failed: {e}") from e

    def save_index(self, directory: str | Path) -> None:
        """Save FAISS index and metadata to disk.

        Args:
            directory: Directory path to save files into.
        """
        if self.index is None:
            raise VectorStoreError("Cannot save uninitialized index.")

        dir_path = Path(directory)
        dir_path.mkdir(parents=True, exist_ok=True)
        
        index_path = dir_path / "vector_store.faiss"
        meta_path = dir_path / "vector_store_meta.json"

        try:
            faiss.write_index(self.index, str(index_path))
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f)
            logger.info("Saved FAISS index and metadata to %s", dir_path)
        except Exception as e:
            raise VectorStoreError(f"Failed to save index: {e}") from e

    def load_index(self, directory: str | Path) -> None:
        """Load FAISS index and metadata from disk.

        Args:
            directory: Directory path to load files from.
        """
        dir_path = Path(directory)
        index_path = dir_path / "vector_store.faiss"
        meta_path = dir_path / "vector_store_meta.json"

        if not index_path.exists() or not meta_path.exists():
            raise VectorStoreError(f"Index files not found in {dir_path}")

        try:
            self.index = faiss.read_index(str(index_path))
            self.dimension = self.index.d
            
            with open(meta_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
                
            logger.info("Loaded FAISS index with %d chunks from %s", self.get_total_chunks(), dir_path)
        except Exception as e:
            raise VectorStoreError(f"Failed to load index: {e}") from e

    def get_total_chunks(self) -> int:
        """Get the total number of chunks stored in the index."""
        if self.index is None:
            return 0
        return self.index.ntotal
