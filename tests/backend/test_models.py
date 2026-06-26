"""Tests for SQLAlchemy ORM model structure."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.enums import QueryStatus, SourceType, SubscriptionTier, UserRole
from backend.app.models.query import Query
from backend.app.models.response import Response
from backend.app.models.source import Source
from backend.app.models.source_chunk import EMBEDDING_DIMENSION, SourceChunk
from backend.app.models.user import User


@pytest.mark.asyncio
async def test_user_model_fields(db_session: AsyncSession) -> None:
    """User model should persist core identity fields."""
    user = User(
        email="test@sanad.local",
        password_hash="hashed",
        role=UserRole.USER,
        locale="ar",
    )
    db_session.add(user)
    await db_session.flush()

    assert user.id is not None
    assert user.email == "test@sanad.local"
    assert user.role == UserRole.USER
    assert user.created_at is not None


@pytest.mark.asyncio
async def test_subscription_tier_reads_lowercase_db_value(db_session: AsyncSession) -> None:
    """subscription_tier stored as 'free' in DB must map to SubscriptionTier.FREE."""
    user = User(
        email="legacy@sanad.local",
        password_hash="hashed",
        locale="ar",
    )
    db_session.add(user)
    await db_session.flush()
    user_id = user.id
    await db_session.commit()

    from sqlalchemy import select

    result = await db_session.execute(select(User).where(User.id == user_id))
    loaded = result.scalar_one()
    assert loaded.subscription_tier == SubscriptionTier.FREE
    assert loaded.subscription_tier.value == "free"


@pytest.mark.asyncio
async def test_source_chunk_relationship(db_session: AsyncSession) -> None:
    """Source should cascade to chunks with vector embedding."""
    source = Source(
        title="Majallah al-Ahkam",
        author="Ottoman Scholars",
        source_type=SourceType.CLASSICAL,
        language="ar",
        is_authenticated=True,
    )
    chunk = SourceChunk(
        content="البيع جائز",
        chunk_index=0,
        embedding=[0.1] * EMBEDDING_DIMENSION,
        metadata_={"page": 1},
    )
    source.chunks.append(chunk)
    db_session.add(source)
    await db_session.flush()

    assert len(source.chunks) == 1
    assert source.chunks[0].source_id == source.id
    assert len(source.chunks[0].embedding) == EMBEDDING_DIMENSION


@pytest.mark.asyncio
async def test_query_response_explainability_chain(db_session: AsyncSession) -> None:
    """Response model stores the full explainability chain as JSONB fields."""
    user = User(email="fiqh@sanad.local", password_hash="hash", locale="en")
    query = Query(
        user=user,
        question="Is Bitcoin halal?",
        language="en",
        status=QueryStatus.COMPLETED,
    )
    response = Response(
        query=query,
        summary="Analysis requires authenticated evidence.",
        evidence=[{"text": "Evidence text", "source_id": str(uuid.uuid4())}],
        principles=[{"name": "Riba prohibition", "description": "..."}],
        reasoning="Step-by-step fiqh reasoning.",
        opinions=[{"scholar": "Council A", "position": "Conditional"}],
        sources=[{"title": "AAOIFI Standard", "url": "https://example.com"}],
        confidence=0.75,
    )
    db_session.add(response)
    await db_session.flush()

    assert response.query_id == query.id
    assert len(response.evidence) == 1
    assert len(response.principles) == 1
    assert response.confidence == 0.75
    assert query.response is response
