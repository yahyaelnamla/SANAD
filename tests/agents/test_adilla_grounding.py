"""Tests for adilla grounding normalization."""

from agents.common.evidence import EvidenceItem
from agents.knowledge_agent.models import EvidenceBundle
from agents.reasoning_agent.models import ReasoningResult
from agents.verification_agent.tools import (
    check_hallucination_risk,
    is_generic_adilla_label,
    normalize_adilla_from_evidence,
)


def test_generic_adilla_labels_skipped() -> None:
    assert is_generic_adilla_label("Quran")
    assert is_generic_adilla_label("Hadith")
    assert is_generic_adilla_label("Consensus")
    assert not is_generic_adilla_label("Surah Al-Baqarah 2:275")


def test_normalize_adilla_replaces_generic_with_citations() -> None:
    bundle = EvidenceBundle(
        evidences=[
            EvidenceItem(
                text="Riba is prohibited.",
                source_id="s1",
                chunk_id="c1",
                citation="Quran 2:275",
                source_title="Quran",
                source_author="Allah",
                source_type="quran",
                language="en",
            )
        ]
    )
    result = normalize_adilla_from_evidence(["Quran", "Hadith", "Consensus"], bundle)
    assert "Quran 2:275" in result
    assert "Quran" not in result or result == ["Quran 2:275"]


def test_hallucination_check_ignores_generic_adilla_only() -> None:
    bundle = EvidenceBundle(
        evidences=[
            EvidenceItem(
                text="Riba is prohibited.",
                source_id="s1",
                chunk_id="c1",
                citation="Quran 2:275",
                source_title="Quran",
                source_author="Allah",
                source_type="quran",
                language="en",
            )
        ]
    )
    reasoning = ReasoningResult(
        analysis="Riba is haram.",
        adilla=["Quran", "Hadith", "Consensus"],
        citations=["Quran 2:275"],
        confidence=0.9,
    )
    issues = check_hallucination_risk(reasoning, bundle)
    assert issues == []
