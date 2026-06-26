"""Shared ingestion data structures."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class IngestedDocument:
    """Standardized document produced by any ingestion loader."""

    content: str
    source_title: str
    source_author: str
    language: str = "ar"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.content.strip():
            raise ValueError("Ingested document content cannot be empty")
