"""Fanar-powered synthesis for the company analysis scanner."""

from __future__ import annotations

import json
import logging
import os
import re
import time
from typing import Any

from agents.common.fanar_client import FanarLLMClient
from backend.app.services.fanar_model_router import model_for_task

logger = logging.getLogger(__name__)

PROHIBITED_SECTORS = {
    "alcohol",
    "tobacco",
    "gambling",
    "casino",
    "conventional banking",
    "interest",
    "adult",
    "pork",
    "weapons",
}


def _extract_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", cleaned)
        if match:
            return json.loads(match.group(0))
        raise


def _fallback_analysis(
    *,
    company_name: str,
    status: str,
    debt_ratio: float | None,
    interest_ratio: float | None,
    non_permissible_ratio: float | None,
    language: str,
) -> dict[str, Any]:
    ar = language == "ar"
    if status == "green":
        summary = (
            f"{company_name} تبدو متوافقة مع معايير AAOIFI بشكل عام."
            if ar
            else f"{company_name} appears broadly compliant with AAOIFI screening thresholds."
        )
    elif status == "red":
        summary = (
            f"{company_name} قد لا تكون مناسبة للاستثمار الشرعي دون مراجعة إضافية."
            if ar
            else f"{company_name} may not be suitable for Shariah-compliant investment without further review."
        )
    else:
        summary = (
            f"{company_name} في منطقة حدودية — قد يلزم التطهير أو مراجعة التقارير السنوية."
            if ar
            else f"{company_name} is borderline — purification or annual report review may be required."
        )

    takeaways = [
        (
            "نسبة الدين ضمن الحدود المقبولة."
            if ar and (debt_ratio or 0) <= 0.30
            else "Debt ratio within acceptable limits."
            if (debt_ratio or 0) <= 0.30
            else (
                "نسبة الدين تتجاوز حد AAOIFI (30%)."
                if ar
                else "Debt ratio exceeds the AAOIFI 30% threshold."
            )
        ),
        (
            "الدخل غير المشروع ضمن 5%."
            if ar and (non_permissible_ratio or 0) <= 0.05
            else "Non-permissible income within 5%."
            if (non_permissible_ratio or 0) <= 0.05
            else (
                "قد يتجاوز الدخل غير المشروع 5%."
                if ar
                else "Non-permissible income may exceed 5%."
            )
        ),
        (
            "راجع النشاط التجاري والتقارير السنوية قبل الاستثمار."
            if ar
            else "Review business activity and annual filings before investing."
        ),
    ]

    qualitative_status = "fail" if status == "red" else "pass"
    qualitative_analysis = (
        "النشاط التجاري يتطلب مراجعة يدوية للتأكد من عدم وجود أنشطة محظورة."
        if ar
        else "Business activity requires manual review to confirm no prohibited revenue streams."
    )

    financial_assessment = (
        "التقييم المالي يعتمد على البيانات المتاحة — قارن النسب مع أقران القطاع."
        if ar
        else "Financial assessment is based on available market data — compare ratios with sector peers."
    )

    return {
        "ai_summary": summary,
        "key_takeaways": takeaways[:4],
        "qualitative_status": qualitative_status,
        "qualitative_analysis": qualitative_analysis,
        "ai_financial_assessment": financial_assessment,
    }


async def generate_company_analysis(
    *,
    company_name: str,
    symbol: str | None,
    fundamentals: dict[str, Any],
    ratios: dict[str, float | None],
    status: str,
    language: str = "en",
    fanar_model: str = "auto",
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return AI synthesis fields and execution metadata."""
    api_key = os.getenv("FANAR_API_KEY", "")
    started = time.perf_counter()
    tokens_used: int | None = None
    model_used = model_for_task("reasoning", depth="deep", preference=fanar_model)

    payload = {
        "company_name": company_name,
        "symbol": symbol,
        "sector": fundamentals.get("sector"),
        "industry": fundamentals.get("industry"),
        "business_summary": (fundamentals.get("business_summary") or "")[:1200],
        "financial_metrics": {
            "pe_ratio": fundamentals.get("pe_ratio"),
            "pb_ratio": fundamentals.get("pb_ratio"),
            "peg_ratio": fundamentals.get("peg_ratio"),
            "gross_margin": fundamentals.get("gross_margin"),
            "net_margin": fundamentals.get("net_margin"),
            "roe": fundamentals.get("roe"),
            "current_ratio": fundamentals.get("current_ratio"),
            "debt_to_equity": fundamentals.get("debt_to_equity"),
        },
        "aaoifi_ratios": ratios,
        "compliance_status": status,
    }

    if not api_key:
        fallback = _fallback_analysis(
            company_name=company_name,
            status=status,
            debt_ratio=ratios.get("interest_bearing_debt_ratio"),
            interest_ratio=ratios.get("interest_earning_investments_ratio"),
            non_permissible_ratio=ratios.get("non_permissible_income_ratio"),
            language=language,
        )
        latency_ms = int((time.perf_counter() - started) * 1000)
        return fallback, {
            "model": "fallback",
            "latency_ms": latency_ms,
            "tokens_used": None,
        }

    lang_label = "Arabic" if language == "ar" else "English"
    client = FanarLLMClient(api_key=api_key)

    system = (
        "You are an expert Islamic finance analyst and financial advisor. "
        "Evaluate company data using AAOIFI Shariah Standard 21 and fundamental analysis. "
        f"Respond in {lang_label}. Output ONLY valid JSON with keys: "
        "ai_summary (string, 2-4 sentences answering if this is a good permissible investment), "
        "key_takeaways (array of 3-4 short strings), "
        "qualitative_status (pass or fail), "
        "qualitative_analysis (string on business activity screening), "
        "ai_financial_assessment (string interpreting valuation and profitability metrics). "
        "Do not invent exact fatwa citations. Be evidence-based from provided data."
    )

    try:
        raw = await client.complete(
            model=model_used,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            temperature=0.25,
            max_tokens=700,
            response_format={"type": "json_object"},
        )
        tokens_used = client.consume_tokens_since_last()
        parsed = _extract_json(raw)
        for key in (
            "ai_summary",
            "key_takeaways",
            "qualitative_status",
            "qualitative_analysis",
            "ai_financial_assessment",
        ):
            if key not in parsed:
                raise KeyError(key)
        if parsed.get("qualitative_status") not in {"pass", "fail"}:
            parsed["qualitative_status"] = "fail" if status == "red" else "pass"
        latency_ms = int((time.perf_counter() - started) * 1000)
        return parsed, {
            "model": model_used,
            "latency_ms": latency_ms,
            "tokens_used": tokens_used,
        }
    except (RuntimeError, json.JSONDecodeError, KeyError, ValueError) as exc:
        logger.warning("Company scanner AI failed: %s", exc)
        fallback = _fallback_analysis(
            company_name=company_name,
            status=status,
            debt_ratio=ratios.get("interest_bearing_debt_ratio"),
            interest_ratio=ratios.get("interest_earning_investments_ratio"),
            non_permissible_ratio=ratios.get("non_permissible_income_ratio"),
            language=language,
        )
        latency_ms = int((time.perf_counter() - started) * 1000)
        return fallback, {
            "model": model_used,
            "latency_ms": latency_ms,
            "tokens_used": tokens_used,
            "error": str(exc),
        }


def _fallback_portfolio_analysis(
    *,
    portfolio_payload: dict[str, Any],
    language: str,
) -> dict[str, Any]:
    ar = language == "ar"
    holdings = portfolio_payload.get("holdings") or []
    total = portfolio_payload.get("total_value") or 0
    div_score = portfolio_payload.get("diversification_score") or 0
    halal_score = portfolio_payload.get("halal_score") or 0
    violations = portfolio_payload.get("violations") or []

    if ar:
        summary = (
            f"تحليل المحفظة يغطي {len(holdings)} أصل بقيمة إجمالية {total:,.0f} "
            f"{portfolio_payload.get('output_currency', 'USD')}. "
            f"درجة الامتثال المرجّحة {halal_score * 100:.0f}% وفق منهجية AAOIFI المطبقة على كل أصل."
        )
    else:
        summary = (
            f"Portfolio analysis covers {len(holdings)} holdings worth {total:,.0f} "
            f"{portfolio_payload.get('output_currency', 'USD')}. "
            f"Weighted compliance score is {halal_score * 100:.0f}% using the documented AAOIFI methodology per holding."
        )

    observations: list[str] = []
    if div_score < 0.4:
        observations.append(
            "تركّز المحفظة مرتفع — فكّر في تنويع القطاعات والجغرافيا."
            if ar
            else "Portfolio concentration is elevated — consider diversifying sectors and geography."
        )
    if violations:
        observations.append(
            f"هناك {len(violations)} ملاحظة امتثال تتطلب مراجعة."
            if ar
            else f"{len(violations)} compliance flag(s) require review."
        )
    sectors = portfolio_payload.get("sector_allocation") or []
    if sectors and sectors[0].get("weight_pct", 0) > 40:
        label = sectors[0].get("label", "")
        observations.append(
            f"القطاع {label} يمثل أكثر من 40% من المحفظة."
            if ar
            else f"Sector '{label}' exceeds 40% of portfolio weight."
        )
    if not observations:
        observations.append(
            "لا توجد مخاوف تركّز حادة — استمر في إعادة الفحص الدوري."
            if ar
            else "No acute concentration flags — continue periodic re-screening."
        )

    limitations: list[str] = []
    data_gaps = portfolio_payload.get("data_gaps") or []
    if data_gaps:
        limitations.extend(data_gaps[:3])
    if not portfolio_payload.get("has_purchase_prices"):
        limitations.append(
            "لم تُقدّم أسعار الشراء — العائد/الخسارة غير المحققة غير متاح."
            if ar
            else "Purchase prices not provided — unrealized gain/loss unavailable."
        )

    return {
        "ai_analysis": summary,
        "ai_observations": observations[:6],
        "ai_limitations": limitations[:5],
    }


async def generate_portfolio_analysis(
    *,
    portfolio_payload: dict[str, Any],
    language: str = "en",
    fanar_model: str = "auto",
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return portfolio-level AI synthesis fields and execution metadata."""
    api_key = os.getenv("FANAR_API_KEY", "")
    started = time.perf_counter()
    tokens_used: int | None = None
    model_used = model_for_task("reasoning", depth="deep", preference=fanar_model)

    if not api_key:
        fallback = _fallback_portfolio_analysis(portfolio_payload=portfolio_payload, language=language)
        latency_ms = int((time.perf_counter() - started) * 1000)
        return fallback, {"model": "fallback", "latency_ms": latency_ms, "tokens_used": None}

    lang_label = "Arabic" if language == "ar" else "English"
    client = FanarLLMClient(api_key=api_key)

    system = (
        "You are an expert Islamic finance portfolio analyst. "
        "Analyze the ENTIRE portfolio holistically — not individual stock deep dives. "
        "Focus on concentration, diversification, sector/geography/currency exposure, "
        "compliance aggregation, and improvement suggestions. "
        "Use ONLY the provided portfolio data and Shariah methodology context. "
        "Do NOT invent fatwas or generic investment advice. "
        "Cite specific holdings and metrics from the payload as evidence. "
        f"Respond in {lang_label}. Output ONLY valid JSON with keys: "
        "ai_analysis (string, 3-5 sentences on portfolio-level observations), "
        "ai_observations (array of 3-6 short strings on concentration, exposure, diversification), "
        "ai_limitations (array of strings noting data gaps or items needing scholar review)."
    )

    try:
        raw = await client.complete(
            model=model_used,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(portfolio_payload, ensure_ascii=False)},
            ],
            temperature=0.25,
            max_tokens=900,
            response_format={"type": "json_object"},
        )
        tokens_used = client.consume_tokens_since_last()
        parsed = _extract_json(raw)
        for key in ("ai_analysis", "ai_observations", "ai_limitations"):
            if key not in parsed:
                raise KeyError(key)
        latency_ms = int((time.perf_counter() - started) * 1000)
        return parsed, {
            "model": model_used,
            "latency_ms": latency_ms,
            "tokens_used": tokens_used,
        }
    except (RuntimeError, json.JSONDecodeError, KeyError, ValueError) as exc:
        logger.warning("Portfolio scanner AI failed: %s", exc)
        fallback = _fallback_portfolio_analysis(portfolio_payload=portfolio_payload, language=language)
        latency_ms = int((time.perf_counter() - started) * 1000)
        return fallback, {
            "model": model_used,
            "latency_ms": latency_ms,
            "tokens_used": tokens_used,
            "error": str(exc),
        }
