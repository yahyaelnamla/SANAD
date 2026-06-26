"""User onboarding schemas."""

from typing import Literal

from pydantic import BaseModel, Field

UseCaseChoice = Literal["personal", "student", "professional", "institution"]


class OnboardingUpdateRequest(BaseModel):
    """Persist onboarding wizard progress."""

    display_name: str | None = Field(default=None, max_length=80)
    locale: str | None = Field(default=None, pattern=r"^(ar|en)$")
    preferred_madhhab: str | None = Field(
        default=None,
        pattern=r"^(hanafi|maliki|shafii|hanbali|general)$",
    )
    favorite_scholars: list[str] | None = Field(default=None, max_length=20)
    use_case: UseCaseChoice | None = None
    completed: bool = False


class OnboardingStatusResponse(BaseModel):
    """Onboarding completion state."""

    completed: bool
    use_case: UseCaseChoice | None = None
