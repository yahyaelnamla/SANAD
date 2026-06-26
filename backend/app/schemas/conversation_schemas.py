"""Pydantic schemas for conversation thread APIs."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from backend.app.schemas.query_schemas import QueryResultSchema


class ConversationMessageSchema(BaseModel):
    """Single message in a persisted conversation thread."""

    message_id: str
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime
    query_id: UUID | None = None
    result: QueryResultSchema | None = None


class ConversationThreadSchema(BaseModel):
    """Full conversation thread for chat resume."""

    session_id: str
    title: str
    language: str
    message_count: int
    turn_count: int
    created_at: datetime
    updated_at: datetime
    messages: list[ConversationMessageSchema] = Field(default_factory=list)


class ConversationListItemSchema(BaseModel):
    """Grouped conversation summary for history sidebar."""

    session_id: str
    title: str
    language: str
    turn_count: int
    message_count: int
    preview: str | None = None
    last_query_id: UUID
    refused: bool = False
    archived: bool = False
    created_at: datetime
    updated_at: datetime


class ConversationListResponse(BaseModel):
    """Paginated conversation list."""

    items: list[ConversationListItemSchema]
    total: int
    limit: int
    offset: int
