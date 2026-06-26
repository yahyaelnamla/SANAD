"""Tests for evaluation dashboard API."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_evaluation_dashboard_requires_auth(async_client: AsyncClient) -> None:
    response = await async_client.get("/api/v1/evaluation/dashboard")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_evaluation_dashboard_returns_fanar_manifest(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    response = await async_client.get("/api/v1/evaluation/dashboard", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "Fanar-Sadiq" in data["fanar_capabilities"]
    assert "Fanar-Guard-2" in data["fanar_capabilities"]
    assert len(data["demo_prompts"]) >= 4
    assert len(data["feature_matrix"]) >= 4
    assert "stats" in data
    assert isinstance(data["recent_queries"], list)


@pytest.mark.asyncio
async def test_evaluation_harness_requires_auth(async_client: AsyncClient) -> None:
    response = await async_client.get("/api/v1/evaluation/harness")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_evaluation_harness_returns_cases(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    response = await async_client.get("/api/v1/evaluation/harness", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_cases"] >= 5
    assert "honesty" in data["categories"]
    assert len(data["scoring_notes"]) >= 3
