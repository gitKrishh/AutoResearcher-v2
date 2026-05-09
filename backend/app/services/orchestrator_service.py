"""Orchestrator Service — the master controller for the entire research pipeline."""

import logging

from app.agents.analysis_agent import AnalysisAgent
from app.agents.embedding_agent import EmbeddingAgent
from app.agents.insight_agent import InsightAgent
from app.agents.pdf_agent import PDFAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.search_agent import SearchAgent
from app.agents.writer_agent import WriterAgent
from app.core.schemas import FinalReport
from app.services.llm_service import LLMService
from app.services.vector_store_service import VectorStoreService

logger = logging.getLogger(__name__)


class OrchestratorService:
    """Orchestrates the entire multi-agent research pipeline."""

    def __init__(self, llm_service: LLMService, vector_store: VectorStoreService):
        self.llm_service = llm_service
        self.vector_store = vector_store
        
        # Initialize all agents
        self.planner = PlannerAgent(llm_service=llm_service)
        self.searcher = SearchAgent()
        self.pdf_agent = PDFAgent()
        self.embedder = EmbeddingAgent(vector_store=vector_store)
        self.analyzer = AnalysisAgent(llm_service=llm_service)
        self.insighter = InsightAgent(llm_service=llm_service)
        self.writer = WriterAgent(llm_service=llm_service)

    async def run_research(self, topic: str, max_papers: int = 10) -> FinalReport:
        """Execute the full autonomous research pipeline.
        
        Args:
            topic: The research topic provided by the user.
            max_papers: Maximum number of papers to fetch and analyze.
            
        Returns:
            A FinalReport containing the literature review and insights.
        """
        logger.info("="*50)
        logger.info("STARTING FULL RESEARCH PIPELINE FOR TOPIC: '%s'", topic)
        logger.info("="*50)

        try:
            # 1. Plan
            logger.info("--- Phase 1: Planning ---")
            sub_topics = await self.planner.run(topic)
            logger.info("Generated sub-topics: %s", sub_topics)

            # 2. Search
            logger.info("--- Phase 2: Searching ---")
            # For each sub-topic, get some papers, but limit total to max_papers
            papers = await self.searcher.run(sub_topics, max_results_per_topic=3)
            # Limit exactly to max_papers to avoid overloading
            papers = papers[:max_papers]
            logger.info("Found %d unique papers across all sub-topics.", len(papers))

            if not papers:
                raise ValueError(f"No papers found for topic: {topic}")

            # 3. Download & Extract PDFs
            logger.info("--- Phase 3: Processing PDFs ---")
            processed_papers = await self.pdf_agent.run(papers)
            logger.info("Successfully extracted text from %d papers.", len(processed_papers))

            if not processed_papers:
                raise ValueError("Failed to extract text from any downloaded PDFs.")

            # 4. Embed & Store in FAISS
            logger.info("--- Phase 4: Vectorizing ---")
            total_chunks = await self.embedder.run(processed_papers)
            logger.info("Stored %d vector chunks in FAISS.", total_chunks)

            # 5. Analyze Papers
            logger.info("--- Phase 5: Deep Analysis ---")
            analyses = await self.analyzer.run(processed_papers)
            logger.info("Completed analysis for %d papers.", len(analyses))

            # 6. Generate Insights
            logger.info("--- Phase 6: Extracting Insights ---")
            insights = await self.insighter.run(analyses, topic)

            # 7. Write Final Report
            logger.info("--- Phase 7: Writing Literature Review ---")
            final_report = await self.writer.run(topic, analyses, insights=insights)
            
            logger.info("="*50)
            logger.info("RESEARCH PIPELINE COMPLETED SUCCESSFULLY")
            logger.info("="*50)
            
            return final_report

        except Exception as e:
            logger.error("RESEARCH PIPELINE FAILED: %s", e, exc_info=True)
            raise
