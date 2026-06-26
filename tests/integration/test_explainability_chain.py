"""Integration tests for the explainability chain structure."""

import pytest
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.enums import SourceType
from rag.ingestion.base import IngestedDocument
from rag.pipelines.main_rag_pipeline import MainRAGPipeline

RIBA_TEXT = (
    "Riba (usury) is categorically prohibited in Islamic law. "
    "Classical jurists from all major madhabs agree that any guaranteed increase "
    "on a loan constitutes riba. Source: Majallah al-Ahkam al-Adliyyah."
)


@pytest.fixture
async def seeded_knowledge(db_session: AsyncSession) -> None:
    """Ingest authenticated riba evidence into the knowledge base."""
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


@pytest.mark.integration
@pytest.mark.asyncio
async def test_query_returns_full_explainability_chain(
    async_client: httpx.AsyncClient,
    auth_headers: dict[str, str],
    seeded_knowledge: None,
) -> None:
    """Query response must follow Evidence → Principles → Reasoning → Analysis."""
    response = await async_client.post(
        "/api/v1/queries",
        json={"question": "Is riba prohibited in Islam?", "language": "en"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()

    assert data["evidence"], "Evidence section required"
    assert data["evidence"][0]["citation"], "Every evidence item must cite a source"
    assert data["principles"], "Principles section required"
    assert data["reasoning"], "Reasoning section required"
    assert data["summary"], "Final analysis summary required"
    assert data["confidence"] > 0
    assert not data["refused"]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_query_refused_without_authenticated_evidence(
    async_client: httpx.AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """No Hallucination Policy: refuse when no authenticated sources exist."""
    response = await async_client.post(
        "/api/v1/queries",
        json={"question": "Is cryptocurrency staking halal?", "language": "en"},
        headers=auth_headers,
    )
    assert response.status_code == 422
    body = response.json()
    assert body["code"] == "NO_EVIDENCE"
