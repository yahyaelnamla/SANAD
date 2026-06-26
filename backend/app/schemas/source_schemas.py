"""Pydantic schemas for source management endpoints."""

from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl

from backend.app.models.enums import SourceType


class SourceCreateRequest(BaseModel):
    """Payload for adding a new knowledge source."""

    title: str = Field(min_length=1, max_length=500)
    author: str = Field(min_length=1, max_length=255)
    source_type: SourceType
    language: str = Field(default="ar", pattern=r"^(ar|en)$")
    url: HttpUrl | None = None
    is_authenticated: bool = False


class SourceUpdateRequest(BaseModel):
    """Payload for updating source metadata or authentication status."""

    title: str | None = Field(default=None, min_length=1, max_length=500)
    author: str | None = Field(default=None, min_length=1, max_length=255)
    source_type: SourceType | None = None
    language: str | None = Field(default=None, pattern=r"^(ar|en)$")
    url: HttpUrl | None = None
    is_authenticated: bool | None = None


class SourceResponse(BaseModel):
    """Serialized knowledge source."""

    id: str
    title: str
    author: str
    source_type: str
    language: str
    url: str | None
    is_authenticated: bool
    created_at: datetime


class SourceListResponse(BaseModel):
    """Paginated source list."""

    items: list[SourceResponse]
    total: int


class AdminStatsResponse(BaseModel):
    """Admin dashboard aggregate metrics."""

    total_sources: int
    authenticated_sources: int
    pending_sources: int


class AdminDailyQueryCount(BaseModel):
    date: str
    count: int


class AdminModelUsage(BaseModel):
    model: str
    count: int


class AdminAnalyticsResponse(BaseModel):
    """Extended admin analytics for query volume and Fanar usage."""

    total_sources: int
    authenticated_sources: int
    pending_sources: int
    total_queries: int
    completed_queries: int
    failed_queries: int
    refused_queries: int
    refusal_rate: float
    average_latency_ms: float | None = None
    queries_by_day: list[AdminDailyQueryCount] = Field(default_factory=list)
    model_usage: list[AdminModelUsage] = Field(default_factory=list)
