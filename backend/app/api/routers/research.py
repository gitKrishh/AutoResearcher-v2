"""Research route — POST /api/research.

This is a simplified MVP pipeline that runs the core agents sequentially:
Search -> PDF Download -> Chunk & Embed -> Retrieve -> Answer.
No complex orchestration or sub-topic planning yet.
"""

import logging

from fastapi import APIRouter, Depends

from app.agents.embedding_agent import EmbeddingAgent
from app.agents.pdf_agent import PDFAgent
from app.agents.retrieval_agent import RetrievalAgent
from app.agents.search_agent import SearchAgent
from app.api.deps import get_llm_service, get_vector_store
from app.core.exceptions import AutoResearcherError
from app.core.schemas import APIError, APIResponse, ResearchRequest
from app.services.llm_service import LLMService
from app.services.vector_store_service import VectorStoreService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/research", response_model=APIResponse)
async def conduct_research(
    request: ResearchRequest,
    llm: LLMService = Depends(get_llm_service),
    vector_store: VectorStoreService = Depends(get_vector_store),
) -> APIResponse:
    """End-to-end research pipeline (MVP).

    Takes a topic, searches for papers, downloads them, stores them in FAISS,
    and then asks the LLM to provide insights based on the retrieved data.
    """
    logger.info("Starting research pipeline MVP for topic: '%s'", request.topic)

    try:
        # 1. Search Agent
        search_agent = SearchAgent(llm_service=llm)
        papers = await search_agent.run([request.topic], max_per_topic=request.max_papers)

        if not papers:
            return APIResponse(
                success=False,
                error=APIError(
                    code="NO_PAPERS_FOUND",
                    message="Could not find any relevant papers for the given topic.",
                ),
            )

        # 2. PDF Agent
        pdf_agent = PDFAgent()
        processed_papers = await pdf_agent.run(papers)

        if not processed_papers:
            return APIResponse(
                success=False,
                error=APIError(
                    code="PDF_DOWNLOAD_FAILED",
                    message="Found papers, but could not download or parse any of their PDFs.",
                ),
            )

        # 3. Embedding Agent
        embedding_agent = EmbeddingAgent(vector_store=vector_store)
        chunk_ids = await embedding_agent.run(processed_papers)
        
        if not chunk_ids:
            return APIResponse(
                success=False,
                error=APIError(
                    code="EMBEDDING_FAILED",
                    message="Failed to extract and embed chunks from the downloaded papers.",
                ),
            )

        # 4. Retrieval Agent (generate answer/insights)
        if request.include_insights:
            retrieval_agent = RetrievalAgent(llm_service=llm, vector_store=vector_store)
            
            # Use the original topic as the query for now
            query = f"Provide a comprehensive summary of recent research findings regarding: {request.topic}"
            answer = await retrieval_agent.run(query=query, top_k=10)
        else:
            answer = "Insights generation was disabled for this request."

        return APIResponse(
            success=True,
            data={
                "topic": request.topic,
                "papers_processed": len(processed_papers),
                "chunks_embedded": len(chunk_ids),
                "insights": answer,
                "sources": [p.model_dump(exclude={"full_text"}) for p in processed_papers]
            },
            meta={
                "pipeline": "mvp_sequential"
            }
        )

    except AutoResearcherError as e:
        # Let the global exception handler deal with structured logging and responses
        # if we want, but since we are in a route, we can just return a clean APIResponse.
        # Alternatively, raise e and let main.py catch it. We'll return it directly here.
        logger.error("Research pipeline failed: %s", e)
        return APIResponse(
            success=False,
            error=APIError(
                code=type(e).__name__.upper(),
                message=str(e),
            ),
        )
    except Exception as e:
        logger.error("Unexpected error in research pipeline: %s", e)
        return APIResponse(
            success=False,
            error=APIError(
                code="INTERNAL_ERROR",
                message=f"An unexpected error occurred: {e}",
            ),
        )
