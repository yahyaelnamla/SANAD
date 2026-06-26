"""Admin dashboard API endpoints."""

from fastapi import APIRouter

from backend.app.api.deps import DbSession
from backend.app.auth.dependencies import RequireReviewer
from backend.app.schemas.source_schemas import AdminAnalyticsResponse, AdminStatsResponse
from backend.app.services.admin_analytics_service import AdminAnalyticsService
from backend.app.services.source_service import SourceService

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats", response_model=AdminStatsResponse, summary="Admin dashboard metrics")
async def admin_stats(
    session: DbSession,
    _reviewer: RequireReviewer,
) -> AdminStatsResponse:
    """Return aggregate source metrics for the admin dashboard."""
    service = SourceService(session)
    return await service.get_admin_stats()


@router.get("/analytics", response_model=AdminAnalyticsResponse, summary="Admin analytics dashboard")
async def admin_analytics(
    session: DbSession,
    _reviewer: RequireReviewer,
) -> AdminAnalyticsResponse:
    """Return query volume, refusal rate, and Fanar model usage analytics."""
    service = AdminAnalyticsService(session)
    return await service.get_analytics()
