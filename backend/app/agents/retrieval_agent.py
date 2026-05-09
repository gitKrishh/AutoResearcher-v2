"""Retrieval Agent — searches FAISS and answers questions.

Embeds a user query, searches the vector database for relevant chunks,
formats them as context, and calls the LLM to generate an answer.
"""

import logging

from app.core.exceptions import RetrievalError
from app.core.prompts import RETRIEVAL_ANSWER_QUESTION
from app.services.llm_service import LLMService
from app.services.vector_store_service import VectorStoreService
from app.tools.embedding_tool import embed_query

logger = logging.getLogger(__name__)


class RetrievalAgent:
    """Agent responsible for RAG retrieval and question answering."""

    def __init__(
        self,
        llm_service: LLMService,
        vector_store: VectorStoreService,
    ) -> None:
        """Initialize RetrievalAgent.

        Args:
            llm_service: Service to communicate with the LLM.
            vector_store: Service to query FAISS index.
        """
        self.llm = llm_service
        self.vector_store = vector_store

    async def run(self, query: str, top_k: int = 5) -> str:
        """Answer a question using retrieved chunks from the vector store.

        Args:
            query: The user's question.
            top_k: Number of relevant chunks to retrieve.

        Returns:
            The LLM-generated answer string.

        Raises:
            RetrievalError: If search or LLM generation fails.
        """
        logger.info("RetrievalAgent started for query: '%s'", query)

        try:
            # 1. Embed the query
            query_embedding = embed_query(query)

            # 2. Search FAISS
            results = self.vector_store.search(query_embedding, top_k=top_k)

            if not results:
                logger.warning("No relevant chunks found in vector store.")
                return "The retrieved papers do not contain enough information to answer this question."

            # 3. Format context
            context_blocks = []
            for i, res in enumerate(results):
                block = f"[Source {i+1}: {res.paper_title}]\n{res.text}"
                context_blocks.append(block)

            context_str = "\n\n---\n\n".join(context_blocks)
            logger.debug(
                "Retrieved %d chunks. Context length: %d chars",
                len(results),
                len(context_str),
            )

            # 4. Call LLM
            prompt = RETRIEVAL_ANSWER_QUESTION.format(
                question=query,
                context=context_str,
            )

            answer = await self.llm.complete(prompt)

            logger.info("RetrievalAgent complete. Answer length: %d chars", len(answer))
            return answer

        except Exception as e:
            logger.error("RetrievalAgent failed: %s", e)
            raise RetrievalError(f"RAG failure: {e}") from e
