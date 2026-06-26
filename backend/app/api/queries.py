"""Query API endpoints for Shariah reasoning."""

import uuid

from fastapi import APIRouter, BackgroundTasks, Query, Response
from fastapi.responses import StreamingResponse

from backend.app.api.deps import CurrentUser, DbSession
from backend.app.config.settings import get_settings
from backend.app.schemas.query_schemas import (
    QueryCreateRequest,
    QueryExportResponse,
    QueryListItemSchema,
    QueryListResponse,
    QueryResultSchema,
    QueryUpdateRequest,
)
from backend.app.services.query_service import QueryService, process_query_background
from backend.app.services.query_stream import stream_query_events

router = APIRouter(prefix="/queries", tags=["Queries"])


@router.post(
    "",
    response_model=QueryResultSchema,
    summary="Submit a Shariah reasoning query",
    responses={
        201: {"description": "Synchronous result (QUERY_ASYNC=false)"},
        202: {"description": "Query accepted; poll GET /queries/{id} for results"},
        422: {"description": "No authenticated evidence found (NO_EVIDENCE)"},
    },
)
async def submit_query(
    request: QueryCreateRequest,
    session: DbSession,
    user: CurrentUser,
    background_tasks: BackgroundTasks,
    response: Response,
) -> QueryResultSchema:
    """Enqueue or run the multi-agent pipeline and return the explainability chain."""
    service = QueryService(session)
    settings = get_settings()

    if settings.query_async:
        accepted = await service.enqueue_query(user, request)
        await session.commit()
        background_tasks.add_task(
            process_query_background,
            accepted.query_id,
            request,
        )
        response.status_code = 202
        return accepted

    response.status_code = 201
    return await service._submit_query_sync(user, request)


@router.get(
    "/{query_id}/stream",
    summary="Stream query progress and response via SSE",
    responses={
        200: {
            "description": "text/event-stream with status, token, section, and complete events",
            "content": {"text/event-stream": {}},
        },
    },
)
async def stream_query(
    query_id: uuid.UUID,
    session: DbSession,
    user: CurrentUser,
) -> StreamingResponse:
    """Stream agent progress, summary tokens, and response sections."""
    service = QueryService(session)

    async def event_generator():
        async for chunk in stream_query_events(service, user, query_id):
            yield chunk

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get(
    "/{query_id}/export",
    response_model=QueryExportResponse,
    summary="Export query as markdown",
)
async def export_query(
    query_id: uuid.UUID,
    session: DbSession,
    user: CurrentUser,
) -> QueryExportResponse:
    """Export a query and its explainability chain as markdown."""
    service = QueryService(session)
    return await service.export_query(user, query_id)


@router.get(
    "/{query_id}",
    response_model=QueryResultSchema,
    summary="Get query status and response",
)
async def get_query(
    query_id: uuid.UUID,
    session: DbSession,
    user: CurrentUser,
) -> QueryResultSchema:
    """Retrieve a previously submitted query and its analysis."""
    service = QueryService(session)
    return await service.get_query(user, query_id)


@router.patch(
    "/{query_id}",
    response_model=QueryListItemSchema,
    summary="Update conversation metadata",
)
async def update_query(
    query_id: uuid.UUID,
    request: QueryUpdateRequest,
    session: DbSession,
    user: CurrentUser,
) -> QueryListItemSchema:
    """Rename, archive, tag, or folder a conversation."""
    service = QueryService(session)
    return await service.update_query(user, query_id, request)


@router.delete(
    "/{query_id}",
    status_code=204,
    summary="Delete a conversation",
)
async def delete_query(
    query_id: uuid.UUID,
    session: DbSession,
    user: CurrentUser,
) -> None:
    """Permanently delete a conversation."""
    service = QueryService(session)
    await service.delete_query(user, query_id)


@router.get(
    "",
    response_model=QueryListResponse,
    summary="List user query history",
)
async def list_queries(
    session: DbSession,
    user: CurrentUser,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    include_archived: bool = Query(default=False),
) -> QueryListResponse:
    """Return the authenticated user's query history."""
    service = QueryService(session)
    return await service.list_queries(
        user,
        limit=limit,
        offset=offset,
        include_archived=include_archived,
    )
