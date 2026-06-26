"""Zakat calculation service with multi-currency and live price support."""

from __future__ import annotations

import asyncio

from backend.app.schemas.feature_schemas import (
    ZakatAssetBreakdown,
    ZakatAssetsRequest,
    ZakatCalculationResponse,
)
from backend.app.services.zakat_ai_service import generate_zakat_guidance
from backend.app.services.zakat_formatters import format_quantity_display, format_unit_price_display
from backend.app.services.zakat_price_service import (
    convert_amount,
    fetch_crypto_price,
    fetch_fx_rates,
    fetch_gold_price_per_gram,
    fetch_stock_price,
    normalize_currency,
    resolve_holding_value,
)

NISAB_GOLD_GRAMS = 85.0
ZAKAT_RATE = 0.025


def _breakdown_row(
    *,
    category: str,
    label: str,
    amount: float,
    currency: str,
    value_in_output_currency: float,
    unit_price: float | None = None,
    quantity: float | None = None,
) -> ZakatAssetBreakdown:
    return ZakatAssetBreakdown(
        category=category,
        label=label,
        amount=amount,
        currency=currency,
        value_in_output_currency=value_in_output_currency,
        unit_price=unit_price,
        quantity=quantity,
        quantity_display=format_quantity_display(
            category=category,
            amount=amount,
            currency=currency,
            quantity=quantity,
            label=label,
        ),
        unit_price_display=format_unit_price_display(
            category=category,
            unit_price=unit_price,
            currency=currency,
        ),
    )


async def calculate_zakat(request: ZakatAssetsRequest) -> ZakatCalculationResponse:
    """Calculate Zakat with currency conversion and optional live market prices."""
    output_currency = normalize_currency(request.output_currency)
    cash_currency = normalize_currency(request.cash_currency)
    debt_currency = normalize_currency(request.debt_currency)
    gold_currency = normalize_currency(request.gold_price_currency)

    rates = await fetch_fx_rates("USD")
    breakdown: list[ZakatAssetBreakdown] = []
    price_sources: dict[str, str] = {}

    cash_value = await convert_amount(request.cash, cash_currency, output_currency, rates)
    if request.cash > 0:
        breakdown.append(
            _breakdown_row(
                category="cash",
                label=f"Cash ({cash_currency})",
                amount=request.cash,
                currency=cash_currency,
                value_in_output_currency=round(cash_value, 2),
                quantity=request.cash,
            )
        )

    if request.fetch_live_prices and request.gold_price_per_gram is None:
        gold_price, gold_source = await fetch_gold_price_per_gram(gold_currency)
        price_sources["gold"] = gold_source
    else:
        gold_price = request.gold_price_per_gram or 75.0
        if request.gold_price_per_gram is not None and gold_currency != "USD":
            gold_price = await convert_amount(gold_price, gold_currency, gold_currency, rates)

    gold_value = request.gold_grams * gold_price
    if request.gold_grams > 0:
        breakdown.append(
            _breakdown_row(
                category="gold",
                label="Gold",
                amount=request.gold_grams,
                currency=gold_currency,
                value_in_output_currency=round(gold_value, 2),
                unit_price=round(gold_price, 2),
                quantity=request.gold_grams,
            )
        )

    stocks_total = 0.0
    if request.fetch_live_prices and request.stock_holdings:
        stock_tasks = [
            resolve_holding_value(
                asset_type="stock",
                symbol=holding.symbol,
                quantity=holding.quantity,
                output_currency=output_currency,
                rates=rates,
            )
            for holding in request.stock_holdings
        ]
        stock_results = await asyncio.gather(*stock_tasks)
        for holding, (value, unit_price, source, quote_currency) in zip(
            request.stock_holdings, stock_results, strict=True
        ):
            stocks_total += value
            price_sources[f"stock:{holding.symbol.upper()}"] = source
            breakdown.append(
                _breakdown_row(
                    category="stock",
                    label=holding.symbol.upper(),
                    amount=holding.quantity,
                    currency=quote_currency or "USD",
                    value_in_output_currency=value,
                    unit_price=unit_price,
                    quantity=holding.quantity,
                )
            )
    elif request.stocks > 0:
        stocks_total = request.stocks
        breakdown.append(
            _breakdown_row(
                category="stock",
                label="Stocks (manual)",
                amount=request.stocks,
                currency=output_currency,
                value_in_output_currency=round(stocks_total, 2),
            )
        )

    crypto_total = 0.0
    if request.fetch_live_prices and request.crypto_holdings:
        crypto_tasks = [
            resolve_holding_value(
                asset_type="crypto",
                symbol=holding.symbol,
                quantity=holding.quantity,
                output_currency=output_currency,
                rates=rates,
            )
            for holding in request.crypto_holdings
        ]
        crypto_results = await asyncio.gather(*crypto_tasks)
        for holding, (value, unit_price, source, _quote_currency) in zip(
            request.crypto_holdings, crypto_results, strict=True
        ):
            crypto_total += value
            price_sources[f"crypto:{holding.symbol.upper()}"] = source
            breakdown.append(
                _breakdown_row(
                    category="crypto",
                    label=holding.symbol.upper(),
                    amount=holding.quantity,
                    currency="USD",
                    value_in_output_currency=value,
                    unit_price=unit_price,
                    quantity=holding.quantity,
                )
            )
    elif request.crypto > 0:
        crypto_total = request.crypto
        breakdown.append(
            _breakdown_row(
                category="crypto",
                label="Crypto (manual)",
                amount=request.crypto,
                currency=output_currency,
                value_in_output_currency=round(crypto_total, 2),
            )
        )

    debts_value = await convert_amount(request.debts, debt_currency, output_currency, rates)
    if request.debts > 0:
        breakdown.append(
            _breakdown_row(
                category="debt",
                label=f"Debts ({debt_currency})",
                amount=request.debts,
                currency=debt_currency,
                value_in_output_currency=round(-debts_value, 2),
                quantity=request.debts,
            )
        )

    total_wealth = cash_value + gold_value + stocks_total + crypto_total
    net_wealth = max(total_wealth - debts_value, 0.0)
    nisab_threshold = NISAB_GOLD_GRAMS * gold_price
    is_above_nisab = net_wealth >= nisab_threshold
    zakat_due = round(net_wealth * ZAKAT_RATE, 2) if is_above_nisab else 0.0

    notes = [
        f"All values normalized to {output_currency} using live FX where available.",
        f"Nisab estimated at 85g gold @ {gold_price:,.2f} {gold_currency}/g.",
        "Zakat rate applied: 2.5% on net zakatable wealth after deductible debts.",
    ]
    if not is_above_nisab:
        notes.append("Wealth is below nisab — no Zakat is due on these assets.")
    if request.debts > 0:
        notes.append("Outstanding debts were deducted before calculating net wealth.")
    if request.fetch_live_prices:
        notes.append("Stock, crypto, and gold prices fetched from live market data.")

    ai_guidance = None
    if request.include_ai_guidance:
        asset_summary = ", ".join(
            f"{item.label}={item.value_in_output_currency:,.0f} {output_currency}"
            for item in breakdown
            if item.category != "debt"
        )
        ai_guidance = await generate_zakat_guidance(
            net_wealth=net_wealth,
            zakat_due=zakat_due,
            output_currency=output_currency,
            is_above_nisab=is_above_nisab,
            asset_summary=asset_summary or "none",
            language=request.language,
        )

    return ZakatCalculationResponse(
        total_wealth=round(total_wealth, 2),
        net_wealth=round(net_wealth, 2),
        nisab_threshold=round(nisab_threshold, 2),
        zakat_due=zakat_due,
        is_above_nisab=is_above_nisab,
        gold_value=round(gold_value, 2),
        rate=ZAKAT_RATE,
        notes=notes,
        output_currency=output_currency,
        gold_price_per_gram=round(gold_price, 2),
        gold_price_currency=gold_currency,
        asset_breakdown=breakdown,
        price_sources=price_sources,
        ai_guidance=ai_guidance,
        live_prices_used=request.fetch_live_prices,
    )


async def fetch_zakat_prices(
    *,
    output_currency: str = "USD",
    gold_currency: str = "USD",
    stock_symbols: list[str] | None = None,
    crypto_symbols: list[str] | None = None,
) -> dict:
    """Return live prices for Zakat calculator UI."""
    output_currency = normalize_currency(output_currency)
    gold_currency = normalize_currency(gold_currency)
    rates = await fetch_fx_rates("USD")

    gold_price, gold_source = await fetch_gold_price_per_gram(gold_currency)
    stocks: dict[str, dict] = {}
    crypto: dict[str, dict] = {}

    for symbol in stock_symbols or []:
        price, quote_currency, source = await fetch_stock_price(symbol)
        if price is not None:
            converted = await convert_amount(price, quote_currency or "USD", output_currency, rates)
            stocks[symbol.upper()] = {
                "unit_price": price,
                "quote_currency": quote_currency or "USD",
                "value_currency": output_currency,
                "unit_price_converted": round(converted, 2),
                "source": source,
            }

    for symbol in crypto_symbols or []:
        price, source = await fetch_crypto_price(symbol)
        if price is not None:
            converted = await convert_amount(price, "USD", output_currency, rates)
            crypto[symbol.upper()] = {
                "unit_price_usd": price,
                "value_currency": output_currency,
                "unit_price_converted": round(converted, 2),
                "source": source,
            }

    return {
        "output_currency": output_currency,
        "gold_price_per_gram": gold_price,
        "gold_price_currency": gold_currency,
        "gold_source": gold_source,
        "stocks": stocks,
        "crypto": crypto,
        "fx_source": "Frankfurter",
    }
