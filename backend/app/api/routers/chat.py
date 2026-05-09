"""Chat route — POST /api/chat.

Allows users to ask follow-up questions about the research context.
"""

import logging
from pydantic import BaseModel
from fastapi import APIRouter, Depends

from app.api.deps import get_llm_service, get_vector_store
from app.agents.retrieval_agent import RetrievalAgent
from app.core.schemas import APIResponse, APIError
from app.services.llm_service import LLMService
from app.services.vector_store_service import VectorStoreService

logger = logging.getLogger(__name__)

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    top_k: int = 5

@router.post("/chat", response_model=APIResponse)
async def chat_with_context(
    request: ChatRequest,
    llm: LLMService = Depends(get_llm_service),
    vector_store: VectorStoreService = Depends(get_vector_store),
) -> APIResponse:
    """Ask a question based on currently indexed papers."""
    logger.info("Handling chat request: '%s'", request.query)
    
    try:
        agent = RetrievalAgent(llm_service=llm, vector_store=vector_store)
        answer = await agent.run(query=request.query, top_k=request.top_k)
        
        return APIResponse(
            success=True,
            data={"answer": answer}
        )
    except Exception as e:
        logger.error("Chat failed: %s", e)
        return APIResponse(
            success=False,
            error=APIError(code="CHAT_FAILED", message=str(e))
        )
