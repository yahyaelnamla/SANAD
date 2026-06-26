"""Unit tests for Zakat calculation with currencies and live prices."""

from unittest.mock import AsyncMock, patch

import pytest

from backend.app.schemas.feature_schemas import ZakatAssetsRequest, ZakatHolding
from backend.app.services.zakat_service import calculate_zakat


@pytest.mark.asyncio
async def test_zakat_manual_values_without_live_prices() -> None:
    request = ZakatAssetsRequest(
        cash=10000,
        cash_currency="USD",
        gold_grams=50,
        gold_price_per_gram=80,
        gold_price_currency="USD",
        stocks=20000,
        crypto=5000,
        debts=2000,
        debt_currency="USD",
        output_currency="USD",
        fetch_live_prices=False,
        include_ai_guidance=False,
    )
    result = await calculate_zakat(request)
    assert result.net_wealth > 0
    assert result.zakat_due >= 0
    assert result.output_currency == "USD"
    assert result.gold_price_per_gram == 80
    gold_row = next(row for row in result.asset_breakdown if row.category == "gold")
    assert gold_row.quantity_display == "50 g"
    assert gold_row.unit_price_display == "80.00 USD/g"


@pytest.mark.asyncio
async def test_zakat_with_mocked_live_holdings() -> None:
    request = ZakatAssetsRequest(
        cash=5000,
        cash_currency="USD",
        gold_grams=10,
        stock_holdings=[ZakatHolding(symbol="AAPL", quantity=2, asset_type="stock")],
        crypto_holdings=[ZakatHolding(symbol="BTC", quantity=0.1, asset_type="crypto")],
        debts=0,
        output_currency="USD",
        fetch_live_prices=True,
        include_ai_guidance=False,
    )

    with (
        patch(
            "backend.app.services.zakat_service.fetch_fx_rates",
            new=AsyncMock(return_value={"USD": 1.0, "EUR": 0.92}),
        ),
        patch(
            "backend.app.services.zakat_service.fetch_gold_price_per_gram",
            new=AsyncMock(return_value=(75.0, "test")),
        ),
        patch(
            "backend.app.services.zakat_service.resolve_holding_value",
            new=AsyncMock(side_effect=[(400.0, 200.0, "test", "USD"), (3000.0, 30000.0, "test", "USD")]),
        ),
    ):
        result = await calculate_zakat(request)

    assert result.live_prices_used is True
    assert len(result.asset_breakdown) >= 3
    assert result.net_wealth > 5000
