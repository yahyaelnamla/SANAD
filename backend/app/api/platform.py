"""Platform integration API for partners and institutions."""

from fastapi import APIRouter, Depends

from backend.app.api.deps import DbSession
from backend.app.auth.dependencies import get_current_user
from backend.app.auth.platform_auth import require_platform_api_key
from backend.app.config.settings import get_settings
from backend.app.models.user import User
from backend.app.schemas.evaluation_schemas import EvaluationHarnessSchema
from backend.app.schemas.query_schemas import QueryCreateRequest, QueryResultSchema
from backend.app.services.evaluation_harness_service import build_evaluation_harness
from backend.app.services.query_service import QueryService

router = APIRouter(prefix="/platform", tags=["Platform"])


@router.get("/status")
async def platform_status(
    _: None = Depends(require_platform_api_key),
) -> dict:
    """Return platform API status and capabilities."""
    settings = get_settings()
    return {
        "status": "ok",
        "service": "sanad-platform",
        "version": settings.app_version,
        "capabilities": [
            "shariah_query",
            "document_analysis",
            "company_scanner",
            "portfolio_scanner",
            "evaluation_harness",
        ],
        "docs": f"{settings.api_prefix}/docs",
    }


@router.get("/harness", response_model=EvaluationHarnessSchema)
async def platform_harness(
    _: None = Depends(require_platform_api_key),
) -> EvaluationHarnessSchema:
    """Return hackathon evaluation harness test cases."""
    return build_evaluation_harness()


@router.post("/queries", response_model=QueryResultSchema)
async def platform_submit_query(
    request: QueryCreateRequest,
    session: DbSession,
    user: User = Depends(get_current_user),
    _: None = Depends(require_platform_api_key),
) -> QueryResultSchema:
    """Submit a Shariah query via platform API (requires platform key + user JWT)."""
    service = QueryService(session)
    return await service.submit_query(user, request)
