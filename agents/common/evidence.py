"""Shared evidence item used across agents."""

from typing import Any

from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    """Single piece of evidence with mandatory citation."""

    text: str
    source_id: str
    chunk_id: str
    citation: str
    source_title: str
    source_author: str
    source_type: str
    language: str
    score: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)
