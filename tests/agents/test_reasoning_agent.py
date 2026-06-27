"""Unit tests for the Reasoning Agent."""

import os

import pytest

from agents.common.evidence import EvidenceItem
from agents.financial_context_agent.models import FinancialContext
from agents.intent_agent.models import IntentResult, IntentType
from agents.knowledge_agent.models import EvidenceBundle, JurisprudentialPrinciple
from agents.reasoning_agent.agent import ReasoningAgent
from tests.helpers.fanar_stub import DeterministicFanarClient


@pytest.fixture
def reasoning_agent() -> ReasoningAgent:
    os.environ["FANAR_API_KEY"] = "test-key"
    return ReasoningAgent(llm_client=DeterministicFanarClient())


@pytest.mark.asyncio
async def test_reasoning_cites_evidence(reasoning_agent: ReasoningAgent) -> None:
    bundle = EvidenceBundle(
        evidences=[
            EvidenceItem(
                text="Riba is categorically prohibited.",
                source_id="s1",
                chunk_id="c1",
                citation="Scholars. Majallah.",
                source_title="Majallah",
                source_author="Scholars",
                source_type="classical",
                language="en",
            )
        ],
        principles=[
            JurisprudentialPrinciple(
                name="Prohibition of Riba",
                description="No guaranteed increase on loans.",
                citation="Scholars. Majallah.",
            )
        ],
    )
    intent = IntentResult(
        raw_query="Is riba haram?",
        intent_type=IntentType.SHARIAH_RULING,
        domain="islamic_finance",
        language="en",
        entities=["riba"],
    )
    context = FinancialContext(entities=["riba"])

    result = await reasoning_agent.analyze(bundle, context, intent)
    assert result.citations
    assert result.confidence > 0
    assert "Prohibition of Riba" in result.principles_applied
