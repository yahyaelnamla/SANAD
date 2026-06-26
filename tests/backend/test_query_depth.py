"""Tests for adaptive query depth routing."""

from backend.app.services.query_depth import (
    classify_query_depth,
    is_document_question,
    plan_for_depth,
)


def test_simple_question_uses_fast_path() -> None:
    assert classify_query_depth("Is riba haram?") == "fast"
    assert classify_query_depth("What is zakat?") == "fast"


def test_complex_question_uses_deep_path() -> None:
    assert classify_query_depth("Compare Hanafi and Shafii opinions on Bitcoin staking rewards") == "deep"
    assert (
        classify_query_depth(
            "Analyze the murabaha structure versus conventional mortgage with AAOIFI screening"
        )
        == "deep"
    )


def test_document_question_detection() -> None:
    assert is_document_question("What did my annual report mention about debt?")
    assert is_document_question("Summarize chapter 3 of the uploaded PDF")
    assert not is_document_question("Is riba haram?")


def test_plan_for_depth_steps() -> None:
    fast = plan_for_depth("fast")
    assert "financial" not in fast["steps"]
    assert "reasoning" in fast["steps"]

    deep = plan_for_depth("deep")
    assert "financial" in deep["steps"]
    assert "reasoning" in deep["steps"]
