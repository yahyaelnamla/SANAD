"""Unit tests for the Knowledge Agent."""

import os

import pytest

from agents.common.evidence import EvidenceItem
from agents.intent_agent.models import IntentResult, IntentType
from agents.knowledge_agent.agent import KnowledgeAgent
from agents.retrieval_agent.models import RetrievalAgentResult
from tests.helpers.fanar_stub import DeterministicFanarClient


@pytest.fixture
def knowledge_agent() -> KnowledgeAgent:
    os.environ["FANAR_API_KEY"] = "test-key"
    return KnowledgeAgent(llm_client=DeterministicFanarClient())


def _sample_evidence() -> EvidenceItem:
    return EvidenceItem(
        text="Riba is prohibited in Islamic law.",
        source_id="src-1",
        chunk_id="chunk-1",
        citation="Ottoman Scholars. Majallah al-Ahkam.",
        source_title="Majallah al-Ahkam",
        source_author="Ottoman Scholars",
        source_type="classical",
        language="en",
        score=0.9,
        metadata={"is_authenticated": True},
    )


@pytest.mark.asyncio
async def test_assembles_valid_evidence_bundle(knowledge_agent: KnowledgeAgent) -> None:
    retrieval = RetrievalAgentResult(
        query="Is riba prohibited?",
        chunks=[_sample_evidence()],
    )
    intent = IntentResult(
        raw_query="Is riba prohibited?",
        intent_type=IntentType.SHARIAH_RULING,
        domain="islamic_finance",
        language="en",
        entities=["riba"],
    )
    bundle = await knowledge_agent.assemble(retrieval, intent)

    assert bundle.has_valid_evidence
    assert len(bundle.principles) >= 1
    assert bundle.principles[0].name == "Prohibition of Riba"


@pytest.mark.asyncio
async def test_rejects_invalid_evidence(knowledge_agent: KnowledgeAgent) -> None:
    bad = _sample_evidence()
    bad.citation = ""
    retrieval = RetrievalAgentResult(query="test", chunks=[bad])
    intent = IntentResult(
        raw_query="test",
        intent_type=IntentType.GENERAL_INQUIRY,
        domain="islamic_finance",
        language="en",
    )
    bundle = await knowledge_agent.assemble(retrieval, intent)
    assert not bundle.has_valid_evidence
    assert bundle.rejected_count == 1
