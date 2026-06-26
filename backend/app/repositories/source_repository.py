"""Source repository."""

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.enums import SourceType
from backend.app.models.source import Source
from backend.app.repositories.base import BaseRepository


class SourceRepository(BaseRepository[Source]):
    """Data access for authenticated knowledge sources."""

    model = Source

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    def _apply_filters(
        self,
        stmt,
        *,
        is_authenticated: bool | None = None,
        source_type: SourceType | None = None,
    ):
        if is_authenticated is not None:
            stmt = stmt.where(Source.is_authenticated.is_(is_authenticated))
        if source_type is not None:
            stmt = stmt.where(Source.source_type == source_type)
        return stmt

    async def list_authenticated(
        self,
        source_type: SourceType | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Source]:
        """Return authenticated sources, optionally filtered by type."""
        stmt = select(Source).where(Source.is_authenticated.is_(True))
        if source_type is not None:
            stmt = stmt.where(Source.source_type == source_type)
        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_filtered(
        self,
        *,
        is_authenticated: bool | None = None,
        source_type: SourceType | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Source]:
        """Return sources with optional filters, newest first."""
        stmt = select(Source)
        stmt = self._apply_filters(
            stmt,
            is_authenticated=is_authenticated,
            source_type=source_type,
        )
        stmt = stmt.order_by(Source.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_filtered(
        self,
        *,
        is_authenticated: bool | None = None,
        source_type: SourceType | None = None,
    ) -> int:
        """Count sources matching optional filters."""
        stmt = select(func.count()).select_from(Source)
        stmt = self._apply_filters(
            stmt,
            is_authenticated=is_authenticated,
            source_type=source_type,
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def count_authenticated(self) -> int:
        """Count sources verified by admin/reviewer."""
        return await self.count_filtered(is_authenticated=True)

    async def count_pending(self) -> int:
        """Count sources awaiting authentication review."""
        return await self.count_filtered(is_authenticated=False)

    async def search_authenticated(self, query_text: str, *, limit: int = 10) -> list[Source]:
        """Search authenticated sources by title or author."""
        pattern = f"%{query_text.strip()}%"
        stmt = (
            select(Source)
            .where(
                Source.is_authenticated.is_(True),
                or_(Source.title.ilike(pattern), Source.author.ilike(pattern)),
            )
            .order_by(Source.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
