"""Writer Agent — generates the final literature review and insights."""

import datetime
import json
import logging
from typing import Any

from app.core.config import settings
from app.core.prompts import (
    ANALYSIS_COMPARE_PAPERS,
    INSIGHT_FIND_GAPS,
    WRITER_LITERATURE_REVIEW,
)
from app.core.schemas import FinalReport, InsightReport, PaperAnalysis
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class WriterAgent:
    """Agent that compiles paper analyses into a final structured literature review."""

    def __init__(self, llm_service: LLMService) -> None:
        self.llm = llm_service

    async def _generate_comparison(self, analyses: list[PaperAnalysis]) -> dict[str, Any]:
        """Generate a comparison of methodologies across papers."""
        summaries = "\n\n".join([f"Title: {a.title}\nSummary: {a.summary}\nMethodology: {a.methodology}" for a in analyses])
        prompt = ANALYSIS_COMPARE_PAPERS.format(paper_summaries=summaries)
        
        try:
            return await self.llm.complete_json(prompt, model=settings.heavy_llm_model)
        except Exception as e:
            logger.error("Failed to generate comparison: %s", e)
            return {"error": "Failed to generate comparison."}

    async def run(self, topic: str, analyses: list[PaperAnalysis], insights: InsightReport | None = None) -> FinalReport:
        """Run the full writing pipeline.
        
        Generates paper comparisons and writes the final literature review markdown.
        """
        logger.info("WriterAgent started for topic: '%s' with %d analyses", topic, len(analyses))
        
        if not analyses:
            logger.warning("No analyses provided to WriterAgent. Returning empty report.")
            return FinalReport(
                topic=topic,
                paper_count=0,
                papers=[],
                literature_review="No relevant papers were found to review.",
                insights=insights,
                generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat()
            )

        # 1. Generate comparison
        logger.info("Generating paper comparisons...")
        comparison = await self._generate_comparison(analyses)

        # 2. Prepare data for the writer prompt
        summaries_text = "\n\n".join([
            f"Title: {a.title}\nAuthors: {', '.join(a.authors)}\nSummary: {a.summary}\nFindings: {a.key_findings}\nLimitations: {a.limitations}"
            for a in analyses
        ])
        
        comparison_text = json.dumps(comparison, indent=2)
        insights_text = insights.model_dump_json(indent=2) if insights else "No insights available."

        # 3. Generate the actual literature review
        logger.info("Writing final literature review...")
        review_prompt = WRITER_LITERATURE_REVIEW.format(
            topic=topic,
            paper_count=len(analyses),
            summaries=summaries_text,
            comparison=comparison_text,
            insights=insights_text
        )
        
        try:
            review_markdown = await self.llm.complete(
                review_prompt, 
                model=settings.heavy_llm_model,
                temperature=0.4
            )
        except Exception as e:
            logger.error("Failed to generate literature review: %s", e)
            review_markdown = "An error occurred while generating the literature review."

        logger.info("WriterAgent complete for topic: '%s'", topic)
        
        # 4. Construct and return the FinalReport
        return FinalReport(
            topic=topic,
            paper_count=len(analyses),
            papers=analyses,
            literature_review=review_markdown.strip(),
            insights=insights,
            generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat()
        )
