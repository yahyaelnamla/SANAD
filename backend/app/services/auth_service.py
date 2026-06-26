"""Authentication service — registration, login, profile."""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserProfileResponse,
)
from backend.app.auth.security import create_access_token, hash_password, verify_password
from backend.app.config.settings import get_settings
from backend.app.exceptions import UnauthorizedError, ValidationError
from backend.app.models.enums import UserRole
from backend.app.models.user import User
from backend.app.repositories.user_repository import UserRepository


class AuthService:
    """Business logic for user authentication."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)
        self.settings = get_settings()

    async def register(self, request: RegisterRequest) -> UserProfileResponse:
        """Create a new user account."""
        existing = await self.user_repo.get_by_email(request.email)
        if existing is not None:
            raise ValidationError("Email is already registered.")

        user = User(
            email=request.email.lower(),
            password_hash=hash_password(request.password),
            role=UserRole.USER,
            locale=request.locale,
            onboarding_completed=False,
        )
        created = await self.user_repo.create(user)
        return self._to_profile(created)

    async def login(self, request: LoginRequest) -> TokenResponse:
        """Authenticate user and return JWT access token."""
        user = await self.user_repo.get_by_email(request.email.lower())
        if user is None or user.password_hash is None:
            raise UnauthorizedError("Invalid email or password.")
        if not verify_password(request.password, user.password_hash):
            raise UnauthorizedError("Invalid email or password.")

        token = create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role.value,
        )
        return TokenResponse(
            access_token=token,
            expires_in=self.settings.jwt_expire_minutes * 60,
        )

    async def get_profile(self, user: User) -> UserProfileResponse:
        """Return the authenticated user's profile."""
        return self._to_profile(user)

    @staticmethod
    def _to_profile(user: User) -> UserProfileResponse:
        return UserProfileResponse(
            id=str(user.id),
            email=user.email,
            role=user.role.value,
            locale=user.locale,
            subscription_tier=user.subscription_tier.value,
            subscription_status=user.subscription_status.value,
            onboarding_completed=user.onboarding_completed,
            auth_provider=user.auth_provider.value,
        )
