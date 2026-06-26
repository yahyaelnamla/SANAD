"""Extract knowledge content from the SANAD database."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.models.source import Source
from rag.ingestion.base import IngestedDocument


async def extract_source_from_database(
    session: AsyncSession,
    source_id: uuid.UUID,
) -> IngestedDocument:
    """Build an IngestedDocument from stored source chunks."""
    stmt = (
        select(Source)
        .options(selectinload(Source.chunks))
        .where(Source.id == source_id)
    )
    result = await session.execute(stmt)
    source = result.scalar_one_or_none()
    if source is None:
        raise ValueError(f"Source not found: {source_id}")

    if not source.chunks:
        raise ValueError(f"Source has no chunks: {source_id}")

    ordered = sorted(source.chunks, key=lambda chunk: chunk.chunk_index)
    content = "\n\n".join(chunk.content for chunk in ordered)

    return IngestedDocument(
        content=content,
        source_title=source.title,
        source_author=source.author,
        language=source.language,
        metadata={
            "format": "database",
            "source_id": str(source.id),
            "source_type": source.source_type.value,
            "chunk_count": len(ordered),
        },
    )
