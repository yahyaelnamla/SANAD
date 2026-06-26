"""Classify Islamic evidence into Quran, Hadith, Fatwa, Fiqh, or Standard."""

import re


def classify_evidence_kind(text: str, citation: str = "", source_type: str = "") -> str:
    """Return evidence kind label for UI badges and confidence weighting."""
    combined = f"{text} {citation} {source_type}".lower()

    quran_markers = (
        "quran",
        "qur'an",
        "surah",
        "sura",
        "ayah",
        "verse",
        "سورة",
        "آية",
        "قرآن",
        "القرآن",
    )
    hadith_markers = (
        "hadith",
        "hadeeth",
        "prophet",
        "narrated",
        "bukhari",
        "muslim",
        "tirmidhi",
        "حديث",
        "رسول",
        "رواه",
    )
    fatwa_markers = (
        "fatwa",
        "فتوى",
        "islamqa",
        "islamweb",
        "fiqh council",
        "dar al-ifta",
        "ifta",
    )

    if any(marker in combined for marker in quran_markers):
        return "quran"
    if any(marker in combined for marker in hadith_markers):
        return "hadith"
    if source_type == "fatwa" or any(marker in combined for marker in fatwa_markers):
        return "fatwa"
    if source_type in {"classical", "contemporary", "fanar_sadiq"}:
        return "fiqh"
    if source_type == "standard":
        return "standard"
    return "fiqh"


def enrich_citation_label(kind: str, citation: str, text: str) -> str:
    """Build a human-readable citation when Fanar returns bare reference numbers."""
    if citation and not re.fullmatch(r"\[\d+\]", citation.strip()) and len(citation) > 4:
        return citation

    preview = " ".join(text.split()[:12])
    if len(text.split()) > 12:
        preview += "…"

    labels = {
        "quran": "Quranic Evidence",
        "hadith": "Prophetic Hadith",
        "fatwa": "Scholarly Fatwa",
        "fiqh": "Fiqh Reference",
        "standard": "Shariah Standard",
    }
    label = labels.get(kind, "Islamic Reference")
    if preview:
        return f"{label}: {preview}"
    return label
