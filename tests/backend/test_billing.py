"""Tests for SaaS billing endpoints."""

import httpx
import pytest


@pytest.mark.asyncio
async def test_list_billing_plans(async_client: httpx.AsyncClient) -> None:
    response = await async_client.get("/api/v1/billing/plans")
    assert response.status_code == 200
    plans = response.json()
    assert len(plans) == 2
    assert plans[0]["id"] == "free"
    assert plans[0]["recommended"] is True
    assert plans[1]["id"] == "enterprise"


@pytest.mark.asyncio
async def test_subscription_free_tier(
    async_client: httpx.AsyncClient,
    auth_headers: dict,
) -> None:
    sub = await async_client.get("/api/v1/billing/subscription", headers=auth_headers)
    assert sub.status_code == 200
    assert sub.json()["tier"] == "free"


@pytest.mark.asyncio
async def test_checkout_rejects_paid_tiers(
    async_client: httpx.AsyncClient,
    auth_headers: dict,
) -> None:
    response = await async_client.post(
        "/api/v1/billing/checkout",
        headers=auth_headers,
        json={"tier": "pro"},
    )
    assert response.status_code == 400
