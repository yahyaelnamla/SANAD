"""Response repository."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.response import Response
from backend.app.repositories.base import BaseRepository


class ResponseRepository(BaseRepository[Response]):
    """Data access for structured explainability responses."""

    model = Response

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_query_id(self, query_id: uuid.UUID) -> Response | None:
        """Fetch the response linked to a query."""
        stmt = select(Response).where(Response.query_id == query_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
