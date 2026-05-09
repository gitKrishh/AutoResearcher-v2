"""Tests for tools/chunking_tool.py — text splitting."""

from app.tools.chunking_tool import chunk_text


def test_chunk_text_returns_list_of_strings():
    """chunk_text should return a list of string chunks."""
    text = "This is a simple test sentence. " * 10
    chunks = chunk_text(text, chunk_size=50, chunk_overlap=10)
    
    assert isinstance(chunks, list)
    assert len(chunks) > 0
    assert all(isinstance(c, str) for c in chunks)


def test_chunk_text_respects_chunk_size():
    """Chunks should generally not exceed the requested chunk_size."""
    text = "This is a long sentence to test chunking limits without newlines. " * 20
    chunk_size = 100
    chunks = chunk_text(text, chunk_size=chunk_size, chunk_overlap=20)
    
    for chunk in chunks:
        # Langchain text splitter is approximate when exact splits aren't possible,
        # but it should stay close to chunk_size
        assert len(chunk) <= chunk_size + 20


def test_chunk_text_handles_empty_text():
    """chunk_text should return empty list for empty or whitespace text."""
    assert chunk_text("") == []
    assert chunk_text("   \n  ") == []
    assert chunk_text(None) == []


def test_chunk_text_filters_tiny_chunks():
    """chunk_text should filter out chunks smaller than 50 characters."""
    text = "A very short text."
    chunks = chunk_text(text)
    # The text is < 50 chars, so it should be filtered out
    assert chunks == []
    
    # Text > 50 chars should be kept
    long_text = "This is a reasonably long text that exceeds the fifty character minimum threshold."
    long_chunks = chunk_text(long_text)
    assert len(long_chunks) == 1
    assert long_chunks[0] == long_text
