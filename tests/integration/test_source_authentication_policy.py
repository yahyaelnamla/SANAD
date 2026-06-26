"""Integration tests for source authentication gating RAG retrieval."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.enums import SourceType
from backend.app.models.source import Source
from backend.app.models.source_chunk import EMBEDDING_DIMENSION, SourceChunk
from backend.app.repositories.source_repository import SourceRepository
from rag.ingestion.base import IngestedDocument
from rag.pipelines.main_rag_pipeline import MainRAGPipeline

RIBA_TEXT = (
    "Riba (usury) is categorically prohibited in Islamic law. "
    "Classical jurists agree that guaranteed increase on a loan constitutes riba."
)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_unauthenticated_sources_excluded_from_retrieval(
    db_session: AsyncSession,
) -> None:
    """Only authenticated sources may support jurisprudential retrieval."""
    repo = SourceRepository(db_session)
    pending = await repo.create(
        Source(
            title="Pending Fiqh Text",
            author="Scholar",
            source_type=SourceType.CLASSICAL,
            language="ar",
            is_authenticated=False,
        )
    )
    await db_session.flush()
    chunk_repo_source = pending
    db_session.add(
        SourceChunk(
            source_id=chunk_repo_source.id,
            content=RIBA_TEXT,
            chunk_index=0,
            embedding=[0.1] * EMBEDDING_DIMENSION,
        )
    )
    await db_session.flush()

    authenticated = await repo.list_authenticated()
    assert all(source.is_authenticated for source in authenticated)
    assert pending.id not in {source.id for source in authenticated}


@pytest.mark.integration
@pytest.mark.asyncio
async def test_authenticated_source_available_after_review(
    db_session: AsyncSession,
) -> None:
    """Admin authentication enables a source for RAG retrieval."""
    repo = SourceRepository(db_session)
    source = await repo.create(
        Source(
            title="Reviewed Standard",
            author="AAOIFI",
            source_type=SourceType.STANDARD,
            language="en",
            is_authenticated=False,
        )
    )
    db_session.add(
        SourceChunk(
            source_id=source.id,
            content=RIBA_TEXT,
            chunk_index=0,
            embedding=[0.2] * EMBEDDING_DIMENSION,
        )
    )
    await db_session.flush()

    source.is_authenticated = True
    await db_session.flush()

    authenticated = await repo.list_authenticated(source_type=SourceType.STANDARD)
    assert any(item.id == source.id for item in authenticated)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ingested_authenticated_source_is_retrievable(
    db_session: AsyncSession,
) -> None:
    """RAG ingestion with is_authenticated=True makes evidence available."""
    pipeline = MainRAGPipeline(db_session)
    await pipeline.ingest(
        IngestedDocument(
            content=RIBA_TEXT,
            source_title="Majallah al-Ahkam",
            source_author="Ottoman Scholars",
            language="en",
        ),
        SourceType.CLASSICAL,
        is_authenticated=True,
    )

    repo = SourceRepository(db_session)
    results = await repo.list_authenticated(source_type=SourceType.CLASSICAL)
    assert len(results) >= 1
    assert results[0].is_authenticated is True
