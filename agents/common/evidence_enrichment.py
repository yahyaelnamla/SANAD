"""Evidence enrichment — ensure quotable text, not bare references."""

from __future__ import annotations

import re

from agents.common.evidence import EvidenceItem

MAX_EVIDENCE_CHARS = 600
MIN_SUBSTANTIVE_CHARS = 12

_BARE_REFERENCE = re.compile(
    r"^(\[\d+\]|\d+:\d+|surah\s+\d+|s\d+\s*v\d+|quran\s+\d+|hadith\s+\d+)\.?$",
    re.IGNORECASE,
)
_REFERENCE_ONLY = re.compile(r"^[\[\]\d\s:.,\-–—]+$")


def is_bare_reference(text: str) -> bool:
    """Detect citations without substantive quoted content."""
    cleaned = text.strip()
    if not cleaned:
        return True
    if len(cleaned) < MIN_SUBSTANTIVE_CHARS:
        return True
    if _BARE_REFERENCE.match(cleaned):
        return True
    if _REFERENCE_ONLY.match(cleaned):
        return True
    if cleaned.startswith("[") and cleaned.endswith("]") and len(cleaned) < 40:
        return True
    return False


def enrich_evidence_item(item: EvidenceItem) -> EvidenceItem | None:
    """Normalize evidence text — drop bare refs, truncate long dumps."""
    text = item.text.strip()
    if not text or is_bare_reference(text):
        return None

    if len(text) > MAX_EVIDENCE_CHARS:
        truncated = text[:MAX_EVIDENCE_CHARS].rsplit(" ", 1)[0].strip()
        text = f"{truncated}…" if truncated else text[:MAX_EVIDENCE_CHARS].strip() + "…"

    citation = item.citation.strip()
    if is_bare_reference(citation) and not is_bare_reference(text):
        citation = text[:120].strip()
        if len(text) > 120:
            citation += "…"

    return item.model_copy(update={"text": text, "citation": citation})


def enrich_evidence_list(items: list[EvidenceItem]) -> list[EvidenceItem]:
    """Filter and enrich a list of evidence items."""
    enriched: list[EvidenceItem] = []
    seen: set[str] = set()
    for item in items:
        processed = enrich_evidence_item(item)
        if processed is None:
            continue
        key = processed.text[:160].lower()
        if key in seen:
            continue
        seen.add(key)
        enriched.append(processed)
    return enriched
