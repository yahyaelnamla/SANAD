"""Tests for document memory injection in chat queries."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.enums import SourceType
from backend.app.services.document_memory_service import fetch_document_evidence
from rag.ingestion.base import IngestedDocument
from rag.pipelines.main_rag_pipeline import MainRAGPipeline
from tests.backend.test_document_service import _build_sample_pdf
from tests.backend.test_queries import RIBA_TEXT


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


@pytest.mark.asyncio
async def test_fetch_document_evidence_by_keywords(
    db_session: AsyncSession,
    auth_headers: dict[str, str],
    async_client,
) -> None:
    from backend.app.repositories.user_repository import UserRepository

    user = await UserRepository(db_session).get_by_email("user@example.com")
    assert user is not None

    pdf_bytes = _build_sample_pdf("Interest income disclosure on page 12.")
    upload = await async_client.post(
        "/api/v1/tools/documents/analyze",
        files={"file": ("annual-report.pdf", pdf_bytes, "application/pdf")},
        data={"language": "en"},
        headers=auth_headers,
    )
    assert upload.status_code == 200

    evidence = await fetch_document_evidence(
        db_session,
        user.id,
        "What did my annual report mention about interest income?",
    )
    assert evidence
    assert "interest" in evidence[0].text.lower()


@pytest.mark.asyncio
async def test_document_question_uses_saved_pdf_context(
    async_client,
    auth_headers: dict[str, str],
    seeded_knowledge: None,
) -> None:
    pdf_bytes = _build_sample_pdf(
        "Interest income disclosure on page 12. Total revenue reached 500,000."
    )
    upload = await async_client.post(
        "/api/v1/tools/documents/analyze",
        files={"file": ("annual-report.pdf", pdf_bytes, "application/pdf")},
        data={"language": "en"},
        headers=auth_headers,
    )
    assert upload.status_code == 200

    response = await async_client.post(
        "/api/v1/queries",
        json={
            "question": "What did my annual report mention about interest income?",
            "language": "en",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    data = response.json()

    assert data["status"] == "completed", data.get("refusal_reason")
    assert data.get("execution_metrics", {}).get("document_context_used") is True
    evidence_text = " ".join(item.get("text", "") for item in data.get("evidence", []))
    assert "interest" in evidence_text.lower() or "annual-report" in evidence_text.lower()
