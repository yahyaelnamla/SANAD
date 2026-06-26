"""User ORM model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from backend.app.models.enums import (
    AuthProvider,
    SubscriptionStatus,
    SubscriptionTier,
    UserRole,
    enum_column,
)

if TYPE_CHECKING:
    from backend.app.models.audit_log import AuditLog
    from backend.app.models.query import Query


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Platform user account."""

    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        enum_column(UserRole, "user_role"),
        default=UserRole.USER,
        nullable=False,
    )
    locale: Mapped[str] = mapped_column(String(5), default="ar", nullable=False)
    preferences: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    subscription_tier: Mapped[SubscriptionTier] = mapped_column(
        enum_column(SubscriptionTier, "subscription_tier"),
        default=SubscriptionTier.FREE,
        nullable=False,
    )
    subscription_status: Mapped[SubscriptionStatus] = mapped_column(
        enum_column(SubscriptionStatus, "subscription_status"),
        default=SubscriptionStatus.ACTIVE,
        nullable=False,
    )
    onboarding_completed: Mapped[bool] = mapped_column(default=False, nullable=False)
    auth_provider: Mapped[AuthProvider] = mapped_column(
        enum_column(AuthProvider, "auth_provider"),
        default=AuthProvider.EMAIL,
        nullable=False,
    )
    sso_subject: Mapped[str | None] = mapped_column(String(255), nullable=True)

    queries: Mapped[list[Query]] = relationship(back_populates="user", cascade="all, delete-orphan")
    audit_logs: Mapped[list[AuditLog]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"
