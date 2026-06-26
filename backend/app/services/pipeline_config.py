"""Resolve pipeline depth and retrieval settings from user preferences and question."""

from __future__ import annotations

from backend.app.services.auto_mode_service import AutoMode, detect_auto_mode
from backend.app.services.query_depth import QueryDepth, classify_query_depth


def resolve_pipeline_config(
    question: str,
    *,
    advanced_analysis: bool,
    fanar_model: str,
) -> tuple[QueryDepth, int, bool, AutoMode]:
    """
    Return (depth, top_k, advanced_analysis, auto_mode).

    Priority:
    1. Explicit model choice (sadiq → fast, c2/guard → deep)
    2. User advanced toggle → deep
    3. Auto model → classify question complexity
    4. Default → standard
    """
    auto_mode = detect_auto_mode(question)

    if fanar_model in {"c2", "guard"}:
        return "deep", 12, True, auto_mode
    if fanar_model == "sadiq":
        return "fast", 5, False, auto_mode
    if advanced_analysis:
        return "deep", 12, True, auto_mode

    if fanar_model == "auto":
        classified = classify_query_depth(question)
        if classified == "fast":
            return "fast", 5, False, auto_mode
        if classified == "deep":
            return "deep", 12, True, auto_mode
        return "standard", 8, False, auto_mode

    return "standard", 8, False, auto_mode
