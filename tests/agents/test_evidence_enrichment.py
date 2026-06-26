"""Tests for evidence enrichment."""

from agents.common.evidence import EvidenceItem
from agents.common.evidence_enrichment import enrich_evidence_list, is_bare_reference


def _item(text: str) -> EvidenceItem:
    return EvidenceItem(
        text=text,
        source_id="s1",
        chunk_id="c1",
        citation="Test",
        source_title="Source",
        source_author="Author",
        source_type="quran",
        language="en",
        score=0.9,
    )


def test_bare_reference_detected():
    assert is_bare_reference("[2]")
    assert is_bare_reference("2:275")


def test_enrich_filters_bare_references():
    items = enrich_evidence_list([_item("[1]"), _item("Allah has permitted trade and forbidden usury.")])
    assert len(items) == 1
    assert "Allah" in items[0].text


def test_enrich_truncates_long_text():
    long_text = "word " * 200
    items = enrich_evidence_list([_item(long_text.strip())])
    assert len(items[0].text) <= 602
