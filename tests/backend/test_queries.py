"""Tests for query API endpoints."""

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.enums import SourceType
from rag.ingestion.base import IngestedDocument
from rag.pipelines.main_rag_pipeline import MainRAGPipeline
from tests.conftest import TEST_PASSWORD

RIBA_TEXT = (
    "Riba (usury) is categorically prohibited in Islamic law. "
    "Classical jurists from all major madhabs agree that any guaranteed increase "
    "on a loan constitutes riba. Source: Majallah al-Ahkam al-Adliyyah."
)


@pytest.fixture
async def auth_headers(async_client: httpx.AsyncClient) -> dict[str, str]:
    """Register a user, login, and return JWT Bearer headers."""
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": "query-test@example.com", "password": TEST_PASSWORD, "locale": "en"},
    )
    login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "query-test@example.com", "password": TEST_PASSWORD},
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


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


@pytest.mark.asyncio
async def test_submit_query_returns_explainability_chain(
    async_client: httpx.AsyncClient,
    auth_headers: dict[str, str],
    seeded_knowledge: None,
) -> None:
    """POST /queries should return the full explainability chain with citations."""
    response = await async_client.post(
        "/api/v1/queries",
        json={"question": "Is riba prohibited in Islam?", "language": "en"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["summary"]
    assert data["evidence"]
    assert data["evidence"][0]["citation"]
    assert data["principles"]
    assert data["reasoning"]
    assert data["confidence"] > 0
    assert not data["refused"]


@pytest.mark.asyncio
async def test_submit_query_refuses_without_evidence(
    async_client: httpx.AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """POST /queries should return 422 NO_EVIDENCE when pipeline refuses."""
    response = await async_client.post(
        "/api/v1/queries",
        json={"question": "Is quantum trading halal?", "language": "en"},
        headers=auth_headers,
    )
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == "NO_EVIDENCE"
    assert "authenticated" in data["message"].lower()


@pytest.mark.asyncio
async def test_get_query_by_id(
    async_client: httpx.AsyncClient,
    auth_headers: dict[str, str],
    seeded_knowledge: None,
) -> None:
    """GET /queries/{id} should return a persisted query result."""
    create_resp = await async_client.post(
        "/api/v1/queries",
        json={"question": "Is riba haram?", "language": "en"},
        headers=auth_headers,
    )
    query_id = create_resp.json()["query_id"]

    get_resp = await async_client.get(f"/api/v1/queries/{query_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["query_id"] == query_id
    assert data["evidence"]


@pytest.mark.asyncio
async def test_list_queries(
    async_client: httpx.AsyncClient,
    auth_headers: dict[str, str],
    seeded_knowledge: None,
) -> None:
    """GET /queries should return user query history."""
    await async_client.post(
        "/api/v1/queries",
        json={"question": "Is riba prohibited?", "language": "en"},
        headers=auth_headers,
    )
    response = await async_client.get("/api/v1/queries", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 1
    assert data["items"][0]["question"]


@pytest.mark.asyncio
async def test_unauthorized_without_token(async_client: httpx.AsyncClient) -> None:
    """Requests without JWT should return 401."""
    response = await async_client.post(
        "/api/v1/queries",
        json={"question": "Is riba haram?", "language": "en"},
    )
    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_get_query_not_found(
    async_client: httpx.AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """GET /queries/{id} should return 404 for unknown query."""
    response = await async_client.get(
        "/api/v1/queries/00000000-0000-0000-0000-000000000001",
        headers=auth_headers,
    )
    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_update_query_metadata(
    async_client: httpx.AsyncClient,
    auth_headers: dict[str, str],
    seeded_knowledge: None,
) -> None:
    create_resp = await async_client.post(
        "/api/v1/queries",
        json={"question": "Is riba prohibited in Islam?", "language": "en"},
        headers=auth_headers,
    )
    query_id = create_resp.json()["query_id"]

    patch_resp = await async_client.patch(
        f"/api/v1/queries/{query_id}",
        json={
            "display_title": "Riba ruling summary",
            "folder": "Core Fiqh",
            "tags": ["riba", "fiqh"],
        },
        headers=auth_headers,
    )
    assert patch_resp.status_code == 200
    data = patch_resp.json()
    assert data["display_title"] == "Riba ruling summary"
    assert data["folder"] == "Core Fiqh"
    assert "riba" in data["tags"]


@pytest.mark.asyncio
async def test_archive_and_export_query(
    async_client: httpx.AsyncClient,
    auth_headers: dict[str, str],
    seeded_knowledge: None,
) -> None:
    create_resp = await async_client.post(
        "/api/v1/queries",
        json={"question": "Is riba haram?", "language": "en"},
        headers=auth_headers,
    )
    query_id = create_resp.json()["query_id"]

    archive_resp = await async_client.patch(
        f"/api/v1/queries/{query_id}",
        json={"archived": True},
        headers=auth_headers,
    )
    assert archive_resp.status_code == 200
    assert archive_resp.json()["archived"] is True

    list_resp = await async_client.get("/api/v1/queries", headers=auth_headers)
    assert all(item["query_id"] != query_id for item in list_resp.json()["items"])

    archived_resp = await async_client.get(
        "/api/v1/queries?include_archived=true",
        headers=auth_headers,
    )
    assert any(item["query_id"] == query_id for item in archived_resp.json()["items"])

    export_resp = await async_client.get(
        f"/api/v1/queries/{query_id}/export",
        headers=auth_headers,
    )
    assert export_resp.status_code == 200
    export_data = export_resp.json()
    assert export_data["content"]
    assert export_data["filename"].endswith(".md")


@pytest.mark.asyncio
async def test_delete_query(
    async_client: httpx.AsyncClient,
    auth_headers: dict[str, str],
    seeded_knowledge: None,
) -> None:
    create_resp = await async_client.post(
        "/api/v1/queries",
        json={"question": "Temporary query", "language": "en"},
        headers=auth_headers,
    )
    query_id = create_resp.json()["query_id"]

    delete_resp = await async_client.delete(
        f"/api/v1/queries/{query_id}",
        headers=auth_headers,
    )
    assert delete_resp.status_code == 204

    get_resp = await async_client.get(f"/api/v1/queries/{query_id}", headers=auth_headers)
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_global_search(
    async_client: httpx.AsyncClient,
    auth_headers: dict[str, str],
    seeded_knowledge: None,
) -> None:
    await async_client.post(
        "/api/v1/queries",
        json={"question": "Is riba prohibited?", "language": "en"},
        headers=auth_headers,
    )
    response = await async_client.get("/api/v1/search?q=riba", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert any(item["type"] == "chat" for item in data["results"])


@pytest.mark.asyncio
async def test_global_search_includes_persisted_documents(
    async_client: httpx.AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    from tests.backend.test_document_service import _build_sample_pdf

    pdf_bytes = _build_sample_pdf("Interest income disclosure and total revenue: 500,000")
    upload = await async_client.post(
        "/api/v1/tools/documents/analyze",
        files={"file": ("annual-report.pdf", pdf_bytes, "application/pdf")},
        data={"language": "en"},
        headers=auth_headers,
    )
    assert upload.status_code == 200

    response = await async_client.get("/api/v1/search?q=interest", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert any(item["type"] == "document" for item in data["results"])
