"""Vector-based retriever using pgvector."""

from sqlalchemy.ext.asyncio import AsyncSession

from rag.retrievers.base import RetrievedChunk
from rag.vectorstore.pgvector_client import PgVectorClient


class VectorRetriever:
    """Retrieve chunks via semantic vector similarity."""

    def __init__(self, session: AsyncSession) -> None:
        self.client = PgVectorClient(session)

    async def retrieve(
        self,
        query_embedding: list[float],
        top_k: int = 10,
        language: str | None = None,
    ) -> list[RetrievedChunk]:
        """Return top-k authenticated chunks by vector similarity."""
        return await self.client.similarity_search(
            query_embedding=query_embedding,
            top_k=top_k,
            authenticated_only=True,
            language=language,
        )
