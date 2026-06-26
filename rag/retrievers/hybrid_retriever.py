"""Hybrid retriever combining vector and keyword search."""

from sqlalchemy.ext.asyncio import AsyncSession

from rag.rerankers.score_fusion import reciprocal_rank_fusion
from rag.retrievers.base import RetrievedChunk
from rag.retrievers.keyword_retriever import KeywordRetriever
from rag.retrievers.vector_retriever import VectorRetriever


class HybridRetriever:
    """Combine vector and keyword retrieval with reciprocal rank fusion."""

    def __init__(self, session: AsyncSession) -> None:
        self.vector_retriever = VectorRetriever(session)
        self.keyword_retriever = KeywordRetriever(session)

    async def retrieve(
        self,
        query: str,
        query_embedding: list[float],
        top_k: int = 10,
        language: str | None = None,
    ) -> list[RetrievedChunk]:
        """Retrieve and fuse vector + keyword results."""
        vector_results = await self.vector_retriever.retrieve(
            query_embedding=query_embedding,
            top_k=top_k,
            language=language,
        )
        keyword_results = await self.keyword_retriever.retrieve(
            query=query,
            top_k=top_k,
            language=language,
        )
        return reciprocal_rank_fusion([vector_results, keyword_results], top_k=top_k)
