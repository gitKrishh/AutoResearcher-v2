"""PDF tool — download PDFs and extract text.

Pure utility functions for downloading academic paper PDFs
and extracting clean text using PyMuPDF (fitz).
No LLM calls, no agent logic.
"""

import logging
import re
from pathlib import Path

import fitz  # PyMuPDF
import httpx

from app.core.config import settings
from app.core.exceptions import PDFDownloadError, PDFParseError

logger = logging.getLogger(__name__)


async def download_pdf(url: str, save_dir: str | None = None) -> Path:
    """Download a PDF from a URL, caching locally.

    Skips download if the file already exists (cache hit).

    Args:
        url: URL of the PDF to download.
        save_dir: Directory to save the PDF. Defaults to settings.pdf_cache_dir.

    Returns:
        Path to the downloaded PDF file.

    Raises:
        PDFDownloadError: If the download fails.
    """
    save_dir = save_dir or settings.pdf_cache_dir
    save_path = Path(save_dir)
    save_path.mkdir(parents=True, exist_ok=True)

    # Extract filename from URL (e.g. "2303.08774.pdf")
    filename = url.rstrip("/").split("/")[-1]
    if not filename.endswith(".pdf"):
        filename += ".pdf"

    file_path = save_path / filename

    # Cache hit — skip download
    if file_path.exists() and file_path.stat().st_size > 0:
        logger.debug("PDF cache hit: %s", file_path)
        return file_path

    logger.info("Downloading PDF: %s → %s", url, file_path)

    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()

            # Verify it's actually a PDF
            content_type = response.headers.get("content-type", "")
            if "pdf" not in content_type and not response.content[:5] == b"%PDF-":
                raise PDFDownloadError(
                    f"URL did not return a PDF (content-type: {content_type})"
                )

            file_path.write_bytes(response.content)
            logger.info(
                "PDF downloaded: %s (%.1f KB)",
                file_path,
                len(response.content) / 1024,
            )

    except httpx.HTTPError as e:
        logger.error("PDF download failed for %s: %s", url, e)
        raise PDFDownloadError(f"PDF download failed: {e}") from e

    return file_path


def extract_text_from_pdf(
    pdf_path: Path,
    max_pages: int | None = None,
) -> str:
    """Extract text from a PDF file using PyMuPDF.

    Args:
        pdf_path: Path to the PDF file.
        max_pages: Maximum number of pages to extract. Defaults to settings.max_pdf_pages.

    Returns:
        Extracted text as a single string.

    Raises:
        PDFParseError: If the PDF cannot be opened or contains no text.
    """
    max_pages = max_pages or settings.max_pdf_pages

    if not pdf_path.exists():
        raise PDFParseError(f"PDF file not found: {pdf_path}")

    logger.info("Extracting text from: %s", pdf_path)

    try:
        doc = fitz.open(str(pdf_path))
    except Exception as e:
        raise PDFParseError(f"Failed to open PDF: {pdf_path} — {e}") from e

    pages_to_read = min(len(doc), max_pages)
    page_texts: list[str] = []

    for page_num in range(pages_to_read):
        try:
            page = doc[page_num]
            text = page.get_text("text")
            if text.strip():
                page_texts.append(text)
        except Exception as e:
            logger.warning(
                "Failed to extract page %d from %s: %s", page_num + 1, pdf_path, e
            )
            continue

    doc.close()

    if not page_texts:
        raise PDFParseError(f"No text extracted from PDF: {pdf_path}")

    full_text = "\n\n".join(page_texts)
    cleaned = clean_text(full_text)

    logger.info(
        "Extracted %d chars from %d/%d pages: %s",
        len(cleaned),
        len(page_texts),
        pages_to_read,
        pdf_path,
    )

    return cleaned


def clean_text(text: str) -> str:
    """Remove noise from extracted PDF text.

    Cleans up common PDF extraction artifacts:
    - Excessive whitespace and blank lines
    - Page numbers
    - Running headers/footers
    - Hyphenated line breaks

    Args:
        text: Raw extracted text.

    Returns:
        Cleaned text string.
    """
    # Fix hyphenated line breaks (e.g. "trans-\nformer" → "transformer")
    text = re.sub(r"-\n(\S)", r"\1", text)

    # Collapse multiple newlines into double newlines (paragraph breaks)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove standalone page numbers (lines that are just a number)
    text = re.sub(r"\n\s*\d{1,3}\s*\n", "\n", text)

    # Collapse multiple spaces into single space
    text = re.sub(r" {2,}", " ", text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text
