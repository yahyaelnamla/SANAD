"""Evaluation dashboard API for hackathon judges."""

from fastapi import APIRouter

from backend.app.api.deps import CurrentUser, DbSession
from backend.app.schemas.evaluation_schemas import EvaluationDashboardSchema, EvaluationHarnessSchema
from backend.app.services.evaluation_harness_service import build_evaluation_harness
from backend.app.services.evaluation_service import EvaluationService

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])


@router.get("/dashboard", response_model=EvaluationDashboardSchema)
async def evaluation_dashboard(
    user: CurrentUser,
    session: DbSession,
) -> EvaluationDashboardSchema:
    """Return Fanar capability demo data and aggregated pipeline metrics."""
    service = EvaluationService(session)
    return await service.get_dashboard(user)


@router.get("/harness", response_model=EvaluationHarnessSchema)
async def evaluation_harness(
    user: CurrentUser,
) -> EvaluationHarnessSchema:
    """Return reproducible hackathon scoring scenarios and rubric."""
    _ = user
    return build_evaluation_harness()
