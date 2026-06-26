"""Unit tests for Reasoning Agent tools."""

from agents.reasoning_agent.tools import normalize_citations


def test_normalize_citations_from_string_ref() -> None:
    assert normalize_citations("[1]") == ["[1]"]


def test_normalize_citations_from_json_string() -> None:
    assert normalize_citations('["Scholars. Majallah.", "AAOIFI Standard 21"]') == [
        "Scholars. Majallah.",
        "AAOIFI Standard 21",
    ]


def test_normalize_citations_from_list() -> None:
    assert normalize_citations(["citation-a", "citation-b"]) == ["citation-a", "citation-b"]


def test_normalize_citations_empty() -> None:
    assert normalize_citations(None) == []
    assert normalize_citations("") == []
