"""Tests for tools/pdf_tool.py — PDF download and text extraction."""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from app.tools.pdf_tool import download_pdf, extract_text_from_pdf, clean_text
from app.core.exceptions import PDFDownloadError, PDFParseError


# --- download_pdf tests ---


async def test_download_pdf_saves_file(tmp_path):
    """download_pdf should save the PDF to disk."""
    mock_response = MagicMock()
    mock_response.content = b"%PDF-1.4 fake pdf content"
    mock_response.headers = {"content-type": "application/pdf"}
    mock_response.raise_for_status = MagicMock()

    with patch("app.tools.pdf_tool.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_class.return_value.__aexit__ = AsyncMock(return_value=False)

        path = await download_pdf(
            "https://arxiv.org/pdf/2303.08774.pdf",
            save_dir=str(tmp_path),
        )

    assert path.exists()
    assert path.name == "2303.08774.pdf"
    assert path.read_bytes() == b"%PDF-1.4 fake pdf content"


async def test_download_pdf_caches_existing(tmp_path):
    """download_pdf should skip download if file already exists."""
    # Pre-create the file
    pdf_file = tmp_path / "2303.08774.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 cached content")

    with patch("app.tools.pdf_tool.httpx.AsyncClient") as mock_client_class:
        path = await download_pdf(
            "https://arxiv.org/pdf/2303.08774.pdf",
            save_dir=str(tmp_path),
        )
        # httpx should NOT have been called
        mock_client_class.assert_not_called()

    assert path == pdf_file


async def test_download_pdf_raises_on_network_error(tmp_path):
    """download_pdf should raise PDFDownloadError on network failure."""
    import httpx

    with patch("app.tools.pdf_tool.httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.HTTPError("Connection refused")
        mock_client_class.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_class.return_value.__aexit__ = AsyncMock(return_value=False)

        with pytest.raises(PDFDownloadError, match="PDF download failed"):
            await download_pdf(
                "https://arxiv.org/pdf/bad.pdf",
                save_dir=str(tmp_path),
            )


# --- extract_text_from_pdf tests ---


def test_extract_text_raises_on_missing_file():
    """extract_text_from_pdf should raise PDFParseError if file doesn't exist."""
    with pytest.raises(PDFParseError, match="PDF file not found"):
        extract_text_from_pdf(Path("/nonexistent/fake.pdf"))


# --- clean_text tests ---


def test_clean_text_fixes_hyphenated_breaks():
    """clean_text should join hyphenated line breaks."""
    text = "trans-\nformer models are power-\nful"
    result = clean_text(text)
    assert "transformer" in result
    assert "powerful" in result


def test_clean_text_collapses_whitespace():
    """clean_text should collapse multiple blank lines and spaces."""
    text = "Hello\n\n\n\n\nWorld\n\n\n\nTest   multiple   spaces"
    result = clean_text(text)
    assert "\n\n\n" not in result
    assert "   " not in result


def test_clean_text_removes_page_numbers():
    """clean_text should remove standalone page numbers."""
    text = "Some content\n 42 \nMore content"
    result = clean_text(text)
    assert "\n 42 \n" not in result
