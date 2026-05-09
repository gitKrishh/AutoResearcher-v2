"""PDF Agent — downloads and extracts text from paper PDFs.

Takes a list of Paper objects, downloads their PDFs,
extracts and cleans text, and returns ProcessedPaper objects.
Tolerates partial failures — if one PDF fails, the rest continue.
"""

import asyncio
import logging

from app.core.exceptions import PDFDownloadError, PDFParseError
from app.core.schemas import Paper, ProcessedPaper
from app.tools.pdf_tool import download_pdf, extract_text_from_pdf

logger = logging.getLogger(__name__)


class PDFAgent:
    """Agent responsible for downloading and processing paper PDFs.

    Downloads each paper's PDF, extracts text using PyMuPDF,
    and returns ProcessedPaper objects with the full text included.
    """

    def __init__(self) -> None:
        """Initialize PDFAgent. No dependencies needed."""
        pass

    async def run(self, papers: list[Paper]) -> list[ProcessedPaper]:
        """Download and extract text from all paper PDFs.

        Skips individual papers that fail (logs warning, continues with rest).
        CPU-bound PDF extraction runs via asyncio.to_thread().

        Args:
            papers: List of Paper objects with pdf_url fields.

        Returns:
            List of ProcessedPaper objects with extracted text.
        """
        logger.info("PDFAgent started for %d papers", len(papers))

        processed: list[ProcessedPaper] = []

        for paper in papers:
            try:
                result = await self._process_single(paper)
                processed.append(result)
                logger.debug(
                    "Processed: '%s' — %d chars",
                    paper.title[:60],
                    result.text_length,
                )
            except (PDFDownloadError, PDFParseError) as e:
                logger.warning(
                    "Skipping paper '%s': %s",
                    paper.title[:60],
                    e,
                )
                continue

        logger.info(
            "PDFAgent complete — processed %d/%d papers",
            len(processed),
            len(papers),
        )

        return processed

    async def _process_single(self, paper: Paper) -> ProcessedPaper:
        """Download and extract text from a single paper.

        Args:
            paper: Paper object with pdf_url.

        Returns:
            ProcessedPaper with full_text populated.

        Raises:
            PDFDownloadError: If download fails.
            PDFParseError: If text extraction fails.
        """
        # Download PDF (async I/O)
        pdf_path = await download_pdf(paper.pdf_url)

        # Extract text (CPU-bound → run in thread to not block event loop)
        text = await asyncio.to_thread(extract_text_from_pdf, pdf_path)

        # Count pages from the PDF
        import fitz
        doc = fitz.open(str(pdf_path))
        page_count = len(doc)
        doc.close()

        return ProcessedPaper(
            id=paper.id,
            title=paper.title,
            abstract=paper.abstract,
            authors=paper.authors,
            pdf_url=paper.pdf_url,
            published=paper.published,
            source=paper.source,
            full_text=text,
            page_count=page_count,
            text_length=len(text),
        )
