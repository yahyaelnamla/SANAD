"""Tests for conversation memory and follow-up resolution."""

from backend.app.services.conversation_memory_service import (
    is_follow_up_question,
    resolve_query_with_context,
)


def test_is_follow_up_detects_short_why():
    assert is_follow_up_question("Why?")
    assert is_follow_up_question("What about Nvidia?")


def test_is_follow_up_rejects_long_question():
    text = "Compare Hanafi and Maliki opinions on Bitcoin staking rewards in detail"
    assert not is_follow_up_question(text)


def test_resolve_query_with_context_expands_follow_up():
    history = [
        {"role": "user", "content": "Is Tesla halal?"},
        {
            "role": "assistant",
            "content": "Tesla requires screening for debt and interest income ratios.",
        },
    ]
    expanded = resolve_query_with_context("Why?", history)
    assert "Follow-up" in expanded
    assert "Tesla" in expanded or "screening" in expanded
