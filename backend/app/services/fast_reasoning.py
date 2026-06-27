"""Lightweight reasoning synthesis via Fanar API (fast pipeline path)."""

from __future__ import annotations

from agents.common.fanar_client import FanarLLMClient
from agents.intent_agent.models import IntentResult
from agents.knowledge_agent.models import EvidenceBundle
from agents.reasoning_agent.models import ReasoningResult
from agents.reasoning_agent.tools import format_evidence_for_prompt
from agents.response_builder.tools import sanitize_user_text
from config.fanar_api_keys import FANAR_MODELS


async def build_fast_reasoning(
    bundle: EvidenceBundle,
    intent: IntentResult,
    *,
    llm: FanarLLMClient | None = None,
) -> ReasoningResult:
    """Build a concise reasoning object using Fanar-Sadiq (no template text)."""
    client = llm or FanarLLMClient()
    evidence_text = format_evidence_for_prompt(bundle)
    language = intent.language if intent.language in {"ar", "en"} else "ar"
    language_rule = (
        "اكتب الإجابة بالعربية الفصحى فقط."
        if language == "ar"
        else "Write the answer in English only."
    )

    text = await client.complete(
        model=FANAR_MODELS["generation_ar"],
        messages=[
            {
                "role": "system",
                "content": (
                    "You are SANAD, an Islamic finance assistant. "
                    "Answer only from the supplied evidence. "
                    "Provide 2–4 clear paragraphs. No inline citation numbers."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Language: {language}\n"
                    f"{language_rule}\n"
                    f"Question: {intent.raw_query}\n"
                    f"Evidence:\n{evidence_text}\n"
                    "Write the final user-facing answer only."
                ),
            },
        ],
        max_tokens=2000,
        enable_thinking=False,
    )

    analysis = sanitize_user_text(text)
    citations = [item.citation for item in bundle.evidences[:5] if item.citation]
    principles = [principle.name for principle in bundle.principles[:4]]

    return ReasoningResult(
        principles_applied=principles,
        analysis=analysis,
        citations=citations,
        confidence=0.78,
        active_model=FANAR_MODELS["generation_ar"],
    )
