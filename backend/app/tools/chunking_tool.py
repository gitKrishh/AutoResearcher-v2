"""Chunking tool — split text into overlapping chunks.

Uses LangChain's RecursiveCharacterTextSplitter for reliable,
semantically-aware text splitting. This is a pure tool function —
no LLM calls, no agent logic.
"""

import logging

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings

logger = logging.getLogger(__name__)

# Minimum chunk length to keep — filters out headers, footers, tiny fragments
MIN_CHUNK_LENGTH = 50


def chunk_text(
    text: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[str]:
    """Split text into overlapping chunks using recursive character splitting.

    Splits on paragraph boundaries first, then sentences, then words.
    Filters out very short chunks (< 50 chars) that are typically noise.

    Args:
        text: The full text to split.
        chunk_size: Max characters per chunk. Defaults to settings.chunk_size.
        chunk_overlap: Overlap between consecutive chunks. Defaults to settings.chunk_overlap.

    Returns:
        List of text chunks. Returns empty list if text is empty or too short.
    """
    if not text or not text.strip():
        logger.debug("chunk_text called with empty text — returning []")
        return []

    chunk_size = chunk_size or settings.chunk_size
    chunk_overlap = chunk_overlap or settings.chunk_overlap

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )

    raw_chunks = splitter.split_text(text)

    # Filter out tiny chunks (headers, footers, page numbers, etc.)
    chunks = [c for c in raw_chunks if len(c.strip()) >= MIN_CHUNK_LENGTH]

    logger.info(
        "Chunked text: %d chars → %d raw chunks → %d after filtering (size=%d, overlap=%d)",
        len(text),
        len(raw_chunks),
        len(chunks),
        chunk_size,
        chunk_overlap,
    )

    return chunks
