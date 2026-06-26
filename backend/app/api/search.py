"""Global search API."""

from fastapi import APIRouter, Query

from backend.app.api.deps import CurrentUser, DbSession
from backend.app.schemas.feature_schemas import GlobalSearchResponse
from backend.app.services.search_service import global_search

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("", response_model=GlobalSearchResponse, summary="Global search")
async def search_all(
    session: DbSession,
    user: CurrentUser,
    q: str = Query(..., min_length=2, max_length=200),
    limit: int = Query(default=20, ge=1, le=50),
) -> GlobalSearchResponse:
    """Search chats, sources, scholars, companies, and documents."""
    return await global_search(session, user.id, q, limit=limit)
