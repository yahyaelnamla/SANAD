"""Generic async repository base class."""

from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Provides common async CRUD operations for ORM models."""

    model: type[ModelType]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, entity_id: UUID) -> ModelType | None:
        """Fetch a single record by primary key."""
        return await self.session.get(self.model, entity_id)

    async def create(self, entity: ModelType) -> ModelType:
        """Persist a new record."""
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity: ModelType) -> None:
        """Remove a record from the database."""
        await self.session.delete(entity)
        await self.session.flush()

    async def list_all(self, limit: int = 100, offset: int = 0) -> list[ModelType]:
        """Return paginated records."""
        stmt = select(self.model).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
