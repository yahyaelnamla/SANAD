"""Shared SQLAlchemy enums for SANAD models."""

import enum
from typing import TypeVar

from sqlalchemy import Enum as SAEnum

_E = TypeVar("_E", bound=enum.Enum)


def enum_column(enum_class: type[_E], name: str) -> SAEnum:
    """Map a Python enum to a VARCHAR column using member **values** (not names).

    Alembic migrations store lowercase values (e.g. ``free``). Without
    ``values_callable``, SQLAlchemy defaults to member names (``FREE``) and
    raises LookupError when reading existing rows.
    """
    return SAEnum(
        enum_class,
        name=name,
        native_enum=False,
        values_callable=lambda obj: [member.value for member in obj],
    )


class UserRole(str, enum.Enum):
    """User access role."""

    USER = "user"
    ADMIN = "admin"
    REVIEWER = "reviewer"


class SourceType(str, enum.Enum):
    """Knowledge source classification."""

    CLASSICAL = "classical"
    CONTEMPORARY = "contemporary"
    STANDARD = "standard"
    FATWA = "fatwa"


class QueryStatus(str, enum.Enum):
    """Query processing lifecycle status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class SubscriptionTier(str, enum.Enum):
    """SaaS subscription plan tier."""

    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str, enum.Enum):
    """Subscription billing lifecycle status."""

    ACTIVE = "active"
    TRIALING = "trialing"
    CANCELED = "canceled"
    PAST_DUE = "past_due"


class AuthProvider(str, enum.Enum):
    """Identity provider used for sign-in."""

    EMAIL = "email"
    GOOGLE = "google"
    MICROSOFT = "microsoft"
