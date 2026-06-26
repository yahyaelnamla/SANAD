"""Pydantic schemas for backend ↔ RAG integration."""

from typing import Any

from pydantic import BaseModel, Field, field_validator


class RAGIngestRequest(BaseModel):
    """Request to ingest content into the knowledge base."""

    content: str
    source_title: str
    source_author: str
    source_type: str
    language: str = "ar"
    url: str | None = None
    is_authenticated: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("content must not be empty")
        return v.strip()

    @field_validator("source_title", "source_author")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("field must not be empty")
        return v.strip()

    @field_validator("language")
    @classmethod
    def language_supported(cls, v: str) -> str:
        supported = {"ar", "en", "fr", "ur", "tr", "ms"}
        if v not in supported:
            raise ValueError(f"language must be one of {supported}")
        return v


class RAGRetrieveRequest(BaseModel):
    """Request to retrieve evidence for a query."""

    query: str
    top_k: int = Field(default=5, ge=1, le=20)
    language: str | None = None

    @field_validator("query")
    @classmethod
    def query_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("query must not be empty")
        return v.strip()


class RAGEvidenceItem(BaseModel):
    """Single evidence item with mandatory citation."""

    text: str
    source_id: str
    chunk_id: str
    citation: str
    source_title: str
    source_author: str
    source_type: str
    language: str
    score: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class RAGRetrieveResponse(BaseModel):
    """Response from RAG retrieval."""

    query: str
    refused: bool
    reason: str | None = None
    evidence: list[RAGEvidenceItem] = Field(default_factory=list)

    @property
    def has_evidence(self) -> bool:
        return bool(self.evidence) and not self.refused


class RAGIngestResponse(BaseModel):
    """Response after ingesting a document."""

    source_id: str
    message: str = "Document ingested successfully"
