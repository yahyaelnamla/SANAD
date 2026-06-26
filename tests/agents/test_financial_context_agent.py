"""Unit tests for the Financial Context Agent."""

import pytest

from agents.financial_context_agent.agent import FinancialContextAgent
from agents.intent_agent.models import IntentResult, IntentType


@pytest.mark.asyncio
async def test_builds_context_for_crypto() -> None:
    intent = IntentResult(
        raw_query="Is Bitcoin halal?",
        intent_type=IntentType.SHARIAH_RULING,
        domain="cryptocurrency",
        language="en",
        entities=["crypto"],
    )
    agent = FinancialContextAgent()
    context = await agent.enrich(intent)

    assert context.entities == ["crypto"]
    assert len(context.products) == 1
    assert context.products[0].category == "digital_asset"
    assert not context.has_external_data
