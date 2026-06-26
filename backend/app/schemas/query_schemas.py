"""Pydantic schemas for query API endpoints."""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from backend.app.models.enums import QueryStatus


class ConfidenceBreakdownSchema(BaseModel):
    """Factor-level confidence decomposition."""

    retrieval: float = 0.0
    grounding: float = 0.0
    model: float = 0.0
    guard: float = 0.0
    verification: float = 0.0
    scholarly_coverage: float = 0.0


class ConversationTurnSchema(BaseModel):
    """Single turn in client-side conversation history."""

    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1, max_length=12000)


class QueryCreateRequest(BaseModel):
    """Request body for submitting a Shariah reasoning query."""

    question: str = Field(..., min_length=3, max_length=5000)
    language: Literal["ar", "en"] | None = Field(
        default=None,
        description="Preferred response language; auto-detected if omitted.",
    )
    session_id: str | None = Field(
        default=None,
        max_length=64,
        description="Chat session identifier for conversation memory.",
    )
    conversation_history: list[ConversationTurnSchema] | None = Field(
        default=None,
        max_length=30,
        description="Recent turns for follow-up context (user + assistant).",
    )
    advanced_analysis: bool = Field(
        default=False,
        description="Force deep pipeline with expanded source retrieval for researchers.",
    )
    fanar_model: Literal["auto", "sadiq", "c2", "guard"] = Field(
        default="auto",
        description="Preferred Fanar model; auto selects based on question complexity.",
    )


class EvidenceSchema(BaseModel):
    """Retrieved evidence with mandatory citation."""

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


class PrincipleSchema(BaseModel):
    """Applicable fiqh principle with citation."""

    name: str
    description: str
    citation: str


class OpinionSchema(BaseModel):
    """Scholarly opinion with supporting citations and bibliographic metadata."""

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


class MadhhabPositionSchema(BaseModel):
    """School-of-thought position for comparative matrix."""

    school: str
    position: str
    alignment: str = "mixed"
    source: str | None = None


class MarketQuoteSchema(BaseModel):
    """Live market quote for financial screening context."""

    symbol: str
    price: float | None = None
    currency: str | None = None
    market_cap: float | None = None
    exchange: str | None = None


class FinancialContextSchema(BaseModel):
    """Structured financial context from the Financial Context Agent."""

    entities: list[str] = Field(default_factory=list)
    notes: str = ""
    has_external_data: bool = False
    screening_notes: list[str] = Field(default_factory=list)
    market_quotes: list[MarketQuoteSchema] = Field(default_factory=list)


class ExecutionMetricsSchema(BaseModel):
    """Aggregated pipeline execution telemetry."""

    total_latency_ms: int = 0
    steps_completed: int = 0
    steps_total: int = 0
    models_used: list[str] = Field(default_factory=list)
    tokens_estimate: int | None = None
    pipeline_depth: str | None = None
    document_context_used: bool | None = None
    conversation_memory_used: bool | None = None
    auto_mode: str | None = None
    fanar_capabilities: dict[str, str] | None = None


class SourceSchema(BaseModel):
    """Deduplicated source reference."""

    source_id: str
    title: str
    author: str
    type: str
    citation: str
    source_url: str | None = None


class AgentTraceSchema(BaseModel):
    """Live agent execution telemetry."""

    phase: str
    agent: str
    model: str
    status: str = "pending"
    latency_ms: int | None = None
    started_at: str | None = None
    completed_at: str | None = None
    tokens_estimate: int | None = None


class QueryResultSchema(BaseModel):
    """Explainability chain response per API_SPEC.md."""

    query_id: UUID
    status: QueryStatus
    question: str
    language: str
    summary: str | None = None
    evidence: list[EvidenceSchema] = Field(default_factory=list)
    principles: list[PrincipleSchema] = Field(default_factory=list)
    reasoning: str | None = None
    opinions: list[OpinionSchema] = Field(default_factory=list)
    sources: list[SourceSchema] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    confidence_breakdown: ConfidenceBreakdownSchema | None = None
    refused: bool = False
    refusal_reason: str | None = None
    agent_trace: list[AgentTraceSchema] = Field(default_factory=list)
    thinking_trace: str | None = None
    financial_context: FinancialContextSchema | None = None
    execution_metrics: ExecutionMetricsSchema | None = None
    madhhab_matrix: list[MadhhabPositionSchema] = Field(default_factory=list)
    suggested_questions: list[str] = Field(default_factory=list)
    draft_summary: str | None = None
    created_at: datetime


class QueryListItemSchema(BaseModel):
    """Summary item for query history listing."""

    query_id: UUID
    question: str
    display_title: str | None = None
    language: str
    status: QueryStatus
    summary: str | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    refused: bool = False
    archived: bool = False
    folder: str | None = None
    tags: list[str] = Field(default_factory=list)
    session_id: str | None = None
    turn_count: int = 1
    created_at: datetime


class QueryUpdateRequest(BaseModel):
    """Partial update for conversation metadata."""

    display_title: str | None = Field(default=None, max_length=500)
    archived: bool | None = None
    folder: str | None = Field(default=None, max_length=120)
    tags: list[str] | None = Field(default=None, max_length=20)


class QueryExportResponse(BaseModel):
    """Markdown export payload for a query."""

    query_id: UUID
    filename: str
    content: str
    format: Literal["markdown"] = "markdown"


class QueryListResponse(BaseModel):
    """Paginated query history."""

    items: list[QueryListItemSchema]
    total: int
    limit: int
    offset: int
