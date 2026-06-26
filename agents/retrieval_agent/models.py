"""Retrieval Agent data models."""

from pydantic import BaseModel, Field

from agents.common.evidence import EvidenceItem


class RetrievalAgentResult(BaseModel):
    """Output from the Retrieval Agent."""

    query: str
    chunks: list[EvidenceItem] = Field(default_factory=list)
    refused: bool = False
    reason: str | None = None

    @property
    def has_evidence(self) -> bool:
        return bool(self.chunks) and not self.refused
