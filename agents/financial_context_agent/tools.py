"""Financial Context Agent tools — live market data enrichment."""

import asyncio
import logging
import re
import time

from agents.financial_context_agent.market_data import fetch_market_fundamentals, fetch_market_quote
from agents.financial_context_agent.models import FinancialContext, FinancialProduct, MarketQuote

logger = logging.getLogger(__name__)

_quote_cache: dict[str, tuple[float, dict]] = {}
_quote_lock = asyncio.Lock()
QUOTE_CACHE_TTL = 120.0

_fundamentals_cache: dict[str, tuple[float, dict]] = {}
_fundamentals_lock = asyncio.Lock()
FUNDAMENTALS_CACHE_TTL = 300.0

_NON_TICKER_WORDS = frozenset({
    "ETF", "USD", "GBP", "EUR", "BTC", "NFT", "AML", "KYC",
    "AAOIFI", "IFSB", "IBAN", "VAT", "GST", "ATM", "API",
    "PDF", "URL", "RTL", "LTR", "FAQ", "TBD", "TBA", "N/A",
})

ENTITY_CONTEXT: dict[str, FinancialProduct] = {
    "riba": FinancialProduct(
        name="Riba / Interest",
        category="prohibited_concept",
        description="Guaranteed increase on loans or debt obligations.",
    ),
    "crypto": FinancialProduct(
        name="Cryptocurrency",
        category="digital_asset",
        description="Decentralized digital currency subject to scholarly debate on gharar and utility.",
    ),
    "bitcoin": FinancialProduct(
        name="Bitcoin",
        category="digital_asset",
        description="Proof-of-work cryptocurrency; scholarly opinions vary on currency vs commodity.",
    ),
    "stock": FinancialProduct(
        name="Equity / Stock",
        category="equity",
        description="Ownership share in a company; requires Shariah screening for compliance.",
    ),
    "etf": FinancialProduct(
        name="ETF",
        category="fund",
        description="Exchange-traded fund; compliance depends on underlying holdings.",
    ),
    "sukuk": FinancialProduct(
        name="Sukuk",
        category="islamic_finstrument",
        description="Islamic bond-like instrument based on asset-backed structures.",
    ),
    "mortgage": FinancialProduct(
        name="Mortgage / Loan",
        category="debt",
        description="Debt instrument; conventional interest-based mortgages involve riba.",
    ),
}

TICKER_MAP: dict[str, str] = {
    "tesla": "TSLA",
    "apple": "AAPL",
    "microsoft": "MSFT",
    "nvidia": "NVDA",
    "amazon": "AMZN",
    "google": "GOOGL",
    "meta": "META",
}


async def fetch_live_quote(symbol: str) -> dict | None:
    """Fetch real-time quote via yfinance / Alpha Vantage / Yahoo."""
    key = symbol.upper()
    async with _quote_lock:
        now = time.monotonic()
        stale = [k for k, (ts, _) in _quote_cache.items() if now - ts > QUOTE_CACHE_TTL * 2]
        for k in stale:
            del _quote_cache[k]
        cached = _quote_cache.get(key)
        if cached and now - cached[0] < QUOTE_CACHE_TTL:
            return cached[1]

    quote = await fetch_market_quote(key)
    if quote and quote.get("price") is not None:
        async with _quote_lock:
            _quote_cache[key] = (time.monotonic(), quote)
        return quote
    return None


def detect_tickers(entities: list[str], query: str = "") -> list[str]:
    """Map entities and query text to stock tickers."""
    tickers: list[str] = []
    combined = " ".join(entities + [query]).lower()
    for name, ticker_symbol in TICKER_MAP.items():
        if name in combined and ticker_symbol not in tickers:
            tickers.append(ticker_symbol)
    for match in re.findall(r"\b[A-Z]{2,5}\b", query):
        if match not in tickers and match not in _NON_TICKER_WORDS:
            tickers.append(match)
    return tickers[:3]


async def fetch_company_fundamentals(symbol: str) -> dict | None:
    """Fetch company profile and financial metrics from market data providers."""
    key = symbol.upper()
    async with _fundamentals_lock:
        now = time.monotonic()
        stale = [
            k for k, (ts, _) in _fundamentals_cache.items() if now - ts > FUNDAMENTALS_CACHE_TTL * 2
        ]
        for k in stale:
            del _fundamentals_cache[k]
        cached = _fundamentals_cache.get(key)
        if cached and now - cached[0] < FUNDAMENTALS_CACHE_TTL:
            return cached[1]

    payload = await fetch_market_fundamentals(key)
    if payload:
        async with _fundamentals_lock:
            _fundamentals_cache[key] = (time.monotonic(), payload)
        return payload

    logger.warning("All market data providers failed for %s", key)
    return None


async def build_live_context(entities: list[str], query: str = "") -> FinancialContext:
    """Build financial context with live market metrics where available."""
    products = [ENTITY_CONTEXT[e] for e in entities if e in ENTITY_CONTEXT]
    tickers = detect_tickers(entities, query)
    live_notes: list[str] = []
    market_quotes: list[MarketQuote] = []
    screening_notes: list[str] = []
    has_live = False

    for ticker_symbol in tickers:
        quote = await fetch_live_quote(ticker_symbol)
        if quote and quote.get("price"):
            has_live = True
            cap = quote.get("market_cap")
            cap_str = f", market cap {cap:,.0f}" if cap else ""
            live_notes.append(
                f"{ticker_symbol}: {quote['price']} {quote.get('currency', 'USD')}"
                f"{cap_str} ({quote.get('exchange', 'N/A')})"
            )
            market_quotes.append(
                MarketQuote(
                    symbol=ticker_symbol,
                    price=float(quote["price"]) if quote.get("price") is not None else None,
                    currency=quote.get("currency"),
                    market_cap=float(cap) if cap else None,
                    exchange=quote.get("exchange"),
                )
            )
            screening_notes.append(
                f"{ticker_symbol}: Requires AAOIFI screening — debt ratio, non-permissible revenue, "
                "and business activity review before a Shariah ruling."
            )
            products.append(
                FinancialProduct(
                    name=f"{ticker_symbol} Equity",
                    category="equity",
                    description=(
                        f"Live quote: {quote['price']} {quote.get('currency', 'USD')}. "
                        "Requires Shariah screening (debt ratio, revenue mix, AAOIFI)."
                    ),
                )
            )

    notes = (
        "Live market data: " + "; ".join(live_notes)
        if live_notes
        else "Financial context derived from query entities."
    )
    return FinancialContext(
        entities=entities,
        products=products,
        market_quotes=market_quotes,
        notes=notes,
        has_external_data=has_live,
        screening_notes=screening_notes,
    )
