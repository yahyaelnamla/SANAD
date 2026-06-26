"""User onboarding wizard service."""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.user import User
from backend.app.repositories.user_repository import UserRepository
from backend.app.schemas.onboarding_schemas import OnboardingStatusResponse, OnboardingUpdateRequest
from backend.app.schemas.user_preferences_schemas import UserPreferencesUpdateRequest
from backend.app.services.user_preferences_service import UserPreferencesService


class OnboardingService:
    """Persist onboarding funnel progress and completion."""

    USE_CASE_KEY = "use_case"

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)

    def get_status(self, user: User) -> OnboardingStatusResponse:
        prefs = user.preferences or {}
        use_case = prefs.get(self.USE_CASE_KEY)
        return OnboardingStatusResponse(
            completed=user.onboarding_completed,
            use_case=use_case,
        )

    async def update(
        self,
        user: User,
        request: OnboardingUpdateRequest,
    ) -> OnboardingStatusResponse:
        if request.locale is not None:
            user.locale = request.locale

        if (
            request.display_name is not None
            or request.preferred_madhhab is not None
            or request.favorite_scholars is not None
        ):
            pref_service = UserPreferencesService(self.user_repo)
            pref_payload = UserPreferencesUpdateRequest()
            if request.display_name is not None:
                pref_payload.display_name = request.display_name.strip() or None
            if request.preferred_madhhab is not None:
                pref_payload.preferred_madhhab = request.preferred_madhhab
            if request.favorite_scholars is not None:
                pref_payload.favorite_scholars = request.favorite_scholars
            await pref_service.update_preferences(user, pref_payload)

        if request.use_case is not None:
            prefs = dict(user.preferences or {})
            prefs[self.USE_CASE_KEY] = request.use_case
            user.preferences = prefs

        if request.completed:
            user.onboarding_completed = True

        await self.user_repo.session.flush()
        await self.user_repo.session.refresh(user)
        return self.get_status(user)
