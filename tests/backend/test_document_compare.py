"""Tests for multi-document comparison API."""

import httpx
import pytest

from tests.backend.test_document_service import _build_sample_pdf


@pytest.mark.asyncio
async def test_compare_documents_requires_two(
    async_client: httpx.AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    response = await async_client.post(
        "/api/v1/tools/documents/compare",
        headers=auth_headers,
        json={"document_ids": ["00000000-0000-0000-0000-000000000001"]},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_compare_documents_side_by_side(
    async_client: httpx.AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    ids: list[str] = []
    for label, text in (
        ("report_a.pdf", "riba interest income revenue"),
        ("report_b.pdf", "riba debt compliance revenue"),
    ):
        upload = await async_client.post(
            "/api/v1/tools/documents/analyze",
            headers=auth_headers,
            files={"file": (label, _build_sample_pdf(text), "application/pdf")},
            data={"language": "en"},
        )
        assert upload.status_code == 200
        doc_id = upload.json().get("document_id")
        assert doc_id
        ids.append(doc_id)

    compare = await async_client.post(
        "/api/v1/tools/documents/compare",
        headers=auth_headers,
        json={"document_ids": ids},
    )
    assert compare.status_code == 200
    data = compare.json()
    assert len(data["documents"]) == 2
    assert isinstance(data["comparison_notes"], list)
    assert "riba" in " ".join(data.get("shared_riba_signals", [])).lower() or data["comparison_notes"]
