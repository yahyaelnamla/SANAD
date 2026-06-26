"""Conversation thread service — group queries by session and restore full threads."""

from __future__ import annotations

import uuid
from collections import defaultdict
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.exceptions import ForbiddenError, NotFoundError
from backend.app.models.enums import QueryStatus
from backend.app.models.query import Query
from backend.app.models.user import User
from backend.app.repositories.query_repository import QueryRepository
from backend.app.repositories.response_repository import ResponseRepository
from backend.app.schemas.conversation_schemas import (
    ConversationListItemSchema,
    ConversationListResponse,
    ConversationMessageSchema,
    ConversationThreadSchema,
)
from backend.app.services.conversation_memory_service import _build_assistant_turn_content


class ConversationService:
    """Load and list multi-turn chat sessions."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.query_repo = QueryRepository(session)
        self.response_repo = ResponseRepository(session)

    async def get_thread(self, user: User, session_id: str) -> ConversationThreadSchema:
        """Return all messages in a conversation thread, chronologically."""
        queries = await self.query_repo.list_by_session_chronological(
            user.id,
            session_id,
            limit=50,
        )
        if not queries:
            owned = await self._find_any_session_query(user.id, session_id)
            if owned is None:
                raise NotFoundError(f"Conversation {session_id} not found.")
            raise NotFoundError(f"Conversation {session_id} has no completed messages yet.")

        messages: list[ConversationMessageSchema] = []
        for query in queries:
            messages.append(
                ConversationMessageSchema(
                    message_id=f"user-{query.id}",
                    role="user",
                    content=query.question,
                    created_at=query.created_at,
                    query_id=query.id,
                )
            )
            response = await self.response_repo.get_by_query_id(query.id)
            if response is None:
                continue
            from backend.app.services.query_service import QueryService

            result = QueryService(self.session)._to_result_schema_from_orm(query, response)
            assistant_text = _build_assistant_turn_content(response) or (result.summary or "")
            messages.append(
                ConversationMessageSchema(
                    message_id=f"assistant-{query.id}",
                    role="assistant",
                    content=assistant_text,
                    created_at=query.created_at,
                    query_id=query.id,
                    result=result,
                )
            )

        first = queries[0]
        last = queries[-1]
        title = first.display_title or first.question
        return ConversationThreadSchema(
            session_id=session_id,
            title=title[:500],
            language=first.language,
            message_count=len(messages),
            turn_count=len(queries),
            created_at=first.created_at,
            updated_at=last.created_at,
            messages=messages,
        )

    async def list_conversations(
        self,
        user: User,
        *,
        limit: int = 50,
        offset: int = 0,
        include_archived: bool = False,
    ) -> ConversationListResponse:
        """Group recent queries into conversation threads."""
        queries = await self.query_repo.list_recent_with_session(
            user.id,
            limit=400,
            include_archived=include_archived,
        )

        grouped: dict[str, list[Query]] = defaultdict(list)
        for query in queries:
            if query.session_id:
                grouped[query.session_id].append(query)

        summaries: list[ConversationListItemSchema] = []
        for session_id, session_queries in grouped.items():
            ordered = sorted(session_queries, key=lambda item: item.created_at)
            first = ordered[0]
            last = ordered[-1]
            if not include_archived and all(item.archived for item in ordered):
                continue

            response = await self.response_repo.get_by_query_id(last.id)
            preview = response.summary if response else None
            summaries.append(
                ConversationListItemSchema(
                    session_id=session_id,
                    title=(first.display_title or first.question)[:500],
                    language=first.language,
                    turn_count=len(ordered),
                    message_count=len(ordered) * 2,
                    preview=(preview[:280] if preview else None),
                    last_query_id=last.id,
                    refused=last.status == QueryStatus.FAILED,
                    archived=all(item.archived for item in ordered),
                    created_at=first.created_at,
                    updated_at=last.created_at,
                )
            )

        summaries.sort(key=lambda item: item.updated_at, reverse=True)
        page = summaries[offset : offset + limit]
        return ConversationListResponse(
            items=page,
            total=len(summaries),
            limit=limit,
            offset=offset,
        )

    async def _find_any_session_query(self, user_id: uuid.UUID, session_id: str) -> Query | None:
        recent = await self.query_repo.list_recent_with_session(user_id, limit=400)
        for query in recent:
            if query.session_id == session_id and query.user_id == user_id:
                return query
        return None

    async def assert_session_owner(self, user: User, session_id: str) -> None:
        owned = await self._find_any_session_query(user.id, session_id)
        if owned is None:
            raise NotFoundError(f"Conversation {session_id} not found.")
        if owned.user_id != user.id:
            raise ForbiddenError("You do not have access to this conversation.")
