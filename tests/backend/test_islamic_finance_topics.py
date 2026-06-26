"""Tests for Islamic finance topic enrichment."""

from agents.intent_agent.models import IntentResult, IntentType
from backend.app.services.islamic_finance_topics import (
    detect_islamic_finance_topics,
    enrich_retrieval_query,
)


def test_detect_crypto_topic() -> None:
    topics = detect_islamic_finance_topics("Is Bitcoin staking halal in DeFi?")
    assert "crypto" in topics or "defi" in topics


def test_enrich_retrieval_query_adds_domain_terms() -> None:
    intent = IntentResult(
        raw_query="AAOIFI screening for Tesla stock",
        intent_type=IntentType.COMPLIANCE_SCREENING,
        domain="islamic_finance",
        language="en",
        entities=["Tesla"],
        keywords=["stock", "screening"],
    )
    enriched = enrich_retrieval_query(intent)
    assert "Tesla" in enriched
    assert "AAOIFI" in enriched or "Shariah" in enriched
