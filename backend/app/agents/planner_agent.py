"""Planner Agent — decomposes a main topic into specific search queries."""

import logging

from app.core.config import settings
from app.core.prompts import PLANNER_DECOMPOSE_QUERY
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class PlannerAgent:
    """Agent that breaks down a complex research topic into focused search queries."""

    def __init__(self, llm_service: LLMService) -> None:
        self.llm = llm_service

    async def run(self, topic: str) -> list[str]:
        """Decompose a research topic into multiple sub-topics for search.
        
        Args:
            topic: The main research topic provided by the user.
            
        Returns:
            A list of 3-5 specific search queries (strings).
        """
        logger.info("PlannerAgent started for topic: '%s'", topic)
        
        prompt = PLANNER_DECOMPOSE_QUERY.format(query=topic)
        
        try:
            # We use complete_json because the prompt specifically asks for a JSON array
            sub_topics = await self.llm.complete_json(
                prompt,
                model=settings.planner_model
            )
            
            if not isinstance(sub_topics, list) or not all(isinstance(t, str) for t in sub_topics):
                logger.error("PlannerAgent returned invalid format: %s", sub_topics)
                return [topic]
                
            logger.info("PlannerAgent complete — generated %d sub-topics", len(sub_topics))
            return sub_topics
            
        except Exception as e:
            logger.error("PlannerAgent failed: %s", e)
            # Fallback to just searching the original topic if planning fails
            return [topic]
