"""Source chunk ORM model with pgvector embedding."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from backend.app.models.source import Source

EMBEDDING_DIMENSION = 3584


class SourceChunk(Base, UUIDPrimaryKeyMixin):
    """Text chunk from a source with vector embedding for RAG retrieval."""

    __tablename__ = "source_chunks"

    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(EMBEDDING_DIMENSION), nullable=True
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB, nullable=True)

    source: Mapped[Source] = relationship(back_populates="chunks")

    def __repr__(self) -> str:
        return f"<SourceChunk id={self.id} source_id={self.source_id} index={self.chunk_index}>"
