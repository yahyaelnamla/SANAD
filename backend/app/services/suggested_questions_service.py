"""Generate suggested follow-up questions after each answer."""

from __future__ import annotations

import json
import re

from agents.common.fanar_client import FanarLLMClient
from backend.app.services.fanar_model_router import model_for_task

MAX_SUGGESTIONS = 4


async def generate_suggested_questions(
    llm: FanarLLMClient,
    *,
    question: str,
    summary: str,
    language: str = "en",
) -> list[str]:
    """Generate related follow-up questions using Fanar-Sadiq."""
    if not summary.strip():
        return []

    lang_label = "Arabic" if language == "ar" else "English"
    model = model_for_task("follow_up")

    try:
        raw = await llm.complete_json(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"Generate {MAX_SUGGESTIONS} concise related Islamic finance follow-up "
                        f"questions in {lang_label}. Return JSON with a questions array. "
                        "Questions must be specific to the user's question and answer, actionable, "
                        "and distinct. Do not repeat the original question."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Original question: {question}\n\nAnswer summary: {summary[:800]}",
                },
            ],
            temperature=0.4,
        )
        questions = raw.get("questions", [])
        if isinstance(questions, list):
            cleaned = [_clean_question(q) for q in questions if isinstance(q, str)]
            return [q for q in cleaned if q][:MAX_SUGGESTIONS]
    except (RuntimeError, json.JSONDecodeError, ValueError):
        pass

    return _fallback_suggestions(question, language)


def _clean_question(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text.strip())
    cleaned = cleaned.strip("-•*\"'")
    if cleaned and not cleaned.endswith("?"):
        cleaned += "?"
    return cleaned[:200]


def _fallback_suggestions(question: str, language: str) -> list[str]:
    """Heuristic suggestions when LLM generation is unavailable."""
    lowered = question.lower()
    if language == "ar":
        if "ربا" in question or "riba" in lowered:
            return [
                "ما حكم التمويل الاستهلاكي بالفائدة؟",
                "كيف يمكن تجنب الربا في المعاملات اليومية؟",
            ]
        if "زكاة" in question or "zakat" in lowered:
            return [
                "ما هي نصاب الزكاة على الذهب؟",
                "هل تجب الزكاة على الأسهم؟",
            ]
        return [
            "ما رأي العلماء في صناديق الاستثمار الإسلامية؟",
            "كيف أتحقق من توافق الشركة مع المعايير الشرعية؟",
        ]

    if "riba" in lowered or "interest" in lowered:
        return [
            "What do scholars say about conventional mortgages?",
            "How can I avoid riba in daily transactions?",
        ]
    if "zakat" in lowered:
        return [
            "What is the nisab threshold for gold?",
            "Is zakat due on stocks and ETFs?",
        ]
    if "bitcoin" in lowered or "crypto" in lowered:
        return [
            "Is Bitcoin staking permissible?",
            "What do scholars say about Islamic crypto funds?",
        ]
    return [
        "What do scholars say about Shariah-compliant ETFs?",
        "How do I screen a company for Shariah compliance?",
    ]
