"""Align retrieved evidence language with the user's UI / query language."""

from __future__ import annotations

import logging

from agents.common.evidence import EvidenceItem
from agents.common.fanar_client import FanarLLMClient
from agents.reasoning_agent.tools import is_mostly_english

logger = logging.getLogger(__name__)


def _is_mostly_arabic(text: str) -> bool:
    alpha = [char for char in text if char.isalpha()]
    if len(alpha) < 12:
        return False
    arabic = sum(1 for char in alpha if "\u0600" <= char <= "\u06FF")
    return arabic / len(alpha) > 0.65


async def align_evidence_language(
    evidences: list[EvidenceItem],
    target_language: str,
    llm: FanarLLMClient,
) -> list[EvidenceItem]:
    """Translate evidence excerpts when they do not match the requested language."""
    if target_language not in {"ar", "en"} or not evidences:
        return evidences

    aligned: list[EvidenceItem] = []
    for item in evidences:
        text = item.text.strip()
        if not text:
            aligned.append(item)
            continue

        needs_translation = (
            target_language == "ar" and is_mostly_english(text)
        ) or (
            target_language == "en" and _is_mostly_arabic(text)
        )

        if not needs_translation:
            aligned.append(item.model_copy(update={"language": target_language}))
            continue

        source_language = "en" if target_language == "ar" else "ar"
        try:
            translated = await llm.translate_text(
                text,
                target_language=target_language,
                source_language=source_language,
            )
            if translated.strip():
                aligned.append(
                    item.model_copy(
                        update={
                            "text": translated.strip(),
                            "language": target_language,
                        }
                    )
                )
                continue
        except RuntimeError as exc:
            logger.warning("Evidence translation failed, keeping original: %s", exc)

        aligned.append(item.model_copy(update={"language": target_language}))

    return aligned
