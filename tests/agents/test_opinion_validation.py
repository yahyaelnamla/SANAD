"""Unit tests for scholarly opinion validation."""

from agents.common.evidence import EvidenceItem
from agents.common.opinion_validation import validate_and_ground_opinions
from agents.knowledge_agent.models import EvidenceBundle
from agents.reasoning_agent.models import ScholarlyOpinion


def _evidence(**kwargs: object) -> EvidenceItem:
    defaults = {
        "text": "Allah has permitted trade and forbidden usury (riba).",
        "source_id": "s1",
        "chunk_id": "c1",
        "citation": "Quran 2:275",
        "source_title": "Quran",
        "source_author": "Allah",
        "source_type": "quran",
        "language": "en",
        "score": 0.95,
        "metadata": {"section": "Al-Baqarah"},
    }
    defaults.update(kwargs)
    return EvidenceItem(**defaults)  # type: ignore[arg-type]


def test_grounded_opinion_keeps_evidence_wording() -> None:
    bundle = EvidenceBundle(evidences=[_evidence()])
    opinions = [
        ScholarlyOpinion(
            scholar="Allah",
            position="Trade is permitted.",
            citations=["Quran 2:275"],
        )
    ]
    result = validate_and_ground_opinions(opinions, bundle)
    assert len(result) == 1
    assert "trade" in result[0].position.lower() or "usury" in result[0].position.lower()
    assert result[0].section == "Al-Baqarah"


def test_hallucinated_opinion_dropped() -> None:
    bundle = EvidenceBundle(evidences=[_evidence()])
    opinions = [
        ScholarlyOpinion(
            scholar="Unknown Scholar",
            position="Bitcoin is universally halal without conditions.",
            citations=["Made up ref 999"],
        )
    ]
    result = validate_and_ground_opinions(opinions, bundle)
    assert len(result) == 1
    assert result[0].scholar in {"Allah", "Quran"}


def test_fallback_from_evidence_when_no_opinions() -> None:
    bundle = EvidenceBundle(
        evidences=[
            _evidence(
                text="Riba is categorically prohibited in Islam according to consensus.",
                citation="Scholars consensus",
                source_author="Classical jurists",
                source_title="Majallah",
                source_type="classical",
            )
        ]
    )
    result = validate_and_ground_opinions([], bundle)
    assert len(result) >= 1
    assert "prohibited" in result[0].position.lower()
