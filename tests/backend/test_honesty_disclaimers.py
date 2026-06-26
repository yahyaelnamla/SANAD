"""Tests for Phase 1 honesty disclaimer helpers."""

from agents.common.evidence import EvidenceItem
from agents.common.honesty_disclaimers import append_honesty_to_reasoning, build_honesty_disclaimers
from agents.knowledge_agent.models import EvidenceBundle
from agents.reasoning_agent.models import ReasoningResult, ScholarlyOpinion


def _evidence(source_type: str) -> EvidenceItem:
    return EvidenceItem(
        text="sample",
        source_id="s1",
        chunk_id="c1",
        citation="cite",
        source_title="title",
        source_author="author",
        source_type=source_type,
        language="en",
        score=0.9,
    )


def test_honesty_notes_missing_quran_and_hadith() -> None:
    bundle = EvidenceBundle(evidences=[_evidence("fatwa")])
    reasoning = ReasoningResult(analysis="test", confidence=0.5, opinions=[])
    notes = build_honesty_disclaimers(bundle, reasoning, language="en")
    assert any("Quranic" in note for note in notes)
    assert any("hadith" in note for note in notes)


def test_honesty_notes_disagreement() -> None:
    bundle = EvidenceBundle(evidences=[_evidence("quran"), _evidence("hadith")])
    reasoning = ReasoningResult(
        analysis="test",
        confidence=0.7,
        opinions=[
            ScholarlyOpinion(scholar="A", position="Permitted", citations=[]),
            ScholarlyOpinion(scholar="B", position="Prohibited", citations=[]),
        ],
    )
    notes = build_honesty_disclaimers(bundle, reasoning, language="en")
    assert any("disagreement" in note for note in notes)


def test_append_honesty_to_reasoning() -> None:
    merged = append_honesty_to_reasoning("Summary line.", ["Limited evidence."])
    assert "Summary line." in merged
    assert "Limited evidence." in merged
