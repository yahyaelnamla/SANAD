"""Response Builder data models."""

from typing import Any

from pydantic import BaseModel, Field

from agents.common.evidence import EvidenceItem
from agents.knowledge_agent.models import JurisprudentialPrinciple
from agents.reasoning_agent.models import ScholarlyOpinion


class FinalResponse(BaseModel):
    """Structured final output following the explainability chain."""

    summary: str
    evidence: list[EvidenceItem] = Field(default_factory=list)
    principles: list[JurisprudentialPrinciple] = Field(default_factory=list)
    reasoning: str
    opinions: list[ScholarlyOpinion] = Field(default_factory=list)
    sources: list[dict[str, Any]] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    confidence_breakdown: dict[str, float] = Field(default_factory=dict)
    language: str = "en"
    refused: bool = False
    refusal_reason: str | None = None
    agent_trace: list[dict[str, Any]] = Field(default_factory=list)
    thinking_trace: str | None = None
    financial_context: dict[str, Any] | None = None
    execution_metrics: dict[str, Any] | None = None
    madhhab_matrix: list[dict[str, Any]] = Field(default_factory=list)
    suggested_questions: list[str] = Field(default_factory=list)
