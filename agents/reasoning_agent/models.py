"""Reasoning Agent data models."""

from pydantic import BaseModel, Field


class ScholarlyOpinion(BaseModel):
    """A scholarly position with supporting citations and bibliographic metadata."""

    scholar: str
    position: str
    citations: list[str] = Field(default_factory=list)
    institution: str | None = None
    strength: str | None = None
    book: str | None = None
    fatwa: str | None = None
    page: str | None = None
    standard: str | None = None
    section: str | None = None
    date: str | None = None


class MadhhabPosition(BaseModel):
    """Position mapped to a school of thought or contemporary body."""

    school: str
    position: str
    alignment: str = "mixed"
    source: str | None = None


class ReasoningResult(BaseModel):
    """Jurisprudential analysis output (Takyeef Fiqhi)."""

    principles_applied: list[str] = Field(default_factory=list)
    qawaid_fiqhiyya: list[str] = Field(default_factory=list)
    adilla: list[str] = Field(default_factory=list)
    reasoning_steps: list[str] = Field(default_factory=list)
    thinking_trace: str | None = None
    analysis: str
    opinions: list[ScholarlyOpinion] = Field(default_factory=list)
    madhhab_matrix: list[MadhhabPosition] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    citations: list[str] = Field(default_factory=list)
    active_model: str | None = None
