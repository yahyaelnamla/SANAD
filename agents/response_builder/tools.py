"""Response Builder tools for formatting final output."""

import json
import re
from typing import Any

from agents.common.evidence import EvidenceItem
from agents.common.evidence_enrichment import enrich_evidence_list
from agents.common.honesty_disclaimers import append_honesty_to_reasoning, build_honesty_disclaimers
from agents.knowledge_agent.models import EvidenceBundle, JurisprudentialPrinciple
from agents.reasoning_agent.models import ReasoningResult, ScholarlyOpinion
from agents.response_builder.models import FinalResponse

MAX_ANSWER_CHARS = 100000
MAX_CONCLUSION_CHARS = 2000
MAX_REASONING_CHARS = 100000

_THINKING_TAG_PATTERN = re.compile(
    r"<(?:thinking|redacted_thinking)>[\s\S]*?(?:</(?:thinking|redacted_thinking)>|$)",
    re.IGNORECASE,
)
_CODE_FENCE_PATTERN = re.compile(r"```[\w]*\n?|```")
_JSON_OBJECT_PATTERN = re.compile(r"^\s*\{[\s\S]*\}\s*$")
_JSON_LEAK_PATTERN = re.compile(r"\{[\s\S]*?\"analysis\"[\s\S]*?\}", re.MULTILINE)
_PLANNING_LINE = re.compile(
    r"^(?:The user|The question|Let me|I need to|First,|Next,|Now,|For adilla|"
    r"These form|Moving to|I should|I will|Double-check|Specifically,).*$",
    re.MULTILINE | re.IGNORECASE,
)
_INLINE_CITATION_PATTERN = re.compile(
    r"\s*\[[\d\u0660-\u0669,\s]+\]|\s*\(\d{1,3}\)|\bnbs\b|&nbsp;|&#160;",
    re.IGNORECASE,
)


def strip_inline_citations(text: str) -> str:
    """Remove inline reference numbers and model artifacts from user-facing text."""
    cleaned = _INLINE_CITATION_PATTERN.sub("", text)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def sanitize_user_text(text: str | None) -> str:
    """Remove internal artifacts from user-facing text."""
    if not text or not text.strip():
        return ""

    cleaned = _THINKING_TAG_PATTERN.sub("", text).strip()
    cleaned = _CODE_FENCE_PATTERN.sub("", cleaned).strip()
    cleaned = _PLANNING_LINE.sub("", cleaned).strip()
    cleaned = _JSON_LEAK_PATTERN.sub("", cleaned).strip()

    if _JSON_OBJECT_PATTERN.match(cleaned):
        try:
            payload = json.loads(cleaned)
            if isinstance(payload, dict):
                for key in ("summary", "analysis", "reasoning", "text"):
                    value = payload.get(key)
                    if isinstance(value, str) and value.strip():
                        return sanitize_user_text(value)
        except json.JSONDecodeError:
            pass

    return strip_inline_citations(cleaned)


def truncate_text(text: str, max_chars: int) -> str:
    """Truncate text at a word boundary."""
    if len(text) <= max_chars:
        return text
    trimmed = text[:max_chars].rsplit(" ", 1)[0].strip()
    return f"{trimmed}…" if trimmed else f"{text[:max_chars].strip()}…"


def dedupe_evidence(evidences: list[EvidenceItem]) -> list[EvidenceItem]:
    """Remove duplicate evidence by chunk id or near-identical text."""
    seen_chunks: set[str] = set()
    seen_text: set[str] = set()
    unique: list[EvidenceItem] = []

    for item in evidences:
        if item.chunk_id in seen_chunks:
            continue
        normalized = re.sub(r"\s+", " ", item.text.strip().lower())[:160]
        if normalized in seen_text:
            continue
        seen_chunks.add(item.chunk_id)
        seen_text.add(normalized)
        unique.append(item)

    return unique


def dedupe_principles(principles: list[JurisprudentialPrinciple]) -> list[JurisprudentialPrinciple]:
    """Remove duplicate fiqh principles by name."""
    seen: set[str] = set()
    unique: list[JurisprudentialPrinciple] = []

    for principle in principles:
        key = principle.name.strip().lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(principle)

    return unique


def dedupe_opinions(opinions: list[ScholarlyOpinion]) -> list[ScholarlyOpinion]:
    """Remove duplicate scholarly opinions."""
    seen: set[str] = set()
    unique: list[ScholarlyOpinion] = []

    for opinion in opinions:
        key = f"{opinion.scholar.strip().lower()}|{opinion.position.strip().lower()[:100]}"
        if key in seen:
            continue
        seen.add(key)
        unique.append(opinion)

    return unique


def build_reasoning_display(reasoning: ReasoningResult) -> str:
    """Build a concise reasoning summary without repeating the analysis."""
    analysis = sanitize_user_text(reasoning.analysis)
    if not reasoning.reasoning_steps:
        return analysis

    analysis_lower = analysis.lower()
    unique_steps: list[str] = []
    seen_steps: set[str] = set()

    for step in reasoning.reasoning_steps:
        cleaned = sanitize_user_text(step)
        if not cleaned:
            continue
        normalized = cleaned.lower()
        if normalized in seen_steps or normalized in analysis_lower:
            continue
        seen_steps.add(normalized)
        unique_steps.append(cleaned)

    if not unique_steps:
        return analysis

    steps_text = "\n".join(f"• {step}" for step in unique_steps[:5])
    combined = f"{steps_text}\n\n{analysis}" if analysis else steps_text
    return combined


def build_summary_text(
    summary: str | None,
    reasoning: ReasoningResult,
    language: str,
) -> str:
    """Build the full user-facing answer with a brief conclusion at the end."""
    analysis = sanitize_user_text(reasoning.analysis)
    brief = sanitize_user_text(summary)

    if not analysis and not brief:
        return (
            "تعذر تقديم إجابة."
            if language == "ar"
            else "Unable to provide an answer."
        )

    body = analysis or brief
    conclusion = ""
    if brief:
        norm_body = body.strip().lower()
        norm_brief = brief.strip().lower()
        if norm_brief != norm_body and norm_brief not in norm_body:
            conclusion = brief

    if conclusion:
        label = "خلاصة" if language == "ar" else "In short"
        return f"{body}\n\n━━━\n{label}\n{conclusion}"

    return body


def build_sources_list(evidences: list[EvidenceItem]) -> list[dict[str, Any]]:
    """Deduplicate sources from evidence items."""
    seen: set[str] = set()
    sources: list[dict[str, Any]] = []
    for item in evidences:
        if item.source_id in seen:
            continue
        seen.add(item.source_id)
        sources.append(
            {
                "source_id": item.source_id,
                "title": item.source_title,
                "author": item.source_author,
                "type": item.source_type,
                "citation": item.citation,
            }
        )
    return sources


def build_refusal_response(
    reason: str,
    language: str = "en",
    agent_trace: list[dict[str, Any]] | None = None,
) -> FinalResponse:
    """Build a refusal response when no evidence exists."""
    return FinalResponse(
        summary="Unable to provide an analysis without authenticated evidence.",
        reasoning="",
        confidence=0.0,
        language=language,
        refused=True,
        refusal_reason=reason,
        agent_trace=agent_trace or [],
    )


def build_final_response(
    bundle: EvidenceBundle,
    reasoning: ReasoningResult,
    language: str,
    summary: str | None = None,
    agent_trace: list[dict[str, Any]] | None = None,
    confidence_breakdown: dict[str, float] | None = None,
    financial_context: dict[str, Any] | None = None,
    execution_metrics: dict[str, Any] | None = None,
) -> FinalResponse:
    """Assemble the explainability chain into FinalResponse."""
    bundle.evidences = enrich_evidence_list(bundle.evidences)
    evidences = dedupe_evidence(bundle.evidences)
    principles = dedupe_principles(bundle.principles)
    opinions = dedupe_opinions(reasoning.opinions)
    reasoning_text = build_reasoning_display(reasoning)
    disclaimers = build_honesty_disclaimers(bundle, reasoning, language=language)
    reasoning_text = append_honesty_to_reasoning(reasoning_text, disclaimers)
    summary_text = build_summary_text(summary, reasoning, language)

    sources = build_sources_list(evidences)
    for item in evidences:
        url = (item.metadata or {}).get("source_url")
        if url:
            for source in sources:
                if source["source_id"] == item.source_id and not source.get("source_url"):
                    source["source_url"] = url

    return FinalResponse(
        summary=summary_text,
        evidence=evidences,
        principles=principles,
        reasoning=reasoning_text,
        opinions=opinions,
        sources=sources,
        confidence=reasoning.confidence,
        confidence_breakdown=confidence_breakdown or {},
        language=language,
        agent_trace=agent_trace or [],
        thinking_trace=None,
        financial_context=financial_context,
        execution_metrics=execution_metrics,
        madhhab_matrix=[m.model_dump() for m in reasoning.madhhab_matrix],
    )
