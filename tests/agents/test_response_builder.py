"""Unit tests for the Response Builder."""

import os

import pytest

from agents.common.evidence import EvidenceItem
from tests.helpers.fanar_stub import DeterministicFanarClient
from agents.intent_agent.models import IntentResult, IntentType
from agents.knowledge_agent.models import EvidenceBundle, JurisprudentialPrinciple
from agents.reasoning_agent.models import ReasoningResult, ScholarlyOpinion
from agents.response_builder.agent import ResponseBuilder
from agents.response_builder.tools import build_final_response, sanitize_user_text


@pytest.fixture
def response_builder() -> ResponseBuilder:
    os.environ["FANAR_API_KEY"] = "test-key"
    return ResponseBuilder(llm_client=DeterministicFanarClient())


@pytest.mark.asyncio
async def test_builds_explainability_chain(response_builder: ResponseBuilder) -> None:
    bundle = EvidenceBundle(
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
        ],
        principles=[
            JurisprudentialPrinciple(
                name="Prohibition of Riba",
                description="No guaranteed increase.",
                citation="Scholars. Majallah.",
            )
        ],
    )
    reasoning = ReasoningResult(
        principles_applied=["Prohibition of Riba"],
        reasoning_steps=["Step 1: Review evidence."],
        analysis="Riba is categorically prohibited.",
        opinions=[
            ScholarlyOpinion(
                scholar="Scholars",
                position="Prohibited.",
                citations=["Scholars. Majallah."],
            )
        ],
        confidence=0.92,
        citations=["Scholars. Majallah."],
    )
    intent = IntentResult(
        raw_query="Is riba haram?",
        intent_type=IntentType.SHARIAH_RULING,
        domain="islamic_finance",
        language="en",
    )

    response = await response_builder.build(bundle, reasoning, intent)
    assert response.summary
    assert response.evidence
    assert response.principles
    assert response.reasoning
    assert response.confidence == 0.92
    assert not response.refused
    assert response.thinking_trace is None


def test_dedupes_duplicate_evidence_and_opinions() -> None:
    bundle = EvidenceBundle(
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
            ),
            EvidenceItem(
                text="Riba is prohibited.",
                source_id="s1",
                chunk_id="c1",
                citation="Scholars. Majallah.",
                source_title="Majallah",
                source_author="Scholars",
                source_type="classical",
                language="en",
            ),
        ],
        principles=[
            JurisprudentialPrinciple(
                name="Prohibition of Riba",
                description="No guaranteed increase.",
                citation="Scholars. Majallah.",
            ),
            JurisprudentialPrinciple(
                name="Prohibition of Riba",
                description="Duplicate principle.",
                citation="Scholars. Majallah.",
            ),
        ],
    )
    reasoning = ReasoningResult(
        analysis="Riba is categorically prohibited in Islamic law.",
        reasoning_steps=[
            "Reviewed authenticated evidence on riba.",
            "Reviewed authenticated evidence on riba.",
        ],
        opinions=[
            ScholarlyOpinion(
                scholar="Classical Consensus",
                position="Riba is haram.",
                citations=["Scholars. Majallah."],
            ),
            ScholarlyOpinion(
                scholar="Classical Consensus",
                position="Riba is haram.",
                citations=["Scholars. Majallah."],
            ),
        ],
        confidence=0.9,
        citations=["Scholars. Majallah."],
    )

    response = build_final_response(
        bundle=bundle,
        reasoning=reasoning,
        language="en",
        summary="Riba is categorically prohibited in Islamic law.",
    )

    assert len(response.evidence) == 1
    assert len(response.principles) == 1
    assert len(response.opinions) == 1
    assert response.summary.count("Riba is categorically prohibited") == 1
    assert "Reviewed authenticated evidence on riba." in response.reasoning
    assert response.reasoning.count("Reviewed authenticated evidence on riba.") == 1


def test_sanitize_user_text_strips_thinking_and_json() -> None:
    cleaned = sanitize_user_text(
        '<thinking>internal</thinking>{"summary":"Riba is prohibited."}'
    )
    assert cleaned == "Riba is prohibited."
    assert "<thinking>" not in cleaned
