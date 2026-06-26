"""User document repository."""

import uuid

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.user_document import UserDocument
from backend.app.repositories.base import BaseRepository


class UserDocumentRepository(BaseRepository[UserDocument]):
    """Data access for persisted user PDF documents."""

    model = UserDocument

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_by_user(self, user_id: uuid.UUID, *, limit: int = 50) -> list[UserDocument]:
        stmt = (
            select(UserDocument)
            .where(UserDocument.user_id == user_id)
            .order_by(UserDocument.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search_by_user(
        self,
        user_id: uuid.UUID,
        query_text: str,
        *,
        limit: int = 8,
    ) -> list[UserDocument]:
        pattern = f"%{query_text.strip()}%"
        stmt = (
            select(UserDocument)
            .where(
                UserDocument.user_id == user_id,
                or_(
                    UserDocument.filename.ilike(pattern),
                    UserDocument.summary.ilike(pattern),
                    UserDocument.search_text.ilike(pattern),
                ),
            )
            .order_by(UserDocument.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_owned(self, user_id: uuid.UUID, document_id: uuid.UUID) -> UserDocument | None:
        stmt = select(UserDocument).where(
            UserDocument.id == document_id,
            UserDocument.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
