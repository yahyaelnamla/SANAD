"""Heuristic routing for fast vs deep pipeline execution."""

from __future__ import annotations

import re
from typing import Literal

QueryDepth = Literal["fast", "standard", "deep"]

COMPLEX_SIGNALS = (
    "compare",
    "versus",
    " vs ",
    "difference between",
    "disagree",
    "staking",
    "controversial",
    "debate",
    "both sides",
    "pros and cons",
    "multi-step",
    "structure of",
    "murabaha vs",
    "portfolio",
    "diversification",
    "purification",
    "aaofi screening",
    "مقارنة",
    "اختلاف",
    "جدل",
    "محفظة",
    "تنويع",
)

DOCUMENT_SIGNALS = (
    "document",
    "pdf",
    "report",
    "annual report",
    "uploaded",
    "my file",
    "page ",
    "chapter",
    "what did",
    "summarize chapter",
    "mentioned in",
    "discussed in",
    "annual-report",
    "مستند",
    "تقرير",
    "صفحة",
    "فصل",
    "الملف",
    "رفعت",
    "السنوي",
)

FAST_SIMPLE_PATTERNS = (
    "is riba",
    "is usury",
    "is interest haram",
    "is bitcoin halal",
    "what is riba",
    "what is zakat",
    "define riba",
    "define zakat",
    "هل الربا",
    "ما هو الربا",
    "هل ربا",
    "ما هي الزكاة",
)

FAST_EXECUTE_STEPS = ["intent", "retrieval", "knowledge", "reasoning"]
STANDARD_EXECUTE_STEPS = ["intent", "retrieval", "knowledge", "reasoning"]
DEEP_EXECUTE_STEPS = [
    "intent",
    "retrieval",
    "knowledge",
    "financial",
    "reasoning",
]


def classify_query_depth(question: str) -> QueryDepth:
    """Route simple factual questions to a fast pipeline; complex ones to deep analysis."""
    text = question.strip()
    if not text:
        return "deep"

    lowered = text.lower()
    words = re.findall(r"[\w\u0600-\u06ff]+", text)
    word_count = len(words)

    if any(signal in lowered for signal in COMPLEX_SIGNALS):
        return "deep"
    if word_count > 24:
        return "deep"
    if text.count("?") > 1:
        return "deep"
    if word_count <= 12 and any(pattern in lowered for pattern in FAST_SIMPLE_PATTERNS):
        return "fast"
    if word_count <= 10 and any(token in lowered for token in ("halal", "haram", "permissible", "prohibited")):
        return "fast"
    if word_count <= 8 and any(token in text for token in ("حلال", "حرام", "جائز", "محرم")):
        return "fast"

    return "standard"


def is_document_question(question: str) -> bool:
    """Detect follow-up questions about uploaded PDFs."""
    lowered = question.lower()
    return any(signal in lowered for signal in DOCUMENT_SIGNALS)


def plan_for_depth(depth: QueryDepth) -> dict:
    """Return orchestrator execution plan metadata."""
    if depth == "fast":
        return {
            "steps": list(FAST_EXECUTE_STEPS),
            "requires_financial_context": False,
            "depth": "fast",
        }
    if depth == "standard":
        return {
            "steps": list(STANDARD_EXECUTE_STEPS),
            "requires_financial_context": False,
            "depth": "standard",
        }
    return {
        "steps": list(DEEP_EXECUTE_STEPS),
        "requires_financial_context": True,
        "depth": "deep",
    }
