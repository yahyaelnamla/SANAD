"""End-to-end API journey: user registration through query history."""

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.enums import SourceType
from rag.ingestion.base import IngestedDocument
from rag.pipelines.main_rag_pipeline import MainRAGPipeline

RIBA_TEXT = (
    "Riba (usury) is categorically prohibited in Islamic law. "
    "Classical jurists agree that guaranteed increase on a loan constitutes riba."
)
TEST_PASSWORD = "SecurePass123!"


@pytest.fixture
async def seeded_knowledge(db_session: AsyncSession) -> None:
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


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_user_journey_register_query_history(
    async_client: httpx.AsyncClient,
    seeded_knowledge: None,
) -> None:
    """Full user flow: register → login → query → history."""
    email = "journey-user@example.com"

    register = await async_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": TEST_PASSWORD, "locale": "en"},
    )
    assert register.status_code == 201

    login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": TEST_PASSWORD},
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    profile = await async_client.get("/api/v1/auth/me", headers=headers)
    assert profile.status_code == 200
    assert profile.json()["email"] == email

    query = await async_client.post(
        "/api/v1/queries",
        json={"question": "Is riba prohibited?", "language": "en"},
        headers=headers,
    )
    assert query.status_code == 201
    query_id = query.json()["query_id"]

    history = await async_client.get("/api/v1/queries", headers=headers)
    assert history.status_code == 200
    assert any(item["query_id"] == query_id for item in history.json()["items"])

    detail = await async_client.get(f"/api/v1/queries/{query_id}", headers=headers)
    assert detail.status_code == 200
    assert detail.json()["evidence"]
