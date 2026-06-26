"""Pytest fixtures for SANAD tests."""

import os
from collections.abc import AsyncIterator

import httpx
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import ASGITransport
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from backend.app.auth.security import hash_password
from backend.app.config.database import get_db
from backend.app.config.settings import Settings
from backend.app.main import create_app
from backend.app.models import Base
from backend.app.models.enums import UserRole
from backend.app.models.user import User
from backend.app.repositories.user_repository import UserRepository

TEST_PASSWORD = "SecurePass123!"


@pytest.fixture(autouse=True)
def _test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure deterministic secrets and Fanar stubs for all tests."""
    monkeypatch.setenv("FANAR_API_KEY", "test-key")
    monkeypatch.setenv("JWT_SECRET", "test-jwt-secret")
    monkeypatch.setenv("QUERY_ASYNC", "false")

    from backend.app.config.settings import get_settings

    get_settings.cache_clear()

    from tests.helpers.embedding_stub import DeterministicEmbeddingModel
    from tests.helpers.fanar_stub import DeterministicFanarClient

    monkeypatch.setattr(
        "agents.common.fanar_client.FanarLLMClient",
        DeterministicFanarClient,
    )
    monkeypatch.setattr(
        "backend.app.agents.agent_orchestrator.FanarLLMClient",
        DeterministicFanarClient,
    )
    monkeypatch.setattr(
        "rag.embeddings.embedding_generator.FanarEmbeddingModel",
        DeterministicEmbeddingModel,
    )
    monkeypatch.setattr(
        "rag.embeddings.fanar_embedding_model.FanarEmbeddingModel",
        DeterministicEmbeddingModel,
    )


@pytest.fixture
def client() -> TestClient:
    """Return a test client for the FastAPI application."""
    app = create_app()
    return TestClient(app)


@pytest_asyncio.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    """Yield an isolated async session with rollback after each test."""
    settings = Settings()
    primary_url = os.getenv("TEST_DATABASE_URL", settings.test_database_url)
    fallback_url = settings.database_url

    engine = None

    for candidate in (primary_url, fallback_url):
        engine = create_async_engine(candidate, poolclass=NullPool, echo=False)
        try:
            async with engine.begin() as conn:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                await conn.run_sync(Base.metadata.create_all)
                await conn.execute(
                    text(
                        "ALTER TABLE responses ADD COLUMN IF NOT EXISTS "
                        "confidence_breakdown JSONB NOT NULL DEFAULT '{}'::jsonb"
                    )
                )
                await conn.execute(
                    text(
                        "ALTER TABLE responses ADD COLUMN IF NOT EXISTS "
                        "agent_trace JSONB NOT NULL DEFAULT '[]'::jsonb"
                    )
                )
                await conn.execute(
                    text(
                        "ALTER TABLE responses ADD COLUMN IF NOT EXISTS thinking_trace TEXT"
                    )
                )
                for statement in (
                    "ALTER TABLE queries ADD COLUMN IF NOT EXISTS display_title VARCHAR(500)",
                    "ALTER TABLE queries ADD COLUMN IF NOT EXISTS archived BOOLEAN NOT NULL DEFAULT FALSE",
                    "ALTER TABLE queries ADD COLUMN IF NOT EXISTS folder VARCHAR(120)",
                    "ALTER TABLE queries ADD COLUMN IF NOT EXISTS tags JSONB NOT NULL DEFAULT '[]'::jsonb",
                    "ALTER TABLE queries ADD COLUMN IF NOT EXISTS session_id VARCHAR(64)",
                    "ALTER TABLE responses ADD COLUMN IF NOT EXISTS suggested_questions JSONB NOT NULL DEFAULT '[]'::jsonb",
                    "ALTER TABLE users ADD COLUMN IF NOT EXISTS preferences JSONB NOT NULL DEFAULT '{}'::jsonb",
                    "ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL",
                    "ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_tier VARCHAR(32) NOT NULL DEFAULT 'free'",
                    "ALTER TABLE users ADD COLUMN IF NOT EXISTS subscription_status VARCHAR(32) NOT NULL DEFAULT 'active'",
                    "ALTER TABLE users ADD COLUMN IF NOT EXISTS onboarding_completed BOOLEAN NOT NULL DEFAULT false",
                    "ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_provider VARCHAR(32) NOT NULL DEFAULT 'email'",
                    "ALTER TABLE users ADD COLUMN IF NOT EXISTS sso_subject VARCHAR(255)",
                ):
                    await conn.execute(text(statement))
            break
        except OSError as exc:
            await engine.dispose()
            pytest.skip(f"PostgreSQL not available: {exc}")
        except Exception as exc:
            await engine.dispose()
            engine = None
            if candidate == fallback_url:
                pytest.skip(f"Database setup failed: {exc}")
            continue

    if engine is None:
        pytest.skip("Database setup failed: no connection available")

    connection = await engine.connect()
    transaction = await connection.begin()
    session = AsyncSession(bind=connection, expire_on_commit=False)

    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()
    await engine.dispose()


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession) -> AsyncIterator[httpx.AsyncClient]:
    """Async HTTP client wired to the test database session."""
    app = create_app()

    async def override_get_db() -> AsyncIterator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


async def create_test_user(
    db_session: AsyncSession,
    *,
    email: str,
    role: UserRole = UserRole.USER,
    password: str = TEST_PASSWORD,
) -> User:
    """Persist a user for test scenarios."""
    repo = UserRepository(db_session)
    return await repo.create(
        User(
            email=email,
            password_hash=hash_password(password),
            role=role,
            locale="en",
        )
    )


async def login_and_get_token(
    async_client: httpx.AsyncClient,
    email: str,
    password: str = TEST_PASSWORD,
) -> str:
    """Authenticate and return a JWT access token."""
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def auth_headers(async_client: httpx.AsyncClient) -> dict[str, str]:
    """Register a default user and return JWT Bearer headers."""
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": "user@example.com", "password": TEST_PASSWORD, "locale": "en"},
    )
    token = await login_and_get_token(async_client, "user@example.com")
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_headers(
    async_client: httpx.AsyncClient,
    db_session: AsyncSession,
) -> dict[str, str]:
    """Create an admin user and return JWT Bearer headers."""
    await create_test_user(db_session, email="admin@example.com", role=UserRole.ADMIN)
    token = await login_and_get_token(async_client, "admin@example.com")
    return {"Authorization": f"Bearer {token}"}
