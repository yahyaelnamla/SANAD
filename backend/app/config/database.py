"""Async database engine and session management."""

import logging
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.app.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_database() -> None:
    """Apply idempotent schema patches on startup."""
    from backend.app.config.schema_patches import apply_runtime_schema_patches

    try:
        await apply_runtime_schema_patches(engine)
    except Exception:
        logger.exception("Failed to apply runtime schema patches.")
        raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def create_test_engine(database_url: str):
    """Create an async engine for test environments."""
    return create_async_engine(database_url, echo=False, pool_pre_ping=True)
