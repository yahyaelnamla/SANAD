"""Tests for user preferences service."""

from backend.app.models.enums import UserRole
from backend.app.models.user import User
from backend.app.repositories.user_repository import UserRepository
from backend.app.schemas.user_preferences_schemas import UserPreferencesUpdateRequest
from backend.app.services.user_preferences_service import UserPreferencesService


async def test_update_and_record_topic(db_session):
    repo = UserRepository(db_session)
    user = User(
        email="prefs@example.com",
        password_hash="hash",
        role=UserRole.USER,
        locale="en",
    )
    await repo.create(user)

    service = UserPreferencesService(repo)
    updated = await service.update_preferences(
        user,
        UserPreferencesUpdateRequest(
            preferred_madhhab="hanafi",
            favorite_scholars=["Ibn Rushd"],
        ),
    )
    assert updated.preferred_madhhab == "hanafi"
    assert "Ibn Rushd" in updated.favorite_scholars

    await service.record_recent_topic(user, "Is Bitcoin halal?")
    prefs = service.get_preferences(user)
    assert prefs.recent_topics[0] == "Is Bitcoin halal?"
