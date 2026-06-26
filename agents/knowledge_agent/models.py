"""Knowledge Agent data models."""

from typing import Any

from pydantic import BaseModel, Field

from agents.common.evidence import EvidenceItem


class JurisprudentialPrinciple(BaseModel):
    """A fiqh principle (qa'idah) with citation."""

    name: str
    description: str
    citation: str


class EvidenceBundle(BaseModel):
    """Structured evidence bundle for the Reasoning Agent."""

    evidences: list[EvidenceItem] = Field(default_factory=list)
    principles: list[JurisprudentialPrinciple] = Field(default_factory=list)
    source_ids: list[str] = Field(default_factory=list)
    rejected_count: int = 0

    @property
    def has_valid_evidence(self) -> bool:
        return bool(self.evidences)

    def to_context_dict(self) -> dict[str, Any]:
        """Serialize for downstream agents."""
        return {
            "evidences": [e.model_dump() for e in self.evidences],
            "principles": [p.model_dump() for p in self.principles],
            "source_ids": self.source_ids,
        }
