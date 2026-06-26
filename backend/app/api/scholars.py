"""Scholar profile API."""

from fastapi import APIRouter, HTTPException, Query

from backend.app.api.deps import CurrentUser, DbSession
from backend.app.schemas.scholar_schemas import ScholarListResponse, ScholarProfileSchema
from backend.app.services.scholar_service import ScholarService

router = APIRouter(prefix="/scholars", tags=["Scholars"])


@router.get("", response_model=ScholarListResponse, summary="Browse scholar profiles")
async def list_scholars(
    session: DbSession,
    user: CurrentUser,
    q: str | None = Query(default=None, max_length=120),
    limit: int = Query(default=50, ge=1, le=100),
) -> ScholarListResponse:
    """Return scholar directory merged from seed profiles and authenticated sources."""
    _ = user
    service = ScholarService(session)
    return await service.list_scholars(query=q, limit=limit)


@router.get("/{slug}", response_model=ScholarProfileSchema, summary="Scholar profile detail")
async def get_scholar(
    slug: str,
    session: DbSession,
    user: CurrentUser,
) -> ScholarProfileSchema:
    """Return a single scholar profile with sources and opinion samples."""
    _ = user
    service = ScholarService(session)
    profile = await service.get_scholar(slug)
    if profile is None:
        raise HTTPException(status_code=404, detail="Scholar not found")
    return profile
