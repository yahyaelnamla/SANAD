"""Shared FastAPI dependencies for API routes."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.auth.dependencies import get_current_user
from backend.app.config.database import get_db
from backend.app.models.user import User

DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Alias for get_db — used in dependency overrides during tests."""
    async for session in get_db():
        yield session
