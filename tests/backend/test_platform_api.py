"""Tests for platform integration API."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_platform_status_requires_key(async_client: AsyncClient) -> None:
    response = await async_client.get("/api/v1/platform/status")
    assert response.status_code in {401, 503}


@pytest.mark.asyncio
async def test_platform_status_with_key(
    async_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PLATFORM_API_KEY", "test-platform-key")
    from backend.app.config.settings import get_settings

    get_settings.cache_clear()

    response = await async_client.get(
        "/api/v1/platform/status",
        headers={"X-Platform-Key": "test-platform-key"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "shariah_query" in data["capabilities"]


@pytest.mark.asyncio
async def test_platform_harness_returns_cases(
    async_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PLATFORM_API_KEY", "test-platform-key")
    from backend.app.config.settings import get_settings

    get_settings.cache_clear()

    response = await async_client.get(
        "/api/v1/platform/harness",
        headers={"X-Platform-Key": "test-platform-key"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_cases"] >= 5
    assert len(data["cases"]) >= 5
    assert "scoring_notes" in data
