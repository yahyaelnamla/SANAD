"""Tests for admin source management API."""

import uuid

import httpx
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.audit_log import AuditLog
from backend.app.models.enums import UserRole
from tests.conftest import TEST_PASSWORD, create_test_user, login_and_get_token


@pytest.mark.asyncio
async def test_list_sources_requires_admin_role(
    async_client: httpx.AsyncClient,
    db_session: AsyncSession,
) -> None:
    await create_test_user(db_session, email="regular@example.com", role=UserRole.USER)
    token = await login_and_get_token(async_client, "regular@example.com")

    response = await async_client.get(
        "/api/v1/sources",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json()["code"] == "FORBIDDEN"


@pytest.mark.asyncio
async def test_create_and_list_sources(
    async_client: httpx.AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    create_response = await async_client.post(
        "/api/v1/sources",
        headers=admin_headers,
        json={
            "title": "AAOIFI Shariah Standard",
            "author": "AAOIFI",
            "source_type": "standard",
            "language": "en",
            "is_authenticated": False,
        },
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["title"] == "AAOIFI Shariah Standard"
    assert created["is_authenticated"] is False

    list_response = await async_client.get("/api/v1/sources", headers=admin_headers)
    assert list_response.status_code == 200
    data = list_response.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == created["id"]


@pytest.mark.asyncio
async def test_update_source_authentication_status(
    async_client: httpx.AsyncClient,
    db_session: AsyncSession,
) -> None:
    await create_test_user(db_session, email="reviewer@example.com", role=UserRole.REVIEWER)
    token = await login_and_get_token(async_client, "reviewer@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    create_response = await async_client.post(
        "/api/v1/sources",
        headers=headers,
        json={
            "title": "Classical Fiqh Text",
            "author": "Ibn Qudamah",
            "source_type": "classical",
            "language": "ar",
            "is_authenticated": False,
        },
    )
    source_id = create_response.json()["id"]

    update_response = await async_client.put(
        f"/api/v1/sources/{source_id}",
        headers=headers,
        json={"is_authenticated": True},
    )
    assert update_response.status_code == 200
    assert update_response.json()["is_authenticated"] is True


@pytest.mark.asyncio
async def test_delete_source_writes_audit_log(
    async_client: httpx.AsyncClient,
    db_session: AsyncSession,
) -> None:
    admin = await create_test_user(db_session, email="admin2@example.com", role=UserRole.ADMIN)
    token = await login_and_get_token(async_client, "admin2@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    create_response = await async_client.post(
        "/api/v1/sources",
        headers=headers,
        json={
            "title": "Temporary Source",
            "author": "Test",
            "source_type": "contemporary",
            "language": "en",
        },
    )
    source_id = create_response.json()["id"]

    delete_response = await async_client.delete(
        f"/api/v1/sources/{source_id}",
        headers=headers,
    )
    assert delete_response.status_code == 204

    result = await db_session.execute(
        select(AuditLog).where(AuditLog.user_id == admin.id, AuditLog.action == "source.delete")
    )
    logs = list(result.scalars().all())
    assert len(logs) == 1
    assert logs[0].resource == f"sources/{source_id}"


@pytest.mark.asyncio
async def test_admin_stats(
    async_client: httpx.AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    await async_client.post(
        "/api/v1/sources",
        headers=admin_headers,
        json={
            "title": "Auth Source",
            "author": "Scholar",
            "source_type": "fatwa",
            "language": "ar",
            "is_authenticated": True,
        },
    )
    await async_client.post(
        "/api/v1/sources",
        headers=admin_headers,
        json={
            "title": "Pending Source",
            "author": "Institution",
            "source_type": "standard",
            "language": "en",
            "is_authenticated": False,
        },
    )

    response = await async_client.get("/api/v1/admin/stats", headers=admin_headers)
    assert response.status_code == 200
    stats = response.json()
    assert stats["total_sources"] == 2
    assert stats["authenticated_sources"] == 1
    assert stats["pending_sources"] == 1


@pytest.mark.asyncio
async def test_update_missing_source_returns_404(
    async_client: httpx.AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    response = await async_client.put(
        f"/api/v1/sources/{uuid.uuid4()}",
        headers=admin_headers,
        json={"title": "Missing"},
    )
    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"
