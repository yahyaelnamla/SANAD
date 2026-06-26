"""pgvector client for similarity search."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.source import Source
from backend.app.models.source_chunk import SourceChunk
from rag.retrievers.base import RetrievedChunk, build_retrieved_chunk


class PgVectorClient:
    """Query pgvector for semantically similar source chunks."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def similarity_search(
        self,
        query_embedding: list[float],
        top_k: int = 10,
        authenticated_only: bool = True,
        language: str | None = None,
    ) -> list[RetrievedChunk]:
        """Perform cosine similarity search against stored embeddings."""
        distance = SourceChunk.embedding.cosine_distance(query_embedding)
        stmt = (
            select(SourceChunk, Source, distance.label("distance"))
            .join(Source, SourceChunk.source_id == Source.id)
            .where(SourceChunk.embedding.is_not(None))
        )
        if authenticated_only:
            stmt = stmt.where(Source.is_authenticated.is_(True))
        if language:
            stmt = stmt.where(Source.language == language)

        stmt = stmt.order_by(distance).limit(top_k)
        result = await self.session.execute(stmt)

        retrieved: list[RetrievedChunk] = []
        for chunk, source, dist in result.all():
            score = max(0.0, 1.0 - float(dist))
            retrieved.append(build_retrieved_chunk(chunk, source, score))

        return retrieved
