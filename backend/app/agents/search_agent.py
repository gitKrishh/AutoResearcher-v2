"""Search Agent — fetches papers from academic APIs.

Iterates over sub-topics, calls search_tool for each,
deduplicates results, and handles partial failures.
"""

import logging

from app.core.exceptions import SearchError
from app.core.schemas import Paper
from app.services.llm_service import LLMService
from app.tools.search_tool import search_arxiv

logger = logging.getLogger(__name__)


class SearchAgent:
    """Agent responsible for searching academic papers.

    Takes a list of search sub-topics and returns deduplicated papers.
    Tolerates partial failures — if one topic fails, the rest continue.
    """

    def __init__(self, llm_service: LLMService | None = None) -> None:
        """Initialize SearchAgent.

        Args:
            llm_service: Optional LLM service for relevance filtering (post-MVP).
        """
        self.llm = llm_service

    async def run(
        self,
        sub_topics: list[str],
        max_per_topic: int = 5,
    ) -> list[Paper]:
        """Search arXiv for papers matching the given sub-topics.

        Args:
            sub_topics: List of search queries (e.g. from PlannerAgent).
            max_per_topic: Max papers to fetch per sub-topic.

        Returns:
            Deduplicated list of Paper objects from all sub-topics.
        """
        logger.info(
            "SearchAgent started for %d sub-topics: %s",
            len(sub_topics),
            sub_topics,
        )

        all_papers: list[Paper] = []

        for topic in sub_topics:
            try:
                papers = await search_arxiv(topic, max_per_topic)
                all_papers.extend(papers)
                logger.debug(
                    "Found %d papers for topic: '%s'", len(papers), topic
                )
            except SearchError:
                logger.warning(
                    "Search failed for topic: '%s' — skipping", topic
                )
                continue

        # Deduplicate by paper ID
        deduplicated = _deduplicate_papers(all_papers)

        logger.info(
            "SearchAgent complete — %d papers found, %d after dedup",
            len(all_papers),
            len(deduplicated),
        )

        return deduplicated


def _deduplicate_papers(papers: list[Paper]) -> list[Paper]:
    """Remove duplicate papers by ID, keeping first occurrence.

    Args:
        papers: List of papers that may contain duplicates.

    Returns:
        Deduplicated list preserving original order.
    """
    seen: set[str] = set()
    unique: list[Paper] = []

    for paper in papers:
        if paper.id not in seen:
            seen.add(paper.id)
            unique.append(paper)

    return unique
