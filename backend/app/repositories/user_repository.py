"""User repository."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.enums import AuthProvider
from backend.app.models.user import User
from backend.app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Data access for User entities."""

    model = User

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_email(self, email: str) -> User | None:
        """Find a user by email address."""
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_sso_subject(self, provider: str, subject: str) -> User | None:
        """Find a user by SSO provider subject identifier."""
        stmt = select(User).where(
            User.auth_provider == AuthProvider(provider),
            User.sso_subject == subject,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
