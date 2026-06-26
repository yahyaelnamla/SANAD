"""Source chunk repository with vector-aware queries."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.source_chunk import SourceChunk
from backend.app.repositories.base import BaseRepository


class SourceChunkRepository(BaseRepository[SourceChunk]):
    """Data access for RAG source chunks."""

    model = SourceChunk

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_by_source(
        self,
        source_id: uuid.UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[SourceChunk]:
        """Return chunks belonging to a source, ordered by index."""
        stmt = (
            select(SourceChunk)
            .where(SourceChunk.source_id == source_id)
            .order_by(SourceChunk.chunk_index)
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_with_embeddings(self, limit: int = 100) -> list[SourceChunk]:
        """Return chunks that have vector embeddings (for similarity search prep)."""
        stmt = select(SourceChunk).where(SourceChunk.embedding.is_not(None)).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
