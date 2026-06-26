"""End-to-end API journey: admin source review workflow."""

import pytest
import httpx


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_admin_journey_source_lifecycle(
    async_client: httpx.AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    """Admin flow: stats → create → authenticate → list → delete."""
    initial_stats = await async_client.get("/api/v1/admin/stats", headers=admin_headers)
    assert initial_stats.status_code == 200
    initial_total = initial_stats.json()["total_sources"]

    create = await async_client.post(
        "/api/v1/sources",
        headers=admin_headers,
        json={
            "title": "E2E Test Source",
            "author": "SANAD QA",
            "source_type": "standard",
            "language": "en",
            "is_authenticated": False,
        },
    )
    assert create.status_code == 201
    source_id = create.json()["id"]

    updated_stats = await async_client.get("/api/v1/admin/stats", headers=admin_headers)
    assert updated_stats.json()["total_sources"] == initial_total + 1

    authenticate = await async_client.put(
        f"/api/v1/sources/{source_id}",
        headers=admin_headers,
        json={"is_authenticated": True},
    )
    assert authenticate.status_code == 200

    delete = await async_client.delete(
        f"/api/v1/sources/{source_id}",
        headers=admin_headers,
    )
    assert delete.status_code == 204

    final_stats = await async_client.get("/api/v1/admin/stats", headers=admin_headers)
    assert final_stats.json()["total_sources"] == initial_total
