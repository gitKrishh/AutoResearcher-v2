"""Embedding Agent — processes full papers into vector chunks.

Takes ProcessedPaper objects (with full_text), chunks the text,
generates embeddings, and stores them in the FAISS vector store.
"""

import logging
from typing import Any

from app.core.exceptions import EmbeddingError, VectorStoreError
from app.core.schemas import ProcessedPaper
from app.services.vector_store_service import VectorStoreService
from app.tools.chunking_tool import chunk_text
from app.tools.embedding_tool import create_embeddings

logger = logging.getLogger(__name__)


class EmbeddingAgent:
    """Agent responsible for chunking, embedding, and storing papers."""

    def __init__(self, vector_store: VectorStoreService) -> None:
        """Initialize EmbeddingAgent.

        Args:
            vector_store: The vector store service instance.
        """
        self.vector_store = vector_store

    async def run(self, papers: list[ProcessedPaper]) -> list[str]:
        """Process a list of papers and store them in the vector database.

        For each paper:
        1. Chunks the full text.
        2. Generates vector embeddings for all chunks.
        3. Prepares metadata (paper ID, title, etc.).
        4. Adds chunks and vectors to FAISS.

        Args:
            papers: List of ProcessedPaper objects containing full text.

        Returns:
            List of generated chunk IDs across all papers.
        """
        logger.info("EmbeddingAgent started for %d papers", len(papers))

        all_chunk_ids: list[str] = []

        for paper in papers:
            try:
                # 1. Chunking
                chunks = chunk_text(paper.full_text)
                if not chunks:
                    logger.warning("Paper '%s' yielded 0 chunks. Skipping.", paper.title)
                    continue

                # 2. Embedding
                # This could be CPU intensive, but create_embeddings handles it.
                # Since we don't have async embedding yet, we just call it directly.
                embeddings = create_embeddings(chunks)

                # 3. Metadata Preparation
                # We don't have page level granularity from pure text right now,
                # but we could approximate or just leave it out.
                metadata: list[dict[str, Any]] = [
                    {
                        "paper_id": paper.id,
                        "paper_title": paper.title,
                    }
                    for _ in chunks
                ]

                # 4. Storage
                chunk_ids = self.vector_store.add_chunks(
                    chunks=chunks,
                    embeddings=embeddings,
                    chunk_metadata=metadata,
                )
                
                all_chunk_ids.extend(chunk_ids)
                logger.debug("Paper '%s' -> %d chunks stored", paper.title[:50], len(chunks))

            except (EmbeddingError, VectorStoreError) as e:
                logger.error("Failed to process paper '%s': %s", paper.title, e)
                continue

        logger.info(
            "EmbeddingAgent complete — stored %d total chunks", len(all_chunk_ids)
        )

        return all_chunk_ids
