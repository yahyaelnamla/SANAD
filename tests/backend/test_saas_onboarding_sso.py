"""Tests for SSO and onboarding endpoints."""

import httpx
import pytest

from tests.conftest import TEST_PASSWORD


@pytest.mark.asyncio
async def test_sso_providers(async_client: httpx.AsyncClient) -> None:
    response = await async_client.get("/api/v1/auth/sso/providers")
    assert response.status_code == 200
    providers = response.json()
    assert len(providers) == 2
    assert all(item["enabled"] for item in providers)


@pytest.mark.asyncio
async def test_sso_demo_flow(async_client: httpx.AsyncClient) -> None:
    start = await async_client.post(
        "/api/v1/auth/sso/start",
        json={"provider": "google"},
    )
    assert start.status_code == 200
    data = start.json()
    assert data["mode"] == "demo"
    session_id = data["session_id"]

    complete = await async_client.post(
        "/api/v1/auth/sso/complete",
        json={
            "provider": "google",
            "session_id": session_id,
            "email": "sso-user@example.com",
        },
    )
    assert complete.status_code == 200
    token = complete.json()["access_token"]
    assert token
    assert complete.json()["is_new_user"] is True

    profile = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert profile.status_code == 200
    assert profile.json()["auth_provider"] == "google"
    assert profile.json()["onboarding_completed"] is False


@pytest.mark.asyncio
async def test_onboarding_flow(async_client: httpx.AsyncClient) -> None:
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": "onboard@example.com", "password": TEST_PASSWORD, "locale": "en"},
    )
    login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "onboard@example.com", "password": TEST_PASSWORD},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    status = await async_client.get("/api/v1/auth/me/onboarding", headers=headers)
    assert status.status_code == 200
    assert status.json()["completed"] is False

    patch = await async_client.patch(
        "/api/v1/auth/me/onboarding",
        headers=headers,
        json={
            "locale": "ar",
            "preferred_madhhab": "hanafi",
            "use_case": "student",
            "completed": True,
        },
    )
    assert patch.status_code == 200
    assert patch.json()["completed"] is True
    assert patch.json()["use_case"] == "student"

    profile = await async_client.get("/api/v1/auth/me", headers=headers)
    assert profile.json()["onboarding_completed"] is True
    assert profile.json()["locale"] == "ar"
