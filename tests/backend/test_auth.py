"""Tests for authentication and RBAC."""

import httpx
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.auth.security import hash_password
from backend.app.models.enums import UserRole
from backend.app.models.user import User
from backend.app.repositories.user_repository import UserRepository
from tests.conftest import TEST_PASSWORD


@pytest.mark.asyncio
async def test_user_preferences_api(async_client: httpx.AsyncClient, auth_headers: dict) -> None:
    response = await async_client.get("/api/v1/auth/me/preferences", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "bookmarks" in data

    patch = await async_client.patch(
        "/api/v1/auth/me/preferences",
        headers=auth_headers,
        json={"preferred_madhhab": "hanafi", "favorite_scholars": ["Test Scholar"]},
    )
    assert patch.status_code == 200
    assert patch.json()["preferred_madhhab"] == "hanafi"

    response = await async_client.post(
        "/api/v1/auth/register",
        json={"email": "newuser@example.com", "password": TEST_PASSWORD, "locale": "en"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["role"] == "user"


@pytest.mark.asyncio
async def test_register_duplicate_email(async_client: httpx.AsyncClient) -> None:
    payload = {"email": "dup@example.com", "password": TEST_PASSWORD, "locale": "ar"}
    await async_client.post("/api/v1/auth/register", json=payload)
    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert response.json()["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_login_returns_jwt(async_client: httpx.AsyncClient) -> None:
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "password": TEST_PASSWORD, "locale": "en"},
    )
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": TEST_PASSWORD},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(async_client: httpx.AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "missing@example.com", "password": TEST_PASSWORD},
    )
    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_get_me_with_token(async_client: httpx.AsyncClient) -> None:
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": "me@example.com", "password": TEST_PASSWORD, "locale": "ar"},
    )
    login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "me@example.com", "password": TEST_PASSWORD},
    )
    token = login.json()["access_token"]
    response = await async_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"


@pytest.mark.asyncio
async def test_admin_ping_requires_admin_role(
    async_client: httpx.AsyncClient,
    db_session: AsyncSession,
) -> None:
    repo = UserRepository(db_session)
    user = User(
        email="regular@example.com",
        password_hash=hash_password(TEST_PASSWORD),
        role=UserRole.USER,
        locale="en",
    )
    await repo.create(user)

    login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "regular@example.com", "password": TEST_PASSWORD},
    )
    token = login.json()["access_token"]
    response = await async_client.get(
        "/api/v1/auth/admin/ping",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
    assert response.json()["code"] == "FORBIDDEN"


@pytest.mark.asyncio
async def test_admin_ping_allows_admin(
    async_client: httpx.AsyncClient,
    db_session: AsyncSession,
) -> None:
    repo = UserRepository(db_session)
    admin = User(
        email="admin@example.com",
        password_hash=hash_password(TEST_PASSWORD),
        role=UserRole.ADMIN,
        locale="en",
    )
    await repo.create(admin)

    login = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": TEST_PASSWORD},
    )
    token = login.json()["access_token"]
    response = await async_client.get(
        "/api/v1/auth/admin/ping",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
