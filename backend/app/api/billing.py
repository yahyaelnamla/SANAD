"""Billing and subscription API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends

from backend.app.api.deps import DbSession
from backend.app.auth.dependencies import get_current_user
from backend.app.models.user import User
from backend.app.schemas.billing_schemas import (
    BillingPlanSchema,
    CheckoutConfirmRequest,
    CheckoutConfirmResponse,
    CheckoutRequest,
    CheckoutResponse,
    SubscriptionSchema,
)
from backend.app.services.billing_service import BillingService

router = APIRouter(prefix="/billing", tags=["Billing"])


@router.get("/plans", response_model=list[BillingPlanSchema])
async def list_plans() -> list[BillingPlanSchema]:
    """Return public SaaS pricing plans."""
    return BillingService.list_plans()


@router.get("/subscription", response_model=SubscriptionSchema)
async def get_subscription(
    session: DbSession,
    user: Annotated[User, Depends(get_current_user)],
) -> SubscriptionSchema:
    """Return the authenticated user's subscription snapshot."""
    return await BillingService(session).get_subscription(user)


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    request: CheckoutRequest,
    session: DbSession,
    user: Annotated[User, Depends(get_current_user)],
) -> CheckoutResponse:
    """Start a subscription checkout session."""
    return await BillingService(session).create_checkout(user, request)


@router.post("/checkout/confirm", response_model=CheckoutConfirmResponse)
async def confirm_checkout(
    request: CheckoutConfirmRequest,
    session: DbSession,
    user: Annotated[User, Depends(get_current_user)],
) -> CheckoutConfirmResponse:
    """Confirm a demo checkout session and upgrade the subscription."""
    return await BillingService(session).confirm_checkout(user, request.session_id)


@router.post("/cancel", response_model=SubscriptionSchema)
async def cancel_subscription(
    session: DbSession,
    user: Annotated[User, Depends(get_current_user)],
) -> SubscriptionSchema:
    """Downgrade to the free plan."""
    return await BillingService(session).cancel_subscription(user)
