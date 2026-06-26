"""Source ORM model for authenticated knowledge references."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base, CreatedAtMixin, UUIDPrimaryKeyMixin
from backend.app.models.enums import SourceType, enum_column

if TYPE_CHECKING:
    from backend.app.models.source_chunk import SourceChunk


class Source(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    """Authenticated jurisprudential or financial knowledge source."""

    __tablename__ = "sources"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[SourceType] = mapped_column(
        enum_column(SourceType, "source_type"),
        nullable=False,
        index=True,
    )
    language: Mapped[str] = mapped_column(String(5), nullable=False)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_authenticated: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True
    )

    chunks: Mapped[list[SourceChunk]] = relationship(
        back_populates="source",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Source id={self.id} title={self.title!r}>"
