"""Query ORM model for user Shariah reasoning requests."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base, CreatedAtMixin, UUIDPrimaryKeyMixin
from backend.app.models.enums import QueryStatus, enum_column

if TYPE_CHECKING:
    from backend.app.models.response import Response
    from backend.app.models.user import User


class Query(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    """User-submitted Shariah financial reasoning query."""

    __tablename__ = "queries"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(5), nullable=False)
    status: Mapped[QueryStatus] = mapped_column(
        enum_column(QueryStatus, "query_status"),
        default=QueryStatus.PENDING,
        nullable=False,
    )
    display_title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    folder: Mapped[str | None] = mapped_column(String(120), nullable=True)
    tags: Mapped[list[str]] = mapped_column(JSONB, default=list, nullable=False)
    session_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    user: Mapped[User] = relationship(back_populates="queries")
    response: Mapped[Response | None] = relationship(
        back_populates="query",
        uselist=False,
        cascade="all, delete-orphan",
    )

    @property
    def title(self) -> str:
        """User-facing title (rename) or original question."""
        return self.display_title or self.question

    def __repr__(self) -> str:
        return f"<Query id={self.id} status={self.status.value}>"
