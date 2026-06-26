"""Metadata filtering for authenticated source retrieval."""

from dataclasses import dataclass

from backend.app.models.enums import SourceType
from rag.retrievers.base import RetrievedChunk


@dataclass
class MetadataFilter:
    """Filter criteria applied to retrieved chunks."""

    authenticated_only: bool = True
    source_type: SourceType | None = None
    language: str | None = None

    def apply(self, chunks: list[RetrievedChunk]) -> list[RetrievedChunk]:
        """Filter retrieved chunks by metadata criteria."""
        filtered = chunks
        if self.authenticated_only:
            filtered = [chunk for chunk in filtered if chunk.metadata.get("is_authenticated", True)]
        if self.source_type is not None:
            filtered = [chunk for chunk in filtered if chunk.source_type == self.source_type.value]
        if self.language is not None:
            filtered = [chunk for chunk in filtered if chunk.language == self.language]
        return filtered
