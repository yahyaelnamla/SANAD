"""Query repository."""

import uuid

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.enums import QueryStatus
from backend.app.models.query import Query
from backend.app.repositories.base import BaseRepository


class QueryRepository(BaseRepository[Query]):
    """Data access for user Shariah reasoning queries."""

    model = Query

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
        *,
        include_archived: bool = False,
    ) -> list[Query]:
        """Return a user's query history, newest first."""
        stmt = select(Query).where(Query.user_id == user_id)
        if not include_archived:
            stmt = stmt.where(Query.archived.is_(False))
        stmt = stmt.order_by(Query.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search_by_user(
        self,
        user_id: uuid.UUID,
        query_text: str,
        *,
        limit: int = 20,
    ) -> list[Query]:
        """Search user queries by question or display title."""
        pattern = f"%{query_text.strip()}%"
        stmt = (
            select(Query)
            .where(
                Query.user_id == user_id,
                Query.archived.is_(False),
                or_(Query.question.ilike(pattern), Query.display_title.ilike(pattern)),
            )
            .order_by(Query.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update_status(self, query: Query, status: QueryStatus) -> Query:
        """Update query processing status."""
        query.status = status
        await self.session.flush()
        await self.session.refresh(query)
        return query

    async def update_metadata(
        self,
        query: Query,
        *,
        display_title: str | None = None,
        archived: bool | None = None,
        folder: str | None = None,
        tags: list[str] | None = None,
        unset_folder: bool = False,
    ) -> Query:
        """Update user-managed conversation metadata."""
        if display_title is not None:
            query.display_title = display_title.strip() or None
        if archived is not None:
            query.archived = archived
        if unset_folder:
            query.folder = None
        elif folder is not None:
            query.folder = folder.strip() or None
        if tags is not None:
            query.tags = [tag.strip() for tag in tags if tag.strip()][:20]
        await self.session.flush()
        await self.session.refresh(query)
        return query

    async def delete(self, query: Query) -> None:
        """Delete a query and its related response."""
        await self.session.delete(query)
        await self.session.flush()

    async def list_by_session(
        self,
        user_id: uuid.UUID,
        session_id: str,
        *,
        limit: int = 4,
    ) -> list[Query]:
        """Return recent completed queries in a chat session."""
        stmt = (
            select(Query)
            .where(
                Query.user_id == user_id,
                Query.session_id == session_id,
                Query.status == QueryStatus.COMPLETED,
            )
            .order_by(Query.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_session_chronological(
        self,
        user_id: uuid.UUID,
        session_id: str,
        *,
        limit: int = 20,
    ) -> list[Query]:
        """Return completed queries in a chat session, oldest first."""
        stmt = (
            select(Query)
            .where(
                Query.user_id == user_id,
                Query.session_id == session_id,
                Query.status == QueryStatus.COMPLETED,
            )
            .order_by(Query.created_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_recent_with_session(
        self,
        user_id: uuid.UUID,
        *,
        limit: int = 200,
        include_archived: bool = False,
    ) -> list[Query]:
        """Return recent queries that have a session_id (for conversation grouping)."""
        stmt = select(Query).where(
            Query.user_id == user_id,
            Query.session_id.is_not(None),
        )
        if not include_archived:
            stmt = stmt.where(Query.archived.is_(False))
        stmt = stmt.order_by(Query.created_at.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
