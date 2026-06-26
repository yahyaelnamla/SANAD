"""Vector store manager for persisting embedded chunks."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.enums import SourceType
from backend.app.models.source import Source
from backend.app.models.source_chunk import SourceChunk
from backend.app.repositories.source_chunk_repository import SourceChunkRepository
from backend.app.repositories.source_repository import SourceRepository
from rag.chunking.base import TextChunk


class VectorStoreManager:
    """Manage source and chunk persistence with embeddings."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.source_repo = SourceRepository(session)
        self.chunk_repo = SourceChunkRepository(session)

    async def upsert_source_with_chunks(
        self,
        *,
        title: str,
        author: str,
        source_type: SourceType,
        language: str,
        chunks: list[TextChunk],
        embeddings: list[list[float]],
        url: str | None = None,
        is_authenticated: bool = False,
        source_id: uuid.UUID | None = None,
    ) -> uuid.UUID:
        """Persist a source and its embedded chunks."""
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings length mismatch")
        if not chunks:
            raise ValueError("At least one chunk is required")

        if source_id:
            source = await self.source_repo.get_by_id(source_id)
            if source is None:
                raise ValueError(f"Source not found: {source_id}")
        else:
            source = Source(
                title=title,
                author=author,
                source_type=source_type,
                language=language,
                url=url,
                is_authenticated=is_authenticated,
            )
            source = await self.source_repo.create(source)

        for chunk, embedding in zip(chunks, embeddings, strict=True):
            await self.chunk_repo.create(
                SourceChunk(
                    source_id=source.id,
                    content=chunk.content,
                    chunk_index=chunk.chunk_index,
                    embedding=embedding,
                    metadata_=chunk.metadata,
                )
            )

        return source.id
