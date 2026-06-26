"""Unit tests for the Verification Agent."""

import os

import pytest

from agents.common.evidence import EvidenceItem
from tests.helpers.fanar_stub import DeterministicFanarClient
from agents.knowledge_agent.models import EvidenceBundle
from agents.reasoning_agent.models import ReasoningResult, ScholarlyOpinion
from agents.verification_agent.agent import VerificationAgent


@pytest.fixture
def verification_agent() -> VerificationAgent:
    os.environ["FANAR_API_KEY"] = "test-key"
    return VerificationAgent(llm_client=DeterministicFanarClient())


def _bundle() -> EvidenceBundle:
    return EvidenceBundle(
        evidences=[
            EvidenceItem(
                text="Riba is prohibited.",
                source_id="s1",
                chunk_id="c1",
                citation="Scholars. Majallah.",
                source_title="Majallah",
                source_author="Scholars",
                source_type="classical",
                language="en",
            )
        ]
    )


@pytest.mark.asyncio
async def test_approves_valid_reasoning(verification_agent: VerificationAgent) -> None:
    reasoning = ReasoningResult(
        analysis="Riba is prohibited based on authenticated evidence.",
        citations=["Scholars. Majallah."],
        confidence=0.9,
        opinions=[
            ScholarlyOpinion(
                scholar="Scholars",
                position="Riba is haram.",
                citations=["Scholars. Majallah."],
            )
        ],
    )
    result = await verification_agent.verify(reasoning, _bundle())
    assert result.approved


@pytest.mark.asyncio
async def test_rejects_missing_citations(verification_agent: VerificationAgent) -> None:
    reasoning = ReasoningResult(
        analysis="Riba is prohibited.",
        citations=[],
        confidence=0.9,
    )
    result = await verification_agent.verify(reasoning, _bundle())
    assert not result.approved
    assert any(i.code == "MISSING_CITATIONS" for i in result.issues)
