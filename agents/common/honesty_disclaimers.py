"""Honesty and uncertainty disclaimers appended to verified responses."""

from __future__ import annotations

from agents.knowledge_agent.models import EvidenceBundle
from agents.reasoning_agent.models import ReasoningResult, ScholarlyOpinion

QURAN_TYPES = {"quran", "classical"}
HADITH_TYPES = {"hadith"}


def _has_source_type(evidences, types: set[str]) -> bool:
    for item in evidences:
        st = (item.source_type or "").lower()
        if st in types or any(t in st for t in types):
            return True
    return False


def build_honesty_disclaimers(
    bundle: EvidenceBundle,
    reasoning: ReasoningResult,
    *,
    language: str = "en",
) -> list[str]:
    """Return user-facing honesty notes based on available evidence."""
    ar = language == "ar"
    notes: list[str] = []
    evidences = bundle.evidences or []
    opinions: list[ScholarlyOpinion] = reasoning.opinions or []

    if not _has_source_type(evidences, QURAN_TYPES):
        notes.append(
            "لا يوجد نص قرآني صريح مباشر في الأدلة المسترجعة لهذا السؤال."
            if ar
            else "There is no explicit Quranic verse directly cited in the retrieved evidence for this question."
        )

    if not _has_source_type(evidences, HADITH_TYPES):
        notes.append(
            "لم نعثر على حديث صريح وصحيح صريح في الأدلة المسترجعة."
            if ar
            else "We could not locate an explicit authentic hadith in the retrieved evidence."
        )

    if len(opinions) >= 2:
        positions = {o.position.strip().lower()[:80] for o in opinions if o.position}
        if len(positions) >= 2:
            notes.append(
                "هذه المسألة فيها خلاف بين العلماء — وُضحت آراء متعددة أدناه."
                if ar
                else "This issue remains an area of scholarly disagreement — multiple views are shown below."
            )

    if len(evidences) < 2 and not opinions:
        notes.append(
            "الأدلة المتاحة محدودة — يُفضّل مراجعة مصادر إضافية قبل اتخاذ قرار عملي."
            if ar
            else "Available evidence is limited — additional sources should be reviewed before practical decisions."
        )

    return notes[:3]


def append_honesty_to_reasoning(reasoning_text: str, disclaimers: list[str]) -> str:
    """Append honesty block to reasoning without altering summary."""
    if not disclaimers:
        return reasoning_text
    block = "\n".join(f"• {note}" for note in disclaimers)
    if reasoning_text.strip():
        return f"{reasoning_text.strip()}\n\n{block}"
    return block
