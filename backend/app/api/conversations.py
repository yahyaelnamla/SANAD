"""Conversation thread API endpoints."""

from fastapi import APIRouter, Query

from backend.app.api.deps import CurrentUser, DbSession
from backend.app.schemas.conversation_schemas import (
    ConversationListResponse,
    ConversationThreadSchema,
)
from backend.app.services.conversation_service import ConversationService

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.get(
    "",
    response_model=ConversationListResponse,
    summary="List grouped conversation threads",
)
async def list_conversations(
    session: DbSession,
    user: CurrentUser,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    include_archived: bool = Query(default=False),
) -> ConversationListResponse:
    """Return conversations grouped by session_id."""
    service = ConversationService(session)
    return await service.list_conversations(
        user,
        limit=limit,
        offset=offset,
        include_archived=include_archived,
    )


@router.get(
    "/{session_id}",
    response_model=ConversationThreadSchema,
    summary="Load a full conversation thread",
)
async def get_conversation_thread(
    session_id: str,
    session: DbSession,
    user: CurrentUser,
) -> ConversationThreadSchema:
    """Restore all messages and full query results for a chat session."""
    service = ConversationService(session)
    return await service.get_thread(user, session_id)
