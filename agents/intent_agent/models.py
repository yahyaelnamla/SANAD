"""Intent Agent data models."""

from enum import Enum

from pydantic import BaseModel, Field


class IntentType(str, Enum):
    """Classification of user query intent."""

    SHARIAH_RULING = "shariah_ruling"
    COMPLIANCE_SCREENING = "compliance_screening"
    COMPARATIVE_OPINION = "comparative_opinion"
    DEFINITION = "definition"
    GENERAL_INQUIRY = "general_inquiry"


class IntentResult(BaseModel):
    """Structured output from the Intent Agent."""

    raw_query: str
    intent_type: IntentType
    domain: str
    language: str
    entities: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
