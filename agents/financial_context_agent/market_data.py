"""Market data providers — yfinance, Alpha Vantage, with Yahoo HTTP fallback."""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

YAHOO_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://finance.yahoo.com/",
    "Origin": "https://finance.yahoo.com",
}


def _safe_float(value: object) -> float | None:
    if value is None:
        return None
    try:
        num = float(value)
        if num != num:  # NaN
            return None
        return num
    except (TypeError, ValueError):
        return None


def _merge_payload(base: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in extra.items():
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        if merged.get(key) in (None, "", 0) or key in {
            "company_name",
            "business_summary",
            "sector",
            "industry",
        }:
            merged[key] = value
    return merged


def _fetch_yfinance_sync(symbol: str) -> dict[str, Any] | None:
    try:
        import yfinance as yf
    except ImportError:
        logger.warning("yfinance not installed")
        return None

    key = symbol.upper()
    try:
        ticker = yf.Ticker(key)
        info: dict[str, Any] = {}
        try:
            raw_info = ticker.info
            if isinstance(raw_info, dict):
                info = raw_info
        except Exception as exc:
            logger.debug("yfinance info failed for %s: %s", key, exc)

        price = _safe_float(
            info.get("currentPrice")
            or info.get("regularMarketPrice")
            or info.get("previousClose")
        )
        market_cap = _safe_float(info.get("marketCap"))
        total_debt = _safe_float(info.get("totalDebt"))
        total_cash = _safe_float(info.get("totalCash"))
        revenue = _safe_float(info.get("totalRevenue"))

        if total_debt is None:
            try:
                balance = ticker.balance_sheet
                if balance is not None and not balance.empty:
                    row = balance.iloc[:, 0]
                    total_debt = _safe_float(
                        row.get("Total Debt")
                        or row.get("Long Term Debt")
                        or row.get("Net Debt")
                    )
            except Exception:
                pass

        change_percent = _safe_float(info.get("regularMarketChangePercent"))
        if change_percent is not None and abs(change_percent) <= 1:
            change_percent *= 100

        previous_close = _safe_float(info.get("previousClose") or info.get("regularMarketPreviousClose"))

        return {
            "symbol": key,
            "company_name": info.get("shortName") or info.get("longName") or key,
            "price": price,
            "previous_close": previous_close,
            "currency": info.get("currency") or "USD",
            "market_cap": market_cap,
            "change_percent": change_percent,
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "country": info.get("country"),
            "business_summary": (info.get("longBusinessSummary") or "")[:2000],
            "logo_url": info.get("logo_url"),
            "total_debt": total_debt,
            "total_cash": total_cash,
            "current_ratio": _safe_float(info.get("currentRatio")),
            "debt_to_equity": _safe_float(info.get("debtToEquity")),
            "gross_margin": _safe_float(info.get("grossMargins")),
            "net_margin": _safe_float(info.get("profitMargins")),
            "roe": _safe_float(info.get("returnOnEquity")),
            "pe_ratio": _safe_float(info.get("trailingPE") or info.get("forwardPE")),
            "pb_ratio": _safe_float(info.get("priceToBook")),
            "peg_ratio": _safe_float(info.get("pegRatio")),
            "revenue": revenue,
            "exchange": info.get("exchange"),
            "data_source": "yfinance",
        }
    except Exception as exc:
        logger.warning("yfinance fetch failed for %s: %s", key, exc)
        return None


async def _fetch_alpha_vantage(symbol: str, api_key: str) -> dict[str, Any] | None:
    key = symbol.upper()
    base_url = "https://www.alphavantage.co/query"
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            overview_resp = await client.get(
                base_url,
                params={"function": "OVERVIEW", "symbol": key, "apikey": api_key},
            )
            overview_resp.raise_for_status()
            overview = overview_resp.json()

            quote_resp = await client.get(
                base_url,
                params={"function": "GLOBAL_QUOTE", "symbol": key, "apikey": api_key},
            )
            quote_resp.raise_for_status()
            quote_row = quote_resp.json().get("Global Quote") or {}

        if not overview or overview.get("Symbol") is None:
            if not quote_row:
                return None

        price = _safe_float(quote_row.get("05. price"))
        change_pct = _safe_float(
            (quote_row.get("10. change percent") or "").replace("%", "").strip()
        )

        return {
            "symbol": key,
            "company_name": overview.get("Name") or key,
            "price": price,
            "currency": "USD",
            "market_cap": _safe_float(overview.get("MarketCapitalization")),
            "change_percent": change_pct,
            "sector": overview.get("Sector"),
            "industry": overview.get("Industry"),
            "business_summary": (overview.get("Description") or "")[:2000],
            "logo_url": None,
            "total_debt": None,
            "total_cash": None,
            "current_ratio": _safe_float(overview.get("CurrentRatio")),
            "debt_to_equity": _safe_float(overview.get("DebtToEquity")),
            "gross_margin": _safe_float(overview.get("ProfitMargin")),
            "net_margin": _safe_float(overview.get("ProfitMargin")),
            "roe": _safe_float(overview.get("ReturnOnEquityTTM")),
            "pe_ratio": _safe_float(overview.get("PERatio")),
            "pb_ratio": _safe_float(overview.get("PriceToBookRatio")),
            "peg_ratio": _safe_float(overview.get("PEGRatio")),
            "revenue": None,
            "exchange": overview.get("Exchange"),
            "data_source": "alpha_vantage",
        }
    except (httpx.HTTPError, ValueError, TypeError) as exc:
        logger.warning("Alpha Vantage fetch failed for %s: %s", key, exc)
        return None


async def _yahoo_chart_quote(symbol: str) -> dict[str, Any] | None:
    key = symbol.upper()
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{key}"
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            response = await client.get(url, headers=YAHOO_HEADERS)
            response.raise_for_status()
            data = response.json()
        result = data.get("chart", {}).get("result", [])
        if not result:
            return None
        meta = result[0].get("meta", {})
        return {
            "symbol": key,
            "price": _safe_float(meta.get("regularMarketPrice")),
            "currency": meta.get("currency") or "USD",
            "market_cap": _safe_float(meta.get("marketCap")),
            "exchange": meta.get("exchangeName"),
            "change_percent": _safe_float(meta.get("regularMarketChangePercent")),
            "data_source": "yahoo_chart",
        }
    except (httpx.HTTPError, KeyError, TypeError) as exc:
        logger.debug("Yahoo chart quote failed for %s: %s", key, exc)
        return None


async def fetch_market_quote(symbol: str) -> dict[str, Any] | None:
    """Fetch a live quote using the best available provider."""
    key = symbol.upper()

    yf_data = await asyncio.to_thread(_fetch_yfinance_sync, key)
    if yf_data and yf_data.get("price") is not None:
        return yf_data

    api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    if api_key:
        av_data = await _fetch_alpha_vantage(key, api_key)
        if av_data and av_data.get("price") is not None:
            return av_data

    chart = await _yahoo_chart_quote(key)
    return chart


async def fetch_market_fundamentals(symbol: str) -> dict[str, Any] | None:
    """Fetch company fundamentals; merges yfinance, Alpha Vantage, and Yahoo."""
    key = symbol.upper()
    payload: dict[str, Any] = {"symbol": key, "company_name": key}

    yf_data = await asyncio.to_thread(_fetch_yfinance_sync, key)
    if yf_data:
        payload = _merge_payload(payload, yf_data)

    api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    if api_key:
        av_data = await _fetch_alpha_vantage(key, api_key)
        if av_data:
            payload = _merge_payload(payload, av_data)

    if payload.get("price") is None:
        chart = await _yahoo_chart_quote(key)
        if chart:
            payload = _merge_payload(payload, chart)

    if payload.get("price") is not None or payload.get("market_cap") is not None:
        payload.setdefault("data_source", payload.get("data_source", "merged"))
        return payload

    return None
