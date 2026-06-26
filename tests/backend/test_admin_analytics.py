"""Tests for admin analytics endpoint."""

import httpx
import pytest


@pytest.mark.asyncio
async def test_admin_analytics_requires_reviewer(
    async_client: httpx.AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    response = await async_client.get("/api/v1/admin/analytics", headers=auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_analytics_returns_metrics(
    async_client: httpx.AsyncClient,
    admin_headers: dict[str, str],
) -> None:
    response = await async_client.get("/api/v1/admin/analytics", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_queries" in data
    assert "refusal_rate" in data
    assert "queries_by_day" in data
    assert len(data["queries_by_day"]) == 7
    assert "model_usage" in data
