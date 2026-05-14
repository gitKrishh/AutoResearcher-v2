"""Analysis Agent — extracts structured summaries from papers."""

import logging
from typing import Any

from app.core.config import settings
from app.core.prompts import ANALYSIS_SUMMARIZE_PAPER
from app.core.schemas import PaperAnalysis, ProcessedPaper
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class AnalysisAgent:
    """Agent that analyzes papers and extracts structured insights."""

    def __init__(self, llm_service: LLMService) -> None:
        self.llm = llm_service

    async def run(self, papers: list[ProcessedPaper]) -> list[PaperAnalysis]:
        """Analyze a list of processed papers.
        
        Args:
            papers: List of ProcessedPaper objects containing full text.
            
        Returns:
            List of PaperAnalysis objects containing structured summaries.
        """
        logger.info("AnalysisAgent started for %d papers", len(papers))
        analyses = []

        for paper in papers:
            logger.info("Analyzing paper: %s", paper.title)
            # Use heavy model for analysis as it requires high reasoning capability
            model = settings.heavy_llm_model
            
            # Truncate content to avoid exceeding context limits. 
            # (e.g. keeping first ~50k chars is usually safe for large models,
            # or could use chunking but for MVP we truncate to 30000 chars)
            max_chars = 30000 
            content = paper.full_text[:max_chars]
            if len(paper.full_text) > max_chars:
                content += "\n... [Content truncated due to length limits]"
                
            prompt = ANALYSIS_SUMMARIZE_PAPER.format(
                title=paper.title,
                content=content
            )

            try:
                result_json = await self.llm.complete_json(prompt, model=settings.analyzer_model)
                
                # Build PaperAnalysis from JSON
                analysis = PaperAnalysis(
                    id=paper.id,
                    title=paper.title,
                    abstract=paper.abstract,
                    authors=paper.authors,
                    pdf_url=paper.pdf_url,
                    published=paper.published,
                    source=paper.source,
                    summary=result_json.get("summary", "N/A"),
                    methodology=result_json.get("methodology", "N/A"),
                    datasets=result_json.get("datasets", "N/A"),
                    key_findings=result_json.get("key_findings", "N/A"),
                    limitations=result_json.get("limitations", "N/A"),
                    contribution=result_json.get("contribution", "N/A"),
                )
                analyses.append(analysis)
                logger.debug("Successfully analyzed: %s", paper.title)
            except Exception as e:
                logger.error("Failed to analyze paper %s: %s", paper.title, e)
                # Append a fallback analysis so the pipeline doesn't break completely
                fallback = PaperAnalysis(
                    id=paper.id,
                    title=paper.title,
                    abstract=paper.abstract,
                    authors=paper.authors,
                    pdf_url=paper.pdf_url,
                    published=paper.published,
                    source=paper.source,
                    summary="Analysis failed due to error.",
                    methodology="N/A",
                    datasets="N/A",
                    key_findings="N/A",
                    limitations="N/A",
                    contribution="N/A",
                )
                analyses.append(fallback)

        logger.info("AnalysisAgent complete — analyzed %d/%d papers successfully", 
                    len([a for a in analyses if "Analysis failed" not in a.summary]), 
                    len(papers))
        return analyses
