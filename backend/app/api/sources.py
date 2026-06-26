"""Source management API endpoints (admin/reviewer)."""

import uuid

from fastapi import APIRouter, Query

from backend.app.api.deps import DbSession
from backend.app.auth.dependencies import RequireReviewer
from backend.app.models.enums import SourceType
from backend.app.schemas.source_schemas import (
    SourceCreateRequest,
    SourceListResponse,
    SourceResponse,
    SourceUpdateRequest,
)
from backend.app.services.source_service import SourceService

router = APIRouter(prefix="/sources", tags=["Sources"])


@router.get("", response_model=SourceListResponse, summary="List knowledge sources")
async def list_sources(
    session: DbSession,
    _reviewer: RequireReviewer,
    is_authenticated: bool | None = Query(default=None),
    source_type: SourceType | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> SourceListResponse:
    """Return sources for admin review and management."""
    service = SourceService(session)
    return await service.list_sources(
        is_authenticated=is_authenticated,
        source_type=source_type,
        limit=limit,
        offset=offset,
    )


@router.post(
    "",
    response_model=SourceResponse,
    status_code=201,
    summary="Add a new knowledge source",
)
async def create_source(
    request: SourceCreateRequest,
    session: DbSession,
    actor: RequireReviewer,
) -> SourceResponse:
    """Create a source pending human authentication review."""
    service = SourceService(session)
    return await service.create_source(actor, request)


@router.put(
    "/{source_id}",
    response_model=SourceResponse,
    summary="Update source metadata or authentication",
)
async def update_source(
    source_id: uuid.UUID,
    request: SourceUpdateRequest,
    session: DbSession,
    actor: RequireReviewer,
) -> SourceResponse:
    """Update source fields including `is_authenticated` review status."""
    service = SourceService(session)
    return await service.update_source(actor, source_id, request)


@router.delete(
    "/{source_id}",
    status_code=204,
    summary="Remove a knowledge source",
)
async def delete_source(
    source_id: uuid.UUID,
    session: DbSession,
    actor: RequireReviewer,
) -> None:
    """Delete a source from the knowledge base."""
    service = SourceService(session)
    await service.delete_source(actor, source_id)
