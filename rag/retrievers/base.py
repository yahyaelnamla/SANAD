"""Retrieved chunk with citation metadata."""

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from backend.app.models.source import Source
from backend.app.models.source_chunk import SourceChunk


@dataclass
class RetrievedChunk:
    """A chunk retrieved from the knowledge base with scoring metadata."""

    chunk_id: UUID
    source_id: UUID
    content: str
    score: float
    source_title: str
    source_author: str
    source_type: str
    language: str
    citation: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_evidence_dict(self) -> dict[str, Any]:
        """Convert to evidence format for the explainability chain."""
        return {
            "text": self.content,
            "source_id": str(self.source_id),
            "chunk_id": str(self.chunk_id),
            "citation": self.citation,
            "source_title": self.source_title,
            "source_author": self.source_author,
            "source_type": self.source_type,
            "language": self.language,
            "score": self.score,
            "metadata": self.metadata,
        }


def build_retrieved_chunk(chunk: SourceChunk, source: Source, score: float) -> RetrievedChunk:
    """Map ORM entities to a RetrievedChunk with citation."""
    citation = f"{source.author}. {source.title}."
    if source.url:
        citation = f"{citation} {source.url}"

    metadata: dict[str, Any] = dict(chunk.metadata_ or {})
    metadata.update(
        {
            "chunk_index": chunk.chunk_index,
            "is_authenticated": source.is_authenticated,
            "source_url": source.url,
        }
    )

    return RetrievedChunk(
        chunk_id=chunk.id,
        source_id=source.id,
        content=chunk.content,
        score=score,
        source_title=source.title,
        source_author=source.author,
        source_type=source.source_type.value,
        language=source.language,
        citation=citation.strip(),
        metadata=metadata,
    )
