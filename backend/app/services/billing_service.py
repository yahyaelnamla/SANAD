"""SaaS billing — plans, checkout, and subscription management."""

from __future__ import annotations

import secrets
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.exceptions import NotFoundError, ValidationError
from backend.app.models.enums import SubscriptionStatus, SubscriptionTier
from backend.app.models.user import User
from backend.app.repositories.user_repository import UserRepository
from backend.app.schemas.billing_schemas import (
    BillingPlanSchema,
    CheckoutConfirmResponse,
    CheckoutRequest,
    CheckoutResponse,
    SubscriptionSchema,
)

PLANS: list[BillingPlanSchema] = [
    BillingPlanSchema(
        id="free",
        name="Free",
        price_label="$0",
        price_cents=0,
        interval=None,
        features=[
            "Full platform access",
            "Evidence-based chat",
            "Company & portfolio tools",
        ],
        recommended=True,
    ),
    BillingPlanSchema(
        id="enterprise",
        name="Enterprise",
        price_label="Contact us",
        price_cents=None,
        interval=None,
        features=[
            "Custom API access",
            "SSO & SAML",
            "Private source packs",
            "SLA support",
        ],
    ),
]

TIER_LIMITS: dict[str, int | None] = {
    SubscriptionTier.FREE.value: None,
    SubscriptionTier.PRO.value: None,
    SubscriptionTier.ENTERPRISE.value: None,
}

_DEMO_CHECKOUT_SESSIONS: dict[str, dict[str, Any]] = {}


class BillingService:
    """Manage subscription plans and checkout sessions."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)

    @staticmethod
    def list_plans() -> list[BillingPlanSchema]:
        return PLANS

    async def get_subscription(self, user: User) -> SubscriptionSchema:
        tier = user.subscription_tier.value
        queries_used = await self._count_monthly_queries(user.id)
        return SubscriptionSchema(
            tier=tier,
            status=user.subscription_status.value,
            queries_limit=TIER_LIMITS.get(tier),
            queries_used=queries_used,
            renews_at=self._next_renewal_iso(user),
        )

    async def create_checkout(self, user: User, request: CheckoutRequest) -> CheckoutResponse:
        tier = request.tier
        if tier != SubscriptionTier.ENTERPRISE.value:
            raise ValidationError("Only enterprise inquiries are supported. Contact us for organization plans.")

        session_id = secrets.token_urlsafe(24)
        _DEMO_CHECKOUT_SESSIONS[session_id] = {
            "user_id": str(user.id),
            "tier": tier,
            "created_at": datetime.now(UTC).isoformat(),
        }
        return CheckoutResponse(
            session_id=session_id,
            mode="demo",
            checkout_url=None,
            tier=tier,
        )

    async def confirm_checkout(self, user: User, session_id: str) -> CheckoutConfirmResponse:
        session = _DEMO_CHECKOUT_SESSIONS.pop(session_id, None)
        if session is None or session.get("user_id") != str(user.id):
            raise NotFoundError("Checkout session not found or expired.")

        tier_value = session["tier"]
        tier = SubscriptionTier(tier_value)
        user.subscription_tier = tier
        user.subscription_status = SubscriptionStatus.ACTIVE
        await self.user_repo.session.flush()
        await self.user_repo.session.refresh(user)

        return CheckoutConfirmResponse(
            tier=tier.value,
            status=user.subscription_status.value,
            message="Subscription upgraded successfully.",
        )

    async def cancel_subscription(self, user: User) -> SubscriptionSchema:
        if user.subscription_tier == SubscriptionTier.FREE:
            raise ValidationError("Free plan cannot be canceled.")
        user.subscription_tier = SubscriptionTier.FREE
        user.subscription_status = SubscriptionStatus.CANCELED
        await self.user_repo.session.flush()
        await self.user_repo.session.refresh(user)
        return await self.get_subscription(user)

    async def _count_monthly_queries(self, user_id: Any) -> int:
        from sqlalchemy import func, select

        from backend.app.models.query import Query

        month_start = datetime.now(UTC).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        stmt = select(func.count()).select_from(Query).where(
            Query.user_id == user_id,
            Query.created_at >= month_start,
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    @staticmethod
    def _next_renewal_iso(user: User) -> str | None:
        if user.subscription_tier == SubscriptionTier.FREE:
            return None
        now = datetime.now(UTC)
        if now.month == 12:
            renewal = now.replace(year=now.year + 1, month=1, day=1)
        else:
            renewal = now.replace(month=now.month + 1, day=1)
        return renewal.date().isoformat()
