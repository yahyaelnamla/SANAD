"""Central Fanar model routing — quality-first, speed-aware selection."""

from __future__ import annotations

from typing import Literal

from config.fanar_api_keys import FANAR_MODELS

TaskKind = Literal[
    "intent",
    "retrieval",
    "knowledge",
    "reasoning",
    "verification",
    "response",
    "translation",
    "transcription",
    "document_ocr",
    "memory_summary",
    "follow_up",
    "plan",
]

ModelPreference = Literal["auto", "sadiq", "c2", "guard"]


def _arabic_model(task: TaskKind) -> str:
    """Prefer Arabic-optimised Fanar variants for Arabic queries."""
    if task == "reasoning":
        return FANAR_MODELS["generation_ar"]
    if task == "retrieval":
        return FANAR_MODELS["rag"]
    if task in {"intent", "knowledge", "response", "memory_summary", "follow_up", "plan"}:
        return FANAR_MODELS["generation_ar"]
    return FANAR_MODELS["generation_ar"]


def model_for_task(
    task: TaskKind,
    *,
    depth: str = "deep",
    preference: str = "auto",
    language: str | None = None,
) -> str:
    """Return the Fanar model identifier for a pipeline task."""
    pref = preference if preference in {"auto", "sadiq", "c2", "guard"} else "auto"

    if language == "ar" and pref == "auto":
        return _arabic_model(task)

    if pref == "sadiq":
        if task == "reasoning":
            return FANAR_MODELS["generation_ar"]
        if task == "verification":
            return FANAR_MODELS["guard"]
        if task == "retrieval":
            return FANAR_MODELS["rag"]
        if task in {"intent", "knowledge", "response", "memory_summary", "follow_up"}:
            return FANAR_MODELS["generation_ar"]
        if task == "plan":
            return FANAR_MODELS.get("agentic", FANAR_MODELS.get("reasoning", FANAR_MODELS["generation_ar"]))
        return FANAR_MODELS["agentic"]

    if pref in {"c2", "guard"}:
        if task == "reasoning":
            return FANAR_MODELS["reasoning"]
        if task == "verification":
            return FANAR_MODELS["guard"]
        if task == "retrieval":
            return FANAR_MODELS["rag"]
        if task in {"intent", "knowledge", "response", "memory_summary", "follow_up"}:
            return FANAR_MODELS["generation_ar"]
        if task == "plan":
            return FANAR_MODELS.get("agentic", FANAR_MODELS["reasoning"])
        return FANAR_MODELS["agentic"]

    if task == "plan":
        return FANAR_MODELS.get("agentic", FANAR_MODELS.get("reasoning", FANAR_MODELS["generation_ar"]))
    if task == "reasoning":
        return FANAR_MODELS["reasoning"] if depth == "deep" else FANAR_MODELS["generation_ar"]
    if task == "verification":
        return FANAR_MODELS["guard"]
    if task == "retrieval":
        return FANAR_MODELS["rag"]
    if task == "translation":
        return FANAR_MODELS["translation"]
    if task == "transcription":
        return FANAR_MODELS["stt"]
    if task == "document_ocr":
        return FANAR_MODELS["vision"]
    if task in {"intent", "knowledge", "response", "memory_summary", "follow_up"}:
        return FANAR_MODELS["generation_ar"]
    return FANAR_MODELS["agentic"]


def fanar_capabilities_manifest() -> dict[str, str]:
    """Map Fanar products to their roles for evaluation / judge panels."""
    return {
        "Fanar-Sadiq": "General answers, Arabic generation, summaries, fast responses, RAG retrieval",
        "Fanar-Sadiq-Agentic": "Multi-agent pipeline planning and tool orchestration",
        "Fanar-C-2-27B": "Complex reasoning, comparisons, fatwa disagreements, multi-step synthesis",
        "Fanar-Guard-2": "Mandatory verification — never bypassed; fail-closed on API outage",
        "Fanar-Aura-STT-1": "Voice conversations, Arabic dialects, speech-to-text",
        "Fanar-Oryx-IVU-2": "PDF OCR, tables, financial reports, scanned documents",
        "Fanar-Shaheen-MT-1": "Bilingual and multilingual translation",
    }


def fanar_capability_improvements() -> dict[str, str]:
    """Per-model improvement notes for judge evaluation panels."""
    return {
        "Fanar-Sadiq": "Native SSE token streaming would reduce perceived latency in chat.",
        "Fanar-Sadiq-Agentic": "Structured tool-call schema for Yahoo Finance / Serper would simplify orchestration.",
        "Fanar-C-2-27B": "Dedicated Arabic fiqh JSON schema for madhhab matrices and opinion objects.",
        "Fanar-Guard-2": "Batch moderation endpoint for multi-section responses (summary + analysis).",
        "Fanar-Aura-STT-1": "Real-time partial transcripts during long-form scholarly questions.",
        "Fanar-Oryx-IVU-2": "Table extraction mode tuned for AAOIFI annual report layouts.",
        "Fanar-Shaheen-MT-1": "Preserve inline Quran/Hadith citations when translating answers.",
    }
