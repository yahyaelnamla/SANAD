"""User preferences — persist madhhab, scholars, saved items, and bookmarks."""

from __future__ import annotations

from typing import Any

from backend.app.models.user import User
from backend.app.repositories.user_repository import UserRepository
from backend.app.schemas.user_preferences_schemas import (
    UserPreferencesSchema,
    UserPreferencesUpdateRequest,
)

DEFAULT_PREFERENCES: dict[str, Any] = {
    "display_name": None,
    "preferred_madhhab": None,
    "favorite_scholars": [],
    "saved_companies": [],
    "saved_portfolios": [],
    "saved_portfolio_profiles": [],
    "recent_topics": [],
    "bookmarks": [],
}


def normalize_preferences(raw: dict[str, Any] | None) -> UserPreferencesSchema:
    """Coerce stored JSON into a validated preferences schema."""
    data = {**DEFAULT_PREFERENCES, **(raw or {})}
    return UserPreferencesSchema.model_validate(data)


class UserPreferencesService:
    """Read and update persisted user preferences."""

    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    def get_preferences(self, user: User) -> UserPreferencesSchema:
        return normalize_preferences(user.preferences)

    async def update_preferences(
        self,
        user: User,
        request: UserPreferencesUpdateRequest,
    ) -> UserPreferencesSchema:
        current = normalize_preferences(user.preferences).model_dump()
        patch = request.model_dump(exclude_unset=True)
        current.update(patch)
        user.preferences = current
        await self.user_repo.session.flush()
        await self.user_repo.session.refresh(user)
        return normalize_preferences(user.preferences)

    async def record_recent_topic(self, user: User, topic: str) -> None:
        """Append a deduplicated recent topic (newest first)."""
        cleaned = topic.strip()[:200]
        if not cleaned:
            return
        prefs = normalize_preferences(user.preferences)
        topics = [t for t in prefs.recent_topics if t.lower() != cleaned.lower()]
        topics.insert(0, cleaned)
        user.preferences = {
            **prefs.model_dump(),
            "recent_topics": topics[:30],
        }
        await self.user_repo.session.flush()
