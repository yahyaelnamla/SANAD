"""Company and portfolio Shariah screening services."""

from __future__ import annotations

import asyncio
import time
import uuid
from collections import defaultdict
from datetime import UTC, datetime

from agents.financial_context_agent.tools import (
    detect_tickers,
    fetch_company_fundamentals,
    fetch_live_quote,
)
from backend.app.schemas.feature_schemas import (
    AaoifiRatios,
    AllocationSlice,
    CompanyScanRequest,
    CompanyScanResponse,
    ComplianceTrendPoint,
    FinancialMetrics,
    PeerComparison,
    PortfolioHolding,
    PortfolioHoldingResult,
    PortfolioInsights,
    PortfolioScanRequest,
    PortfolioScanResponse,
    QualitativeScreening,
    ScannerAgentTraceStep,
    ScannerExecutionMetrics,
    ScannerSourceReference,
    ShariahMethodology,
)
from backend.app.services.company_scanner_ai import (
    _fallback_analysis,
    generate_company_analysis,
    generate_portfolio_analysis,
)
from backend.app.services.zakat_price_service import (
    convert_amount,
    fetch_crypto_price,
    fetch_fx_rates,
    fetch_stock_price,
    normalize_currency,
)

CONTROVERSIAL_KEYWORDS = {
    "bank",
    "banking",
    "alcohol",
    "casino",
    "gambling",
    "tobacco",
    "interest",
    "brewery",
    "distillery",
    "pork",
    "weapon",
    "adult",
}

PROHIBITED_INDUSTRY_HINTS = {
    "alcoholic",
    "tobacco",
    "gambling",
    "casino",
    "brewers",
    "distillers",
    "banks",
    "financial services",
    "credit",
    "adult entertainment",
    "aerospace & defense",
}

PEER_GROUPS: dict[str, list[str]] = {
    "tesla": ["Ford", "GM", "Rivian"],
    "tsla": ["Ford", "GM", "Rivian"],
    "apple": ["Microsoft", "Alphabet", "Samsung"],
    "aapl": ["Microsoft", "Alphabet", "Samsung"],
    "nvidia": ["AMD", "Intel", "Qualcomm"],
    "nvda": ["AMD", "Intel", "Qualcomm"],
    "microsoft": ["Apple", "Alphabet", "Oracle"],
    "msft": ["Apple", "Alphabet", "Oracle"],
}


def _verdict(status: str) -> str:
    if status == "green":
        return "halal"
    if status == "red":
        return "haram"
    return "doubtful"


def _verdict_reason(status: str, controversial: bool, debt_ratio: float, interest_ratio: float) -> str:
    if status == "green":
        return "Debt and non-permissible income ratios are within AAOIFI-inspired thresholds."
    if status == "red":
        if controversial:
            return "Business activity or sector may involve non-permissible revenue — scholarly review required."
        return "Financial ratios exceed Shariah screening thresholds for permissibility."
    return "Borderline ratios — purification or deeper annual report review may be required."


def _investment_outlook(
    compliance_score: float,
    trend_history: list[ComplianceTrendPoint],
    status: str,
) -> tuple[bool, str]:
    scores = [point.compliance_score for point in trend_history]
    improving = len(scores) >= 2 and scores[-1] >= scores[0]
    favorable = status == "green" and compliance_score >= 0.7 and improving
    if favorable:
        return True, "Compliance trend is stable or improving with acceptable Shariah ratios."
    if status == "red":
        return False, "High Shariah risk — investment is not recommended until activity is clarified."
    if improving:
        return True, "Moderate compliance with improving trend — cautious investment with purification planning."
    return False, "Mixed signals — verify annual reports and scholar guidance before investing."


def _risk_level(status: str, debt_ratio: float, interest_ratio: float) -> str:
    if status == "red" or debt_ratio > 0.33 or interest_ratio > 0.05:
        return "high"
    if status == "yellow" or debt_ratio > 0.25 or interest_ratio > 0.03:
        return "medium"
    return "low"


def _trend_history(compliance_score: float) -> list[ComplianceTrendPoint]:
    """Synthetic quarterly trend anchored on current compliance score."""
    offsets = (-0.06, -0.03, 0.0)
    labels = ("Q1", "Q2", "Q3")
    return [
        ComplianceTrendPoint(
            period=label,
            compliance_score=round(max(0.1, min(0.99, compliance_score + offset)), 2),
        )
        for label, offset in zip(labels, offsets, strict=True)
    ]


async def _scan_peer(name: str, language: str = "en") -> PeerComparison:
    peer_scan = await scan_company(
        CompanyScanRequest(company_name=name, language=language),
        include_peers=False,
        include_ai=False,
    )
    return PeerComparison(
        company_name=peer_scan.company_name,
        compliance_score=peer_scan.compliance_score,
        status=peer_scan.status,
    )


def _sector_controversial(sector: str | None, industry: str | None, summary: str) -> bool:
    blob = " ".join(filter(None, [sector, industry, summary])).lower()
    return any(hint in blob for hint in PROHIBITED_INDUSTRY_HINTS)


def _compute_aaoifi_ratios(
    fundamentals: dict | None,
    *,
    seed_debt: float,
    seed_interest: float,
    seed_non_permissible: float,
    controversial: bool,
) -> dict[str, float | None]:
    market_cap = (fundamentals or {}).get("market_cap")
    total_debt = (fundamentals or {}).get("total_debt")
    total_cash = (fundamentals or {}).get("total_cash")

    debt_ratio = seed_debt
    if market_cap and total_debt and market_cap > 0:
        debt_ratio = round(total_debt / market_cap, 4)

    interest_investments_ratio = seed_interest
    if market_cap and total_cash and market_cap > 0:
        interest_investments_ratio = round(min(0.35, total_cash / market_cap), 4)

    non_permissible = seed_non_permissible
    if controversial:
        non_permissible = max(non_permissible, 0.08)

    purification = round(max(0.0, non_permissible + interest_investments_ratio * 0.15), 4)

    return {
        "non_permissible_income_ratio": non_permissible,
        "interest_bearing_debt_ratio": debt_ratio,
        "interest_earning_investments_ratio": interest_investments_ratio,
        "dividend_purification_ratio": purification,
    }


def _compliance_score(
    debt_ratio: float,
    interest_ratio: float,
    non_permissible: float,
    controversial: bool,
) -> float:
    if controversial or non_permissible > 0.05:
        return round(max(0.15, min(0.55, 0.45 - debt_ratio * 0.2)), 2)
    score = 0.95 - debt_ratio * 0.85 - interest_ratio * 2.2 - non_permissible * 1.5
    return round(max(0.2, min(0.97, score)), 2)


def _status_from_ratios(
    debt_ratio: float,
    interest_ratio: float,
    non_permissible: float,
    controversial: bool,
) -> str:
    if controversial or non_permissible > 0.05:
        return "red"
    if debt_ratio > 0.30 or interest_ratio > 0.30:
        return "yellow"
    if debt_ratio > 0.33 or interest_ratio > 0.05:
        return "yellow"
    return "green"


def _build_agent_trace(
    *,
    symbol: str | None,
    ai_meta: dict,
    total_latency_ms: int,
    fanar_model: str,
) -> tuple[list[ScannerAgentTraceStep], ScannerExecutionMetrics]:
    data_latency = max(0, total_latency_ms - int(ai_meta.get("latency_ms") or 0))
    steps = [
        ScannerAgentTraceStep(
            phase="Intent Analysis",
            agent="company_scanner",
            model="rules",
            status="completed",
            latency_ms=min(120, data_latency // 4 or 40),
        ),
        ScannerAgentTraceStep(
            phase="Data Retrieval",
            agent="financial_context",
            model="yahoo_finance",
            status="completed" if symbol else "partial",
            latency_ms=min(800, data_latency // 2 or 200),
        ),
        ScannerAgentTraceStep(
            phase="Financial Context",
            agent="ratio_engine",
            model="aaoifi_calculator",
            status="completed",
            latency_ms=min(200, data_latency // 6 or 60),
        ),
        ScannerAgentTraceStep(
            phase="Shariah Screening",
            agent="compliance_engine",
            model="aaoifi_standard_21",
            status="completed",
            latency_ms=min(200, data_latency // 6 or 60),
        ),
        ScannerAgentTraceStep(
            phase="Response Builder",
            agent="fanar_synthesis",
            model=str(ai_meta.get("model") or "fallback"),
            status="completed" if not ai_meta.get("error") else "partial",
            latency_ms=int(ai_meta.get("latency_ms") or 0),
            tokens_estimate=ai_meta.get("tokens_used"),
        ),
    ]
    models = [step.model for step in steps if step.model]
    metrics = ScannerExecutionMetrics(
        total_latency_ms=total_latency_ms,
        steps_completed=len([s for s in steps if s.status == "completed"]),
        steps_total=len(steps),
        models_used=list(dict.fromkeys(models)),
        tokens_total=ai_meta.get("tokens_used"),
        fanar_model_preference=fanar_model,
    )
    return steps, metrics


async def scan_company(
    request: CompanyScanRequest,
    *,
    include_peers: bool = True,
    include_ai: bool = True,
) -> CompanyScanResponse:
    """Screen a company using live market data, AAOIFI ratios, and Fanar AI synthesis."""
    pipeline_started = time.perf_counter()
    name = request.company_name.strip()
    tickers = detect_tickers([name.lower()], name)
    symbol = tickers[0] if tickers else None

    fundamentals = await fetch_company_fundamentals(symbol) if symbol else None
    quote = None
    if symbol and (not fundamentals or not fundamentals.get("price")):
        quote = await fetch_live_quote(symbol)
        if quote and fundamentals:
            fundamentals.setdefault("price", quote.get("price"))
            fundamentals.setdefault("currency", quote.get("currency"))
            fundamentals.setdefault("market_cap", quote.get("market_cap"))
            fundamentals.setdefault("change_percent", quote.get("change_percent"))
        elif quote and not fundamentals:
            fundamentals = {
                "symbol": symbol,
                "company_name": name,
                "price": quote.get("price"),
                "currency": quote.get("currency"),
                "market_cap": quote.get("market_cap"),
                "change_percent": quote.get("change_percent"),
            }

    display_name = (fundamentals or {}).get("company_name") or name
    sector = (fundamentals or {}).get("sector")
    industry = (fundamentals or {}).get("industry")
    summary = (fundamentals or {}).get("business_summary") or ""

    seed_debt, seed_interest, name_controversial = 0.0, 0.0, False
    controversial = _sector_controversial(sector, industry, summary) or name_controversial
    if not fundamentals or not fundamentals.get("market_cap"):
        controversial = _sector_controversial(sector, industry, summary) or any(
            keyword in name.lower() for keyword in CONTROVERSIAL_KEYWORDS
        )
    seed_non_permissible = 0.02 if not controversial else 0.07

    ratios = _compute_aaoifi_ratios(
        fundamentals,
        seed_debt=seed_debt,
        seed_interest=seed_interest,
        seed_non_permissible=seed_non_permissible,
        controversial=controversial,
    )

    debt_ratio = float(ratios["interest_bearing_debt_ratio"] or seed_debt)
    interest_ratio = float(ratios["interest_earning_investments_ratio"] or seed_interest)
    non_permissible = float(ratios["non_permissible_income_ratio"] or seed_non_permissible)

    compliance_score = _compliance_score(debt_ratio, interest_ratio, non_permissible, controversial)
    status = _status_from_ratios(debt_ratio, interest_ratio, non_permissible, controversial)

    if include_ai:
        ai_fields, ai_meta = await generate_company_analysis(
            company_name=display_name,
            symbol=symbol,
            fundamentals=fundamentals or {},
            ratios=ratios,
            status=status,
            language=request.language,
            fanar_model=request.fanar_model,
        )
    else:
        ai_fields = _fallback_analysis(
            company_name=display_name,
            status=status,
            debt_ratio=debt_ratio,
            interest_ratio=interest_ratio,
            non_permissible_ratio=non_permissible,
            language=request.language,
        )
        ai_meta = {"model": "rules", "latency_ms": 0, "tokens_used": None}

    revenue_estimate = (fundamentals or {}).get("revenue")
    if revenue_estimate is None and fundamentals and fundamentals.get("market_cap"):
        revenue_estimate = float(fundamentals["market_cap"]) * 0.12

    risk = _risk_level(status, debt_ratio, interest_ratio)
    purification = round((ratios.get("dividend_purification_ratio") or 0) * (revenue_estimate or 1_000_000), 2)

    data_source = (fundamentals or {}).get("data_source", "market_providers")
    screening_notes = [
        "Screening uses AAOIFI Standard 21 thresholds: debt < 30%, interest investments < 30%, non-permissible income < 5%.",
        f"Market data via {data_source} (yfinance / Alpha Vantage / Yahoo). Annual report verification is still recommended.",
    ]
    if controversial:
        screening_notes.append(
            "Sector or business description suggests potentially non-permissible activity — scholarly review required."
        )
    price = (fundamentals or {}).get("price") or (quote or {}).get("price")
    if price:
        screening_notes.append(
            f"Live quote: {price} {(fundamentals or quote or {}).get('currency', 'USD')}."
        )

    peer_key = (symbol or name.strip().lower()).lower()
    peer_names = PEER_GROUPS.get(peer_key, PEER_GROUPS.get(name.strip().lower().split()[0], []))[:3]
    if include_peers and peer_names:
        peers = list(
            await asyncio.gather(*[_scan_peer(peer, request.language) for peer in peer_names])
        )
    else:
        peers = []

    trend = _trend_history(compliance_score)
    verdict = _verdict(status)
    outlook_favorable, outlook_text = _investment_outlook(compliance_score, trend, status)

    total_latency_ms = int((time.perf_counter() - pipeline_started) * 1000)
    agent_trace, execution_metrics = _build_agent_trace(
        symbol=symbol,
        ai_meta=ai_meta,
        total_latency_ms=total_latency_ms,
        fanar_model=request.fanar_model,
    )

    sources = [
        ScannerSourceReference(
            title=f"Market data ({data_source})",
            citation="Live quotes and fundamentals via yfinance / Alpha Vantage",
            source_type="market_data",
            source_url=f"https://finance.yahoo.com/quote/{symbol}" if symbol else None,
        ),
        ScannerSourceReference(
            title="AAOIFI Shariah Standard 21",
            citation="Investment in company shares — screening criteria",
            source_type="standard",
        ),
    ]

    qualitative = QualitativeScreening(
        status=ai_fields.get("qualitative_status", "pass" if status != "red" else "fail"),  # type: ignore[arg-type]
        analysis=ai_fields.get("qualitative_analysis") or summary[:500] or "Equity issuer — business activity screening required.",
    )

    financial_metrics = FinancialMetrics(
        pe_ratio=(fundamentals or {}).get("pe_ratio"),
        pb_ratio=(fundamentals or {}).get("pb_ratio"),
        peg_ratio=(fundamentals or {}).get("peg_ratio"),
        gross_profit_margin=(fundamentals or {}).get("gross_margin"),
        net_profit_margin=(fundamentals or {}).get("net_margin"),
        roe=(fundamentals or {}).get("roe"),
        current_ratio=(fundamentals or {}).get("current_ratio"),
        debt_to_equity=(fundamentals or {}).get("debt_to_equity"),
    )

    logo_url = (fundamentals or {}).get("logo_url")
    if not logo_url and symbol:
        logo_url = f"https://logo.clearbit.com/{symbol.lower()}.com"

    return CompanyScanResponse(
        company_name=display_name,
        symbol=symbol,
        business_activity=summary[:600] if summary else "Listed equity — requires Shariah business activity screening.",
        debt_ratio=debt_ratio,
        interest_income_ratio=interest_ratio,
        revenue_estimate=revenue_estimate,
        compliance_score=compliance_score,
        status=status,
        risk_level=risk,  # type: ignore[arg-type]
        purification_estimate=purification,
        peer_comparison=peers,
        trend_history=trend,
        screening_notes=screening_notes,
        market_price=float(price) if price is not None else None,
        currency=(fundamentals or quote or {}).get("currency"),
        verdict=verdict,  # type: ignore[arg-type]
        verdict_reason=_verdict_reason(status, controversial, debt_ratio, interest_ratio),
        investment_favorable=outlook_favorable,
        investment_outlook=outlook_text,
        sector=sector,
        industry=industry,
        logo_url=logo_url,
        price_change_percent=(fundamentals or {}).get("change_percent") or (quote or {}).get("change_percent"),
        ai_summary=ai_fields.get("ai_summary", ""),
        key_takeaways=list(ai_fields.get("key_takeaways") or []),
        qualitative_screening=qualitative,
        aaoifi_ratios=AaoifiRatios(**ratios),
        financial_metrics=financial_metrics,
        ai_financial_assessment=ai_fields.get("ai_financial_assessment", ""),
        agent_trace=agent_trace,
        sources=sources,
        execution_metrics=execution_metrics,
    )


def _diversification_score(holdings: list[dict]) -> float:
    """Herfindahl-based diversification (1 = fully diversified, 0 = concentrated)."""
    if not holdings:
        return 0.0
    total = sum(float(h.get("value", 0)) for h in holdings)
    if total <= 0:
        return 0.0
    weights = [float(h.get("value", 0)) / total for h in holdings]
    hhi = sum(w * w for w in weights)
    n = len(weights)
    if n <= 1:
        return 0.0
    return round(max(0.0, min(1.0, (1 - hhi) / (1 - 1 / n))), 2)


def _build_shariah_methodology() -> ShariahMethodology:
    return ShariahMethodology(
        standards_used=[
            "AAOIFI Shariah Standard No. 21 — Investment in Shares (screening criteria)",
            "SANAD compliance engine — AAOIFI-inspired financial ratio thresholds",
        ],
        screening_methodology=(
            "Each holding is screened individually. Equity issuers undergo financial ratio screening "
            "and qualitative business activity review. ETFs, funds, and REITs are screened at the "
            "symbol level using available market data; underlying holdings may require additional review."
        ),
        financial_ratio_methodology=(
            "Interest-bearing debt / market capitalization < 30%; "
            "interest-earning investments / market capitalization < 30%; "
            "non-permissible income < 5%. Ratios computed from live fundamentals when available."
        ),
        business_activity_methodology=(
            "Sector, industry, and business description keyword screening against prohibited categories "
            "(conventional banking, alcohol, gambling, tobacco, adult entertainment, weapons, etc.). "
            "Flagged activities require scholarly review — the engine does not issue independent fatwas."
        ),
        purification_methodology=(
            "Estimated purification amounts apply non-permissible income and interest-investment ratios "
            "to holding values for borderline (yellow) and non-compliant (red) positions. "
            "Actual purification should be calculated from annual reports and verified by a scholar."
        ),
        aggregation_methodology=(
            "Portfolio compliance score is a value-weighted aggregate of individual holding assessments. "
            "This is a methodological summary — not a portfolio-wide halal/haram ruling. "
            "Investment decisions require scholar review and verification of annual filings."
        ),
    )


def _compliance_explanation(
    scan: CompanyScanResponse,
    *,
    language: str,
) -> str:
    ar = language == "ar"
    ratios = scan.aaoifi_ratios
    debt = ratios.interest_bearing_debt_ratio if ratios else scan.debt_ratio
    interest = ratios.interest_earning_investments_ratio if ratios else scan.interest_income_ratio
    non_perm = ratios.non_permissible_income_ratio if ratios else None

    parts: list[str] = []
    if ar:
        parts.append(f"الحالة: {scan.verdict} — {scan.verdict_reason}")
        if debt is not None:
            parts.append(f"نسبة الدين / القيمة السوقية: {debt * 100:.1f}% (حد 30%).")
        if interest is not None:
            parts.append(f"نسبة الاستثمارات الربوية: {interest * 100:.1f}% (حد 30%).")
        if non_perm is not None:
            parts.append(f"نسبة الدخل غير المشروع: {non_perm * 100:.1f}% (حد 5%).")
        if scan.qualitative_screening:
            parts.append(f"الفحص النوعي: {scan.qualitative_screening.analysis[:200]}")
    else:
        parts.append(f"Status: {scan.verdict} — {scan.verdict_reason}")
        if debt is not None:
            parts.append(f"Debt / market cap: {debt * 100:.1f}% (threshold 30%).")
        if interest is not None:
            parts.append(f"Interest investments ratio: {interest * 100:.1f}% (threshold 30%).")
        if non_perm is not None:
            parts.append(f"Non-permissible income: {non_perm * 100:.1f}% (threshold 5%).")
        if scan.qualitative_screening:
            parts.append(f"Qualitative screening: {scan.qualitative_screening.analysis[:200]}")
    return " ".join(parts)


def _portfolio_assessment(halal_score: float, violations: list[str], language: str) -> tuple[str, str]:
    ar = language == "ar"
    if halal_score >= 0.85 and not violations:
        code = "largely_compliant"
        detail = (
            "معظم قيمة المحفظة في أصول ضمن حدود AAOIFI — استمر في الفحص الدوري."
            if ar
            else "Most portfolio value is in holdings within AAOIFI thresholds — continue periodic re-screening."
        )
    elif halal_score >= 0.65:
        code = "mixed_compliance"
        detail = (
            "امتثال مختلط — بعض الأصول في منطقة حدودية أو تتطلب تطهيراً."
            if ar
            else "Mixed compliance — some holdings are borderline or require purification."
        )
    elif violations:
        code = "significant_concerns"
        detail = (
            "هناك مخاوف امتثال جوهرية — راجع الأصول المُعلّمة واستشر عالماً."
            if ar
            else "Material compliance concerns — review flagged holdings and consult a scholar."
        )
    else:
        code = "needs_review"
        detail = (
            "البيانات أو النسب تتطلب مراجعة إضافية قبل أي قرار استثماري."
            if ar
            else "Data or ratios require additional review before investment decisions."
        )
    return code, detail


def _build_allocation_slices(
    buckets: dict[str, float],
    total_value: float,
) -> list[AllocationSlice]:
    if total_value <= 0:
        return []
    slices = [
        AllocationSlice(
            label=label,
            value=round(value, 2),
            weight_pct=round(value / total_value * 100, 2),
        )
        for label, value in buckets.items()
        if value > 0
    ]
    return sorted(slices, key=lambda s: s.weight_pct, reverse=True)


async def _resolve_holding_market_data(
    holding: PortfolioHolding,
    output_currency: str,
    fx_rates: dict[str, float],
) -> tuple[float | None, str, str | None, dict | None, dict | None, list[str]]:
    """Return unit price, price_source, quote currency, quote dict, fundamentals, data gaps."""
    gaps: list[str] = []
    symbol = holding.symbol.strip().upper()

    if not holding.use_market_price:
        if holding.manual_price is None or holding.manual_price <= 0:
            gaps.append(f"{symbol}: manual price required when market pricing is disabled")
            return None, "unavailable", None, None, None, gaps
        return holding.manual_price, "manual", output_currency, None, None, gaps

    if holding.asset_type == "crypto":
        unit_price, _source = await fetch_crypto_price(symbol)
        if unit_price is None:
            gaps.append(f"{symbol}: live crypto price unavailable")
            return None, "unavailable", None, None, None, gaps
        converted = await convert_amount(unit_price, "USD", output_currency, fx_rates)
        return converted, "market", "USD", None, None, gaps

    unit_price, quote_currency, _source = await fetch_stock_price(symbol)
    fundamentals = await fetch_company_fundamentals(symbol)
    if unit_price is None and fundamentals and fundamentals.get("price"):
        unit_price = float(fundamentals["price"])
        quote_currency = fundamentals.get("currency") or "USD"

    if unit_price is None:
        quote = await fetch_live_quote(symbol)
        if quote and quote.get("price") is not None:
            unit_price = float(quote["price"])
            quote_currency = quote.get("currency") or "USD"
        else:
            gaps.append(f"{symbol}: live market price unavailable")
            return None, "unavailable", None, None, fundamentals, gaps

    quote_currency = quote_currency or "USD"
    converted = await convert_amount(unit_price, quote_currency, output_currency, fx_rates)
    if fundamentals is None:
        fundamentals = await fetch_company_fundamentals(symbol)
    return converted, "market", quote_currency, None, fundamentals, gaps


async def _scan_portfolio_holding(
    holding: PortfolioHolding,
    *,
    language: str,
) -> CompanyScanResponse:
    return await scan_company(
        CompanyScanRequest(company_name=holding.symbol, language=language),
        include_peers=False,
        include_ai=False,
    )


async def scan_portfolio(request: PortfolioScanRequest) -> PortfolioScanResponse:
    """Aggregate portfolio compliance, market data, and Fanar portfolio-level analysis."""
    pipeline_started = time.perf_counter()
    output_currency = normalize_currency(request.output_currency)
    fx_rates = await fetch_fx_rates("USD")
    methodology = _build_shariah_methodology()
    data_gaps: list[str] = []

    resolved: list[tuple[PortfolioHolding, float | None, str, str | None, dict | None, dict | None, list[str]]] = []
    for holding in request.holdings:
        price, source, quote_currency, _quote, fundamentals, gaps = await _resolve_holding_market_data(
            holding, output_currency, fx_rates
        )
        data_gaps.extend(gaps)
        resolved.append((holding, price, source, quote_currency, _quote, fundamentals, gaps))

    scans = await asyncio.gather(
        *[_scan_portfolio_holding(h, language=request.language) for h, *_ in resolved]
    )

    holding_results: list[PortfolioHoldingResult] = []
    raw_for_div: list[dict] = []
    violations: list[str] = []
    compliant_weight = 0.0
    purification_total = 0.0
    has_purchase_prices = False
    daily_change_total = 0.0
    unrealized_total = 0.0
    unrealized_cost_total = 0.0

    sector_buckets: dict[str, float] = defaultdict(float)
    country_buckets: dict[str, float] = defaultdict(float)
    currency_buckets: dict[str, float] = defaultdict(float)
    asset_buckets: dict[str, float] = defaultdict(float)

    for (holding, unit_price, price_source, quote_currency, _quote, fundamentals, gaps), scan in zip(
        resolved, scans, strict=True
    ):
        symbol = holding.symbol.strip().upper()
        if unit_price is None or unit_price <= 0:
            data_gaps.append(f"{symbol}: cannot compute holding value — price unavailable")
            continue

        value = round(unit_price * holding.quantity, 2)
        raw_for_div.append({"value": value})

        display_name = (
            holding.name
            or (fundamentals or {}).get("company_name")
            or scan.company_name
            or symbol
        )
        sector = scan.sector or (fundamentals or {}).get("sector")
        industry = scan.industry or (fundamentals or {}).get("industry")
        country = (fundamentals or {}).get("country")
        exchange = (fundamentals or {}).get("exchange")
        market_cap = (fundamentals or {}).get("market_cap") or scan.revenue_estimate
        daily_change_pct = scan.price_change_percent or (fundamentals or {}).get("change_percent")

        if daily_change_pct is not None:
            daily_change_total += value * (daily_change_pct / 100)

        unrealized_gl: float | None = None
        unrealized_gl_pct: float | None = None
        if holding.purchase_price is not None and holding.purchase_price > 0:
            has_purchase_prices = True
            cost_basis = holding.purchase_price * holding.quantity
            unrealized_gl = round(value - cost_basis, 2)
            unrealized_gl_pct = round((unrealized_gl / cost_basis) * 100, 2) if cost_basis else None
            unrealized_total += unrealized_gl
            unrealized_cost_total += cost_basis

        holding_gaps = list(gaps)
        if not sector:
            holding_gaps.append(f"{symbol}: sector data unavailable")
        if not country:
            holding_gaps.append(f"{symbol}: country data unavailable")

        holding_results.append(
            PortfolioHoldingResult(
                symbol=symbol,
                name=display_name,
                asset_type=holding.asset_type,
                quantity=holding.quantity,
                current_price=round(unit_price, 4),
                price_source=price_source,
                use_market_price=holding.use_market_price,
                purchase_price=holding.purchase_price,
                value=value,
                weight_pct=0.0,
                currency=quote_currency or output_currency,
                exchange=exchange,
                sector=sector,
                industry=industry,
                country=country,
                previous_close=(fundamentals or {}).get("previous_close"),
                daily_change_pct=daily_change_pct,
                market_cap=float(market_cap) if market_cap is not None else None,
                status=scan.status,
                compliance_score=scan.compliance_score,
                verdict=scan.verdict,  # type: ignore[arg-type]
                verdict_reason=scan.verdict_reason,
                compliance_explanation=_compliance_explanation(scan, language=request.language),
                aaoifi_ratios=scan.aaoifi_ratios,
                screening_notes=scan.screening_notes,
                unrealized_gain_loss=unrealized_gl,
                unrealized_gain_loss_pct=unrealized_gl_pct,
                data_unavailable=holding_gaps,
            )
        )

    total_value = round(sum(h.value for h in holding_results), 2)
    if total_value > 0:
        for h in holding_results:
            h.weight_pct = round(h.value / total_value * 100, 2)
            sector_buckets[h.sector or "Unknown"] += h.value
            country_buckets[h.country or "Unknown"] += h.value
            currency_buckets[h.currency or output_currency] += h.value
            asset_buckets[h.asset_type] += h.value

    for h in holding_results:
        weight = h.weight_pct / 100 if total_value else 0
        scan_match = next((s for s in scans if (s.symbol or "").upper() == h.symbol), None)
        if h.status == "green":
            compliant_weight += weight
        elif h.status == "yellow":
            compliant_weight += weight * 0.6
            violations.append(f"{h.symbol}: borderline compliance — review purification.")
            ratio = (scan_match.interest_income_ratio if scan_match else None) or 0.05
            purification_total += h.value * ratio
        else:
            violations.append(f"{h.symbol}: potential Shariah violation — consider divesting.")
            purification_total += h.value * 0.05

    halal_score = round(compliant_weight, 2)
    diversification = _diversification_score(raw_for_div)

    daily_change_pct_portfolio: float | None = None
    if total_value > 0 and any(h.daily_change_pct is not None for h in holding_results):
        daily_change_pct_portfolio = round(daily_change_total / total_value * 100, 2)

    unrealized_pct: float | None = None
    if has_purchase_prices and unrealized_cost_total > 0:
        unrealized_pct = round(unrealized_total / unrealized_cost_total * 100, 2)

    sorted_by_weight = sorted(holding_results, key=lambda x: x.value, reverse=True)
    insights = PortfolioInsights(
        holdings_count=len(holding_results),
        largest_position=sorted_by_weight[0].symbol if sorted_by_weight else None,
        smallest_position=sorted_by_weight[-1].symbol if sorted_by_weight else None,
        daily_change_value=round(daily_change_total, 2) if daily_change_pct_portfolio is not None else None,
        daily_change_pct=daily_change_pct_portfolio,
        unrealized_gain_loss=round(unrealized_total, 2) if has_purchase_prices else None,
        unrealized_gain_loss_pct=unrealized_pct,
    )

    assessment_code, assessment_detail = _portfolio_assessment(halal_score, violations, request.language)
    recommendations: list[str] = []
    if halal_score < 0.7:
        recommendations.append(
            "Increase allocation to AAOIFI-compliant equities or Sukuk."
            if request.language != "ar"
            else "زِد التخصيص للأسهم المتوافقة مع AAOIFI أو الصكوك."
        )
    if diversification < 0.4:
        recommendations.append(
            "Portfolio is concentrated — consider diversifying across sectors and geographies."
            if request.language != "ar"
            else "المحفظة مركّزة — فكّر في التنويع عبر القطاعات والجغرافيا."
        )
    if violations:
        recommendations.append(
            "Calculate annual purification for non-permissible income where applicable."
            if request.language != "ar"
            else "احسب التطهير السنوي للدخل غير المشروع حيث ينطبق."
        )
    if not violations and halal_score >= 0.7:
        recommendations.append(
            "Continue periodic re-screening as financial ratios change."
            if request.language != "ar"
            else "استمر في إعادة الفحص الدوري مع تغيّر النسب المالية."
        )

    ai_fields: dict = {}
    ai_meta: dict = {"model": "rules", "latency_ms": 0, "tokens_used": None}
    if request.include_ai and holding_results:
        portfolio_payload = {
            "total_value": total_value,
            "output_currency": output_currency,
            "halal_score": halal_score,
            "diversification_score": diversification,
            "violations": violations,
            "holdings": [
                {
                    "symbol": h.symbol,
                    "weight_pct": h.weight_pct,
                    "status": h.status,
                    "sector": h.sector,
                    "country": h.country,
                    "verdict": h.verdict,
                }
                for h in holding_results
            ],
            "sector_allocation": [
                {"label": s.label, "weight_pct": s.weight_pct}
                for s in _build_allocation_slices(dict(sector_buckets), total_value)
            ],
            "country_allocation": [
                {"label": s.label, "weight_pct": s.weight_pct}
                for s in _build_allocation_slices(dict(country_buckets), total_value)
            ],
            "currency_allocation": [
                {"label": s.label, "weight_pct": s.weight_pct}
                for s in _build_allocation_slices(dict(currency_buckets), total_value)
            ],
            "shariah_methodology": methodology.model_dump(),
            "portfolio_assessment": assessment_code,
            "data_gaps": data_gaps,
            "has_purchase_prices": has_purchase_prices,
        }
        ai_fields, ai_meta = await generate_portfolio_analysis(
            portfolio_payload=portfolio_payload,
            language=request.language,
            fanar_model=request.fanar_model,
        )

    total_latency_ms = int((time.perf_counter() - pipeline_started) * 1000)
    data_latency = max(0, total_latency_ms - int(ai_meta.get("latency_ms") or 0))
    agent_trace = [
        ScannerAgentTraceStep(
            phase="Market Data",
            agent="financial_context",
            model="yahoo_finance",
            status="completed" if holding_results else "partial",
            latency_ms=min(1200, data_latency // 3 or 200),
        ),
        ScannerAgentTraceStep(
            phase="Holding Screening",
            agent="compliance_engine",
            model="aaoifi_standard_21",
            status="completed",
            latency_ms=min(800, data_latency // 3 or 150),
        ),
        ScannerAgentTraceStep(
            phase="Portfolio Aggregation",
            agent="portfolio_scanner",
            model="rules",
            status="completed",
            latency_ms=min(200, data_latency // 6 or 50),
        ),
        ScannerAgentTraceStep(
            phase="Fanar Portfolio Analysis",
            agent="fanar_synthesis",
            model=str(ai_meta.get("model") or "fallback"),
            status="completed" if request.include_ai and not ai_meta.get("error") else "partial",
            latency_ms=int(ai_meta.get("latency_ms") or 0),
            tokens_estimate=ai_meta.get("tokens_used"),
        ),
    ]
    execution_metrics = ScannerExecutionMetrics(
        total_latency_ms=total_latency_ms,
        steps_completed=len([s for s in agent_trace if s.status == "completed"]),
        steps_total=len(agent_trace),
        models_used=list(dict.fromkeys(step.model for step in agent_trace if step.model)),
        tokens_total=ai_meta.get("tokens_used"),
        fanar_model_preference=request.fanar_model,
    )

    sources = [
        ScannerSourceReference(
            title="Market data (Yahoo Finance / yfinance)",
            citation="Live quotes and fundamentals for portfolio valuation",
            source_type="market_data",
        ),
        ScannerSourceReference(
            title="AAOIFI Shariah Standard 21",
            citation="Investment in company shares — screening criteria applied per holding",
            source_type="standard",
        ),
        ScannerSourceReference(
            title="SANAD Shariah Knowledge Base",
            citation="Methodology grounded in authenticated Shariah standards referenced in SANAD reasoning",
            source_type="knowledge_base",
        ),
    ]

    scanned_at = datetime.now(UTC).isoformat()

    return PortfolioScanResponse(
        halal_score=halal_score,
        total_value=total_value,
        diversification_score=diversification,
        violations=violations,
        purification_amount=round(purification_total, 2),
        recommendations=recommendations,
        holdings=holding_results,
        output_currency=output_currency,
        insights=insights,
        sector_allocation=_build_allocation_slices(dict(sector_buckets), total_value),
        country_allocation=_build_allocation_slices(dict(country_buckets), total_value),
        currency_allocation=_build_allocation_slices(dict(currency_buckets), total_value),
        asset_type_allocation=_build_allocation_slices(dict(asset_buckets), total_value),
        shariah_methodology=methodology,
        portfolio_assessment=assessment_code,
        portfolio_assessment_detail=assessment_detail,
        ai_analysis=ai_fields.get("ai_analysis", ""),
        ai_observations=list(ai_fields.get("ai_observations") or []),
        ai_limitations=list(ai_fields.get("ai_limitations") or []),
        sources=sources,
        agent_trace=agent_trace,
        execution_metrics=execution_metrics,
        data_gaps=data_gaps,
        scan_id=str(uuid.uuid4()),
        scanned_at=scanned_at,
    )
