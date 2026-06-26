"""Helpers for post-answer translation via Fanar."""

from __future__ import annotations

import logging
import re

from agents.common.fanar_client import FanarLLMClient

logger = logging.getLogger(__name__)

CHUNK_SIZE = 1600


def detect_language(text: str, fallback: str = "ar") -> str:
    """Rough language detection for Arabic vs Latin scripts."""
    if not text.strip():
        return fallback
    arabic_chars = len(re.findall(r"[\u0600-\u06FF]", text))
    latin_chars = len(re.findall(r"[A-Za-z]", text))
    if arabic_chars > latin_chars:
        return "ar"
    if latin_chars > 0:
        return "en"
    return fallback


def _translation_succeeded(original: str, translated: str, target_language: str) -> bool:
    if not translated.strip():
        return False
    if translated.strip() == original.strip():
        return False
    target = detect_language(translated, target_language)
    return target == target_language


def _chunk_text(text: str, size: int = CHUNK_SIZE) -> list[str]:
    if len(text) <= size:
        return [text]

    paragraphs = re.split(r"\n{2,}", text)
    chunks: list[str] = []
    buffer = ""

    for paragraph in paragraphs:
        piece = paragraph.strip()
        if not piece:
            continue
        candidate = f"{buffer}\n\n{piece}".strip() if buffer else piece
        if len(candidate) <= size:
            buffer = candidate
            continue
        if buffer:
            chunks.append(buffer)
        if len(piece) <= size:
            buffer = piece
        else:
            start = 0
            while start < len(piece):
                end = min(start + size, len(piece))
                if end < len(piece):
                    split_at = piece.rfind(" ", start, end)
                    if split_at > start:
                        end = split_at
                segment = piece[start:end].strip()
                if segment:
                    chunks.append(segment)
                start = end if end > start else start + size
            buffer = ""

    if buffer:
        chunks.append(buffer)

    return chunks or [text]


async def translate_long_text(
    client: FanarLLMClient,
    text: str,
    *,
    target_language: str,
    source_language: str | None = None,
) -> str:
    """Translate long answers chunk-by-chunk via Fanar-Shaheen."""
    src = source_language or detect_language(text)
    if src == target_language:
        return text

    parts = _chunk_text(text)
    translated_parts: list[str] = []
    for index, part in enumerate(parts):
        translated = await client.translate_for_display(
            part,
            target_language=target_language,
            source_language=src,
        )
        if not _translation_succeeded(part, translated, target_language):
            logger.warning("Translation chunk %s language check failed; retrying", index)
            translated = await client.translate_for_display(
                part,
                target_language=target_language,
                source_language=src,
            )
        if not _translation_succeeded(part, translated, target_language):
            raise RuntimeError(f"Translation failed for chunk {index + 1}/{len(parts)}")
        translated_parts.append(translated.strip())

    return "\n\n".join(translated_parts)
