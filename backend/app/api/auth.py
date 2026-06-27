"""Authentication API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends

from backend.app.api.deps import DbSession
from backend.app.auth.dependencies import RequireAdmin, get_current_user
from backend.app.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserProfileResponse,
)
from backend.app.models.user import User
from backend.app.repositories.user_repository import UserRepository
from backend.app.schemas.onboarding_schemas import OnboardingStatusResponse, OnboardingUpdateRequest
from backend.app.schemas.user_preferences_schemas import (
    UserPreferencesSchema,
    UserPreferencesUpdateRequest,
)
from backend.app.services.auth_service import AuthService
from backend.app.services.onboarding_service import OnboardingService
from backend.app.services.user_preferences_service import UserPreferencesService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserProfileResponse, status_code=201)
async def register(request: RegisterRequest, session: DbSession) -> UserProfileResponse:
    """Register a new user account."""
    service = AuthService(session)
    return await service.register(request)


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, session: DbSession) -> TokenResponse:
    """Authenticate and receive a JWT access token."""
    service = AuthService(session)
    return await service.login(request)


@router.get("/me", response_model=UserProfileResponse)
async def get_me(user: Annotated[User, Depends(get_current_user)]) -> UserProfileResponse:
    """Return the authenticated user's profile."""
    return AuthService._to_profile(user)


@router.get("/admin/ping")
async def admin_ping(_admin: RequireAdmin) -> dict[str, str]:
    """RBAC probe — admin role required."""
    return {"status": "ok", "message": "Admin access granted."}


@router.get("/me/preferences", response_model=UserPreferencesSchema)
async def get_preferences(
    session: DbSession,
    user: Annotated[User, Depends(get_current_user)],
) -> UserPreferencesSchema:
    """Return persisted user preferences."""
    repo = UserRepository(session)
    db_user = await repo.get_by_id(user.id)
    if db_user is None:
        return UserPreferencesSchema()
    return UserPreferencesService(repo).get_preferences(db_user)


@router.patch("/me/preferences", response_model=UserPreferencesSchema)
async def update_preferences(
    request: UserPreferencesUpdateRequest,
    session: DbSession,
    user: Annotated[User, Depends(get_current_user)],
) -> UserPreferencesSchema:
    """Update user preferences (madhhab, scholars, bookmarks, etc.)."""
    repo = UserRepository(session)
    db_user = await repo.get_by_id(user.id)
    if db_user is None:
        return UserPreferencesSchema()
    service = UserPreferencesService(repo)
    return await service.update_preferences(db_user, request)


@router.get("/me/onboarding", response_model=OnboardingStatusResponse)
async def get_onboarding(
    session: DbSession,
    user: Annotated[User, Depends(get_current_user)],
) -> OnboardingStatusResponse:
    """Return onboarding completion status."""
    repo = UserRepository(session)
    db_user = await repo.get_by_id(user.id)
    if db_user is None:
        return OnboardingStatusResponse(completed=True)
    return OnboardingService(session).get_status(db_user)


@router.patch("/me/onboarding", response_model=OnboardingStatusResponse)
async def update_onboarding(
    request: OnboardingUpdateRequest,
    session: DbSession,
    user: Annotated[User, Depends(get_current_user)],
) -> OnboardingStatusResponse:
    """Persist onboarding wizard progress."""
    repo = UserRepository(session)
    db_user = await repo.get_by_id(user.id)
    if db_user is None:
        return OnboardingStatusResponse(completed=True)
    return await OnboardingService(session).update(db_user, request)
