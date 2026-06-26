"""Keyword-based retriever using PostgreSQL full-text search."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.source import Source
from backend.app.models.source_chunk import SourceChunk
from rag.retrievers.base import RetrievedChunk, build_retrieved_chunk


class KeywordRetriever:
    """Retrieve chunks via PostgreSQL full-text keyword matching."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def retrieve(
        self,
        query: str,
        top_k: int = 10,
        language: str | None = None,
    ) -> list[RetrievedChunk]:
        """Return top-k authenticated chunks matching query keywords."""
        ts_vector = func.to_tsvector("simple", SourceChunk.content)
        ts_query = func.plainto_tsquery("simple", query)
        rank = func.ts_rank(ts_vector, ts_query).label("rank")

        stmt = (
            select(SourceChunk, Source, rank)
            .join(Source, SourceChunk.source_id == Source.id)
            .where(Source.is_authenticated.is_(True))
            .where(ts_vector.op("@@")(ts_query))
        )
        if language:
            stmt = stmt.where(Source.language == language)

        stmt = stmt.order_by(rank.desc()).limit(top_k)
        result = await self.session.execute(stmt)

        retrieved: list[RetrievedChunk] = []
        for chunk, source, rank_value in result.all():
            score = float(rank_value or 0.0)
            retrieved.append(build_retrieved_chunk(chunk, source, score))

        return retrieved
