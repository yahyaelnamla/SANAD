"""Tests for scholar profile API."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_scholars_requires_auth(async_client: AsyncClient) -> None:
    response = await async_client.get("/api/v1/scholars")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_scholars_returns_seed_profiles(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    response = await async_client.get("/api/v1/scholars", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 5
    slugs = {item["slug"] for item in data["items"]}
    assert "aaoifi-shariah-board" in slugs


@pytest.mark.asyncio
async def test_get_scholar_profile(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    response = await async_client.get(
        "/api/v1/scholars/aaoifi-shariah-board",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "AAOIFI Shariah Board"
    assert "AAOIFI" in data["expertise"]


@pytest.mark.asyncio
async def test_get_scholar_not_found(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    response = await async_client.get(
        "/api/v1/scholars/nonexistent-scholar-xyz",
        headers=auth_headers,
    )
    assert response.status_code == 404
