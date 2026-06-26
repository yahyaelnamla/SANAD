"""Tests for repository CRUD operations."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.audit_log import AuditLog
from backend.app.models.enums import QueryStatus, SourceType, UserRole
from backend.app.models.query import Query
from backend.app.models.response import Response
from backend.app.models.source import Source
from backend.app.models.source_chunk import EMBEDDING_DIMENSION, SourceChunk
from backend.app.models.user import User
from backend.app.repositories.audit_log_repository import AuditLogRepository
from backend.app.repositories.query_repository import QueryRepository
from backend.app.repositories.response_repository import ResponseRepository
from backend.app.repositories.source_chunk_repository import SourceChunkRepository
from backend.app.repositories.source_repository import SourceRepository
from backend.app.repositories.user_repository import UserRepository


@pytest.mark.asyncio
async def test_user_repository_crud(db_session: AsyncSession) -> None:
    """UserRepository should create and fetch by email."""
    repo = UserRepository(db_session)
    user = User(email="repo@sanad.local", password_hash="hash", role=UserRole.ADMIN)
    created = await repo.create(user)

    fetched = await repo.get_by_email("repo@sanad.local")
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.role == UserRole.ADMIN


@pytest.mark.asyncio
async def test_source_repository_authenticated_filter(db_session: AsyncSession) -> None:
    """SourceRepository should filter authenticated sources by type."""
    repo = SourceRepository(db_session)
    auth_source = Source(
        title="AAOIFI Shariah Standard",
        author="AAOIFI",
        source_type=SourceType.STANDARD,
        language="en",
        is_authenticated=True,
    )
    unauth_source = Source(
        title="Unverified Blog",
        author="Unknown",
        source_type=SourceType.CONTEMPORARY,
        language="en",
        is_authenticated=False,
    )
    await repo.create(auth_source)
    await repo.create(unauth_source)

    results = await repo.list_authenticated(source_type=SourceType.STANDARD)
    assert len(results) == 1
    assert results[0].title == "AAOIFI Shariah Standard"


@pytest.mark.asyncio
async def test_source_chunk_repository_by_source(db_session: AsyncSession) -> None:
    """SourceChunkRepository should list chunks ordered by index."""
    source_repo = SourceRepository(db_session)
    chunk_repo = SourceChunkRepository(db_session)

    source = await source_repo.create(
        Source(
            title="Fiqh Source",
            author="Scholar",
            source_type=SourceType.CLASSICAL,
            language="ar",
            is_authenticated=True,
        )
    )
    await chunk_repo.create(
        SourceChunk(source_id=source.id, content="Chunk B", chunk_index=1, embedding=[0.0] * EMBEDDING_DIMENSION)
    )
    await chunk_repo.create(
        SourceChunk(source_id=source.id, content="Chunk A", chunk_index=0, embedding=[0.1] * EMBEDDING_DIMENSION)
    )

    chunks = await chunk_repo.list_by_source(source.id)
    assert [c.content for c in chunks] == ["Chunk A", "Chunk B"]

    with_embeddings = await chunk_repo.list_with_embeddings()
    assert len(with_embeddings) == 2


@pytest.mark.asyncio
async def test_query_repository_user_history(db_session: AsyncSession) -> None:
    """QueryRepository should list user queries and update status."""
    user_repo = UserRepository(db_session)
    query_repo = QueryRepository(db_session)

    user = await user_repo.create(User(email="queries@sanad.local", password_hash="hash"))
    query = await query_repo.create(
        Query(user_id=user.id, question="ETF halal?", language="en", status=QueryStatus.PENDING)
    )

    await query_repo.update_status(query, QueryStatus.PROCESSING)
    history = await query_repo.list_by_user(user.id)

    assert len(history) == 1
    assert history[0].status == QueryStatus.PROCESSING


@pytest.mark.asyncio
async def test_response_repository_by_query(db_session: AsyncSession) -> None:
    """ResponseRepository should fetch response by query ID."""
    user_repo = UserRepository(db_session)
    query_repo = QueryRepository(db_session)
    response_repo = ResponseRepository(db_session)

    user = await user_repo.create(User(email="response@sanad.local", password_hash="hash"))
    query = await query_repo.create(
        Query(user_id=user.id, question="DeFi ruling?", language="en")
    )
    response = await response_repo.create(
        Response(
            query_id=query.id,
            summary="Insufficient evidence.",
            evidence=[],
            principles=[],
            reasoning="No authenticated sources found.",
            opinions=[],
            sources=[],
            confidence=0.0,
        )
    )

    fetched = await response_repo.get_by_query_id(query.id)
    assert fetched is not None
    assert fetched.id == response.id
    assert fetched.summary == "Insufficient evidence."


@pytest.mark.asyncio
async def test_audit_log_repository(db_session: AsyncSession) -> None:
    """AuditLogRepository should list logs per user."""
    user_repo = UserRepository(db_session)
    audit_repo = AuditLogRepository(db_session)

    user = await user_repo.create(User(email="audit@sanad.local", password_hash="hash"))
    await audit_repo.create(
        AuditLog(
            user_id=user.id,
            action="source.authenticate",
            resource=f"source:{uuid.uuid4()}",
            details={"approved": True},
        )
    )

    logs = await audit_repo.list_by_user(user.id)
    assert len(logs) == 1
    assert logs[0].action == "source.authenticate"
