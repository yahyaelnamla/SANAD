"""Single sign-on API endpoints."""

from fastapi import APIRouter

from backend.app.api.deps import DbSession
from backend.app.schemas.sso_schemas import (
    SsoCompleteRequest,
    SsoCompleteResponse,
    SsoProviderSchema,
    SsoStartRequest,
    SsoStartResponse,
)
from backend.app.services.sso_service import SsoService

router = APIRouter(prefix="/auth/sso", tags=["SSO"])


@router.get("/providers", response_model=list[SsoProviderSchema])
async def list_sso_providers(session: DbSession) -> list[SsoProviderSchema]:
    """List enabled SSO identity providers."""
    return SsoService(session).list_providers()


@router.post("/start", response_model=SsoStartResponse)
async def start_sso(request: SsoStartRequest, session: DbSession) -> SsoStartResponse:
    """Begin an OAuth or demo SSO flow."""
    return await SsoService(session).start(request)


@router.post("/complete", response_model=SsoCompleteResponse)
async def complete_sso(
    request: SsoCompleteRequest,
    session: DbSession,
) -> SsoCompleteResponse:
    """Complete SSO login and return a JWT access token."""
    return await SsoService(session).complete(request)
