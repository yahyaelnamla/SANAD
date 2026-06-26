"""Text chunking utilities."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TextChunk:
    """A chunk of text ready for embedding."""

    content: str
    chunk_index: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.content.strip():
            raise ValueError("Chunk content cannot be empty")
