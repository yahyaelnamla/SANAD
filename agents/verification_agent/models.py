"""Verification Agent data models."""

from pydantic import BaseModel, Field


class VerificationIssue(BaseModel):
    """A single integrity check failure."""

    code: str
    message: str


class VerificationResult(BaseModel):
    """Output from the Verification Agent."""

    approved: bool
    issues: list[VerificationIssue] = Field(default_factory=list)
    reason: str | None = None
    guard_scores: dict | None = None
