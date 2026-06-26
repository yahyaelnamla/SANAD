"""Automatic query mode detection — routes users without manual configuration."""

from __future__ import annotations

import re
from typing import Literal

from backend.app.services.query_depth import (
    classify_query_depth,
    is_document_question,
)

AutoMode = Literal["fast", "normal", "deep", "document", "company", "portfolio", "voice"]

COMPANY_SIGNALS = (
    "tesla",
    "nvidia",
    "apple",
    "microsoft",
    "amazon",
    "stock",
    "shares",
    "equity",
    "ticker",
    "aaoifi",
    "halal stock",
    "company",
    "شركة",
    "سهم",
    "أسهم",
)

PORTFOLIO_SIGNALS = (
    "portfolio",
    "holdings",
    "my investments",
    "etf",
    "mutual fund",
    "diversification",
    "purification",
    "محفظة",
    "استثمارات",
    "صندوق",
)

VOICE_SIGNALS = (
    "[voice]",
    "transcript:",
    "spoken question",
)


def detect_auto_mode(question: str) -> AutoMode:
    """Infer the best SANAD mode from the user question."""
    text = question.strip()
    lowered = text.lower()

    if any(signal in lowered for signal in VOICE_SIGNALS):
        return "voice"
    if is_document_question(text):
        return "document"
    if any(signal in lowered for signal in PORTFOLIO_SIGNALS):
        return "portfolio"
    if any(signal in lowered for signal in COMPANY_SIGNALS):
        return "company"

    depth = classify_query_depth(text)
    if depth == "fast":
        return "fast"
    if any(signal in lowered for signal in ("compare", "versus", " vs ", "disagree", "مقارنة")):
        return "deep"

    words = re.findall(r"[\w\u0600-\u06ff]+", text)
    if len(words) > 18:
        return "deep"
    return "normal"


def auto_mode_requires_financial(mode: AutoMode) -> bool:
    """Whether financial context agent should run for this auto mode."""
    return mode in {"company", "portfolio", "deep", "normal"}


def auto_mode_label(mode: AutoMode) -> str:
    """Human-readable label for UI badges."""
    labels = {
        "fast": "Fast answer",
        "normal": "Standard analysis",
        "deep": "Deep analysis",
        "document": "Document analysis",
        "company": "Company screening",
        "portfolio": "Portfolio analysis",
        "voice": "Voice query",
    }
    return labels.get(mode, mode)
