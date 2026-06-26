"""Schemas for hackathon evaluation / judge dashboard."""

from __future__ import annotations

from pydantic import BaseModel, Field


class EvaluationStatsSchema(BaseModel):
    """Aggregated pipeline statistics for judge review."""

    total_completed_queries: int = 0
    average_latency_ms: float | None = None
    average_tokens_estimate: float | None = None
    total_tokens_estimate: int | None = None
    unique_models_used: list[str] = Field(default_factory=list)
    guard_pass_rate: float | None = None
    fast_pipeline_count: int = 0
    deep_pipeline_count: int = 0
    document_memory_queries: int = 0
    voice_ready: bool = True


class DemoPromptSchema(BaseModel):
    """One-click demo scenario for judges."""

    id: str
    title: str
    description: str
    fanar_product: str
    route: str
    question: str | None = None


class FeatureMatrixRowSchema(BaseModel):
    """Maps a SANAD capability to Fanar products."""

    id: str
    feature: str
    fanar_products: list[str]
    description: str


class RecentQueryMetricSchema(BaseModel):
    """Lightweight recent query row for the dashboard."""

    query_id: str
    question: str
    latency_ms: float | None = None
    tokens_estimate: int | None = None
    pipeline_depth: str | None = None
    models_used: list[str] = Field(default_factory=list)
    refused: bool = False


class EvaluationDashboardSchema(BaseModel):
    """Full judge dashboard payload."""

    fanar_capabilities: dict[str, str]
    fanar_capability_improvements: dict[str, str] = Field(default_factory=dict)
    stats: EvaluationStatsSchema
    demo_prompts: list[DemoPromptSchema]
    feature_matrix: list[FeatureMatrixRowSchema]
    recent_queries: list[RecentQueryMetricSchema]
    limitations: list[str] = Field(default_factory=list)
    future_fanar_suggestions: list[str] = Field(default_factory=list)


class HarnessCaseSchema(BaseModel):
    """Single hackathon scoring scenario."""

    id: str
    category: str
    question: str
    language: str = "en"
    expects_refusal: bool = False
    expects_evidence: bool = True
    expects_fanar_guard: bool = True
    rubric: list[str] = Field(default_factory=list)


class EvaluationHarnessSchema(BaseModel):
    """Reproducible hackathon evaluation harness."""

    version: str = "1.0"
    total_cases: int
    categories: list[str]
    cases: list[HarnessCaseSchema]
    scoring_notes: list[str] = Field(default_factory=list)
