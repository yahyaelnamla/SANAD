"""Live market and FX price fetching for Zakat calculations."""

from __future__ import annotations

import asyncio
import logging
from typing import Literal

import httpx

from agents.financial_context_agent.tools import fetch_live_quote

logger = logging.getLogger(__name__)

TROY_OZ_GRAMS = 31.1034768
SUPPORTED_CURRENCIES = (
    "USD",
    "EUR",
    "GBP",
    "SAR",
    "AED",
    "EGP",
    "QAR",
    "KWD",
    "BHD",
    "OMR",
    "PKR",
    "MYR",
    "TRY",
    "INR",
)

CRYPTO_TICKER_MAP: dict[str, str] = {
    "BTC": "BTC-USD",
    "BITCOIN": "BTC-USD",
    "ETH": "ETH-USD",
    "ETHEREUM": "ETH-USD",
    "SOL": "SOL-USD",
    "BNB": "BNB-USD",
    "XRP": "XRP-USD",
    "ADA": "ADA-USD",
    "DOGE": "DOGE-USD",
    "USDT": "USDT-USD",
    "USDC": "USDC-USD",
}

_fx_cache: dict[str, tuple[float, dict[str, float]]] = {}
_gold_cache: tuple[float, float] | None = None
GOLD_CACHE_TTL = 300.0
FX_CACHE_TTL = 3600.0


def normalize_currency(code: str) -> str:
    normalized = code.strip().upper()
    if normalized not in SUPPORTED_CURRENCIES:
        return "USD"
    return normalized


async def fetch_fx_rates(base: str = "USD") -> dict[str, float]:
    """Fetch FX rates with USD as pivot; returns {currency: units_per_usd}."""
    import time

    base = normalize_currency(base)
    now = time.monotonic()
    cached = _fx_cache.get(base)
    if cached and now - cached[0] < FX_CACHE_TTL:
        return cached[1]

    rates: dict[str, float] = {base: 1.0}
    try:
        targets = [c for c in SUPPORTED_CURRENCIES if c != base]
        url = f"https://api.frankfurter.app/latest?from={base}&to={','.join(targets)}"
        async with httpx.AsyncClient(timeout=8.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
        for currency, rate in data.get("rates", {}).items():
            rates[currency] = float(rate)
    except (httpx.HTTPError, ValueError, TypeError) as exc:
        logger.warning("FX fetch failed, using USD-only fallback: %s", exc)
        for currency in SUPPORTED_CURRENCIES:
            rates.setdefault(currency, 1.0 if currency == "USD" else 1.0)

    if base != "USD":
        usd_rates = await fetch_fx_rates("USD")
        base_per_usd = usd_rates.get(base, 1.0)
        rates = {currency: usd_rate / base_per_usd for currency, usd_rate in usd_rates.items()}

    _fx_cache[base] = (now, rates)
    return rates


async def convert_amount(
    amount: float,
    from_currency: str,
    to_currency: str,
    rates: dict[str, float] | None = None,
) -> float:
    """Convert amount between supported currencies using USD pivot."""
    if amount == 0:
        return 0.0
    from_currency = normalize_currency(from_currency)
    to_currency = normalize_currency(to_currency)
    if from_currency == to_currency:
        return amount

    fx = rates or await fetch_fx_rates("USD")
    from_rate = fx.get(from_currency, 1.0)
    to_rate = fx.get(to_currency, 1.0)
    usd_amount = amount / from_rate if from_rate else amount
    return usd_amount * to_rate


async def fetch_gold_price_per_gram(currency: str = "USD") -> tuple[float, str]:
    """Return gold spot price per gram in requested currency."""
    import time

    global _gold_cache
    currency = normalize_currency(currency)
    now = time.monotonic()
    if _gold_cache and now - _gold_cache[0] < GOLD_CACHE_TTL:
        usd_per_gram = _gold_cache[1]
    else:
        quote = await fetch_live_quote("GC=F")
        if quote and quote.get("price"):
            usd_per_gram = float(quote["price"]) / TROY_OZ_GRAMS
            _gold_cache = (now, usd_per_gram)
        else:
            usd_per_gram = 75.0
            logger.warning("Gold quote unavailable; using fallback $75/g")

    if currency == "USD":
        return round(usd_per_gram, 2), "Yahoo Finance (GC=F)"

    converted = await convert_amount(usd_per_gram, "USD", currency)
    return round(converted, 2), "Yahoo Finance (GC=F) + Frankfurter FX"


async def fetch_stock_price(symbol: str) -> tuple[float | None, str | None, str]:
    """Return unit price, quote currency, and source label."""
    ticker = symbol.strip().upper()
    quote = await fetch_live_quote(ticker)
    if not quote or quote.get("price") is None:
        return None, None, "unavailable"
    return float(quote["price"]), quote.get("currency") or "USD", "Yahoo Finance"


async def fetch_crypto_price(symbol: str) -> tuple[float | None, str]:
    """Return USD unit price for a crypto symbol."""
    key = symbol.strip().upper()
    ticker = CRYPTO_TICKER_MAP.get(key, f"{key}-USD")
    quote = await fetch_live_quote(ticker)
    if not quote or quote.get("price") is None:
        return None, "unavailable"
    return float(quote["price"]), "Yahoo Finance"


async def resolve_holding_value(
    *,
    asset_type: Literal["stock", "crypto"],
    symbol: str,
    quantity: float,
    output_currency: str,
    rates: dict[str, float],
) -> tuple[float, float | None, str, str | None]:
    """Return value in output currency, unit price, source, and quote currency."""
    if asset_type == "stock":
        unit_price, quote_currency, source = await fetch_stock_price(symbol)
    else:
        unit_price, source = await fetch_crypto_price(symbol)
        quote_currency = "USD"

    if unit_price is None:
        return 0.0, None, source, quote_currency

    raw_value = unit_price * quantity
    value = await convert_amount(raw_value, quote_currency or "USD", output_currency, rates)
    return round(value, 2), unit_price, source, quote_currency
