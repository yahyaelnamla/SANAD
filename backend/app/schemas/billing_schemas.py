"""Billing and subscription schemas."""

from pydantic import BaseModel, Field


class BillingPlanSchema(BaseModel):
    """Public SaaS plan definition."""

    id: str
    name: str
    price_label: str
    price_cents: int | None = None
    interval: str | None = None
    features: list[str]
    recommended: bool = False


class SubscriptionSchema(BaseModel):
    """Current user subscription snapshot."""

    tier: str
    status: str
    queries_limit: int | None = None
    queries_used: int = 0
    renews_at: str | None = None


class CheckoutRequest(BaseModel):
    """Start a subscription checkout session."""

    tier: str = Field(pattern=r"^(pro|enterprise)$")
    success_url: str | None = None
    cancel_url: str | None = None


class CheckoutResponse(BaseModel):
    """Checkout session metadata."""

    session_id: str
    mode: str
    checkout_url: str | None = None
    tier: str


class CheckoutConfirmRequest(BaseModel):
    """Confirm a demo checkout session."""

    session_id: str = Field(min_length=8, max_length=128)


class CheckoutConfirmResponse(BaseModel):
    """Updated subscription after checkout confirmation."""

    tier: str
    status: str
    message: str
