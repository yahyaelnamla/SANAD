"""Response ORM model storing the explainability chain."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base, CreatedAtMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from backend.app.models.query import Query


class Response(Base, UUIDPrimaryKeyMixin, CreatedAtMixin):
    """Structured response following Evidence → Principles → Reasoning → Analysis."""

    __tablename__ = "responses"

    query_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("queries.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    principles: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    opinions: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    sources: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_breakdown: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    agent_trace: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    thinking_trace: Mapped[str | None] = mapped_column(Text, nullable=True)
    financial_context: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    execution_metrics: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    madhhab_matrix: Mapped[list[Any]] = mapped_column(JSONB, nullable=False, default=list)
    suggested_questions: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    refused: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    refusal_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    query: Mapped[Query] = relationship(back_populates="response")

    def __repr__(self) -> str:
        return f"<Response id={self.id} query_id={self.query_id} confidence={self.confidence}>"
