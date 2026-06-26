"""Authentication and RBAC FastAPI dependencies."""

import uuid
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.auth.security import decode_access_token
from backend.app.config.database import get_db
from backend.app.exceptions import ForbiddenError, UnauthorizedError
from backend.app.models.enums import UserRole
from backend.app.models.user import User
from backend.app.repositories.user_repository import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    session: Annotated[AsyncSession, Depends(get_db)],
    credentials: Annotated[
        HTTPAuthorizationCredentials | None,
        Depends(bearer_scheme),
    ],
) -> User:
    """Resolve the authenticated user from a JWT Bearer token."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError("Missing or invalid authorization header.")

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = uuid.UUID(payload["sub"])
    except (ValueError, KeyError) as exc:
        raise UnauthorizedError("Invalid or expired access token.") from exc

    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)
    if user is None:
        raise UnauthorizedError("User not found.")
    return user


def require_roles(*roles: UserRole) -> Callable:
    """Dependency factory enforcing RBAC role membership."""

    async def checker(user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.role not in roles:
            raise ForbiddenError(
                f"Role '{user.role.value}' is not permitted for this resource.",
            )
        return user

    return checker


RequireAdmin = Annotated[User, Depends(require_roles(UserRole.ADMIN))]
RequireReviewer = Annotated[User, Depends(require_roles(UserRole.ADMIN, UserRole.REVIEWER))]
