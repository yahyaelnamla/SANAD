"""Integration tests for admin source management workflow."""

import httpx
import pytest


@pytest.mark.integration
@pytest.mark.asyncio
async def test_admin_source_review_workflow(
    async_client: httpx.AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    """Admin creates a pending source, authenticates it, and stats update."""
    create_response = await async_client.post(
        "/api/v1/sources",
        headers=admin_headers,
        json={
            "title": "Contemporary Fatwa Collection",
            "author": "Shariah Board",
            "source_type": "fatwa",
            "language": "ar",
            "is_authenticated": False,
        },
    )
    assert create_response.status_code == 201
    source_id = create_response.json()["id"]

    pending_stats = await async_client.get("/api/v1/admin/stats", headers=admin_headers)
    assert pending_stats.status_code == 200
    assert pending_stats.json()["pending_sources"] >= 1

    update_response = await async_client.put(
        f"/api/v1/sources/{source_id}",
        headers=admin_headers,
        json={"is_authenticated": True},
    )
    assert update_response.status_code == 200
    assert update_response.json()["is_authenticated"] is True

    filtered = await async_client.get(
        "/api/v1/sources?is_authenticated=true",
        headers=admin_headers,
    )
    assert filtered.status_code == 200
    ids = {item["id"] for item in filtered.json()["items"]}
    assert source_id in ids


@pytest.mark.integration
@pytest.mark.asyncio
async def test_reviewer_can_manage_sources(
    async_client: httpx.AsyncClient,
    db_session,
) -> None:
    """Reviewer role has source management access."""
    from backend.app.models.enums import UserRole
    from tests.conftest import create_test_user, login_and_get_token

    await create_test_user(db_session, email="reviewer@example.com", role=UserRole.REVIEWER)
    token = await login_and_get_token(async_client, "reviewer@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.get("/api/v1/sources", headers=headers)
    assert response.status_code == 200
