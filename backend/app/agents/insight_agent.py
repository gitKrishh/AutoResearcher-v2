"""Insight Agent — identifies gaps, contradictions, and trends across papers."""

import logging

from app.core.config import settings
from app.core.prompts import INSIGHT_FIND_GAPS
from app.core.schemas import InsightReport, PaperAnalysis
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class InsightAgent:
    """Agent that synthesizes multiple paper analyses into high-level insights."""

    def __init__(self, llm_service: LLMService) -> None:
        self.llm = llm_service

    async def run(self, analyses: list[PaperAnalysis], topic: str) -> InsightReport | None:
        """Generate high-level insights (gaps, trends) across all papers.
        
        Args:
            analyses: List of structured paper analyses.
            topic: The main research topic.
            
        Returns:
            InsightReport containing synthesized insights, or None if it fails.
        """
        logger.info("InsightAgent started for topic: '%s' with %d analyses", topic, len(analyses))
        
        if not analyses:
            logger.warning("No analyses provided to InsightAgent.")
            return None

        summaries = "\n\n".join([f"Title: {a.title}\nFindings: {a.key_findings}" for a in analyses])
        prompt = INSIGHT_FIND_GAPS.format(
            paper_count=len(analyses),
            topic=topic,
            summaries=summaries
        )
        
        try:
            # We use complete_json as the prompt expects a JSON structure matching InsightReport
            result_json = await self.llm.complete_json(
                prompt, 
                model=settings.heavy_llm_model
            )
            
            insights = InsightReport(**result_json)
            logger.info("InsightAgent complete — successfully generated insights")
            return insights
            
        except Exception as e:
            logger.error("InsightAgent failed to generate insights: %s", e)
            return None
