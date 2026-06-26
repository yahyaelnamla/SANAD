"""Unit tests for the Intent Agent."""

import os

import pytest

from agents.intent_agent.agent import IntentAgent
from agents.intent_agent.models import IntentType
from tests.helpers.fanar_stub import DeterministicFanarClient


@pytest.fixture
def intent_agent() -> IntentAgent:
    os.environ["FANAR_API_KEY"] = "test-key"
    return IntentAgent(llm_client=DeterministicFanarClient())


@pytest.mark.asyncio
async def test_detects_riba_intent(intent_agent: IntentAgent) -> None:
    result = await intent_agent.analyze("Is riba prohibited in Islam?")
    assert result.intent_type == IntentType.SHARIAH_RULING
    assert "riba" in result.entities
    assert result.language == "en"


@pytest.mark.asyncio
async def test_detects_arabic_query(intent_agent: IntentAgent) -> None:
    result = await intent_agent.analyze("هل الربا حرام في الإسلام؟")
    assert result.language == "ar"
    assert result.intent_type == IntentType.SHARIAH_RULING


@pytest.mark.asyncio
async def test_extracts_crypto_entity(intent_agent: IntentAgent) -> None:
    result = await intent_agent.analyze("Is Bitcoin halal for investment?")
    assert "crypto" in result.entities
