"""Integration tests for the multi-agent pipeline."""

import os

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.agents.agent_orchestrator import AgentOrchestrator
from backend.app.models.enums import SourceType
from rag.embeddings.embedding_generator import EmbeddingGenerator
from rag.pipelines.ingestion_pipeline import IngestionPipeline
from tests.helpers.embedding_stub import DeterministicEmbeddingModel
from tests.helpers.fanar_stub import DeterministicFanarClient
from rag.ingestion.base import IngestedDocument
from rag.pipelines.main_rag_pipeline import MainRAGPipeline

RIBA_TEXT = (
    "Riba (usury) is categorically prohibited in Islamic law. "
    "Classical jurists from all major madhabs agree that any guaranteed increase "
    "on a loan constitutes riba. Source: Majallah al-Ahkam al-Adliyyah."
)


@pytest.fixture
def orchestrator(db_session: AsyncSession) -> AgentOrchestrator:
    os.environ["FANAR_API_KEY"] = "test-key"
    llm = DeterministicFanarClient()
    orch = AgentOrchestrator(db_session, llm_client=llm)
    orch.retrieval_agent.pipeline.embedding_generator = EmbeddingGenerator(
        DeterministicEmbeddingModel()
    )
    return orch


@pytest.mark.asyncio
async def test_full_pipeline_with_evidence(
    db_session: AsyncSession,
    orchestrator: AgentOrchestrator,
) -> None:
    pipeline = MainRAGPipeline(db_session)
    pipeline.ingestion = IngestionPipeline(
        db_session,
        EmbeddingGenerator(DeterministicEmbeddingModel()),
    )
    await pipeline.ingest(
        IngestedDocument(
            content=RIBA_TEXT,
            source_title="Majallah al-Ahkam",
            source_author="Ottoman Scholars",
            language="en",
        ),
        SourceType.CLASSICAL,
        is_authenticated=True,
    )

    response = await orchestrator.process_query("Is riba prohibited in Islam?")

    assert not response.refused
    assert response.confidence > 0
    assert response.evidence
    assert response.evidence[0].citation
    assert response.principles
    assert response.reasoning
    assert response.sources


@pytest.mark.asyncio
async def test_pipeline_refuses_without_evidence(
    orchestrator: AgentOrchestrator,
) -> None:
    response = await orchestrator.process_query("Is quantum trading halal?")

    assert response.refused
    assert response.confidence == 0.0
    assert response.refusal_reason is not None
