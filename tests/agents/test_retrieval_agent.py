"""Unit tests for the Retrieval Agent."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from agents.intent_agent.models import IntentResult, IntentType
from agents.retrieval_agent.agent import RetrievalAgent
from backend.app.models.enums import SourceType
from rag.embeddings.embedding_generator import EmbeddingGenerator
from rag.ingestion.base import IngestedDocument
from rag.pipelines.ingestion_pipeline import IngestionPipeline
from rag.pipelines.main_rag_pipeline import MainRAGPipeline
from rag.pipelines.retrieval_pipeline import RetrievalPipeline
from tests.helpers.embedding_stub import DeterministicEmbeddingModel
from tests.helpers.fanar_stub import DeterministicFanarClient

RIBA_TEXT = (
    "Riba (usury) is categorically prohibited in Islamic law. "
    "Classical jurists agree. Source: Majallah al-Ahkam al-Adliyyah."
)


def _retrieval_agent(session: AsyncSession) -> RetrievalAgent:
    fanar = DeterministicFanarClient()
    pipeline = RetrievalPipeline(
        session,
        fanar_client=fanar,
        embedding_generator=EmbeddingGenerator(DeterministicEmbeddingModel()),
    )
    return RetrievalAgent(session, pipeline=pipeline, fanar_client=fanar)


@pytest.mark.asyncio
async def test_retrieval_returns_authenticated_evidence(db_session: AsyncSession) -> None:
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

    intent = IntentResult(
        raw_query="Is riba prohibited?",
        intent_type=IntentType.SHARIAH_RULING,
        domain="islamic_finance",
        language="en",
        entities=["riba"],
        keywords=["riba", "prohibition"],
    )
    agent = _retrieval_agent(db_session)
    result = await agent.retrieve(intent)

    assert result.has_evidence
    assert result.chunks[0].citation
    assert not result.refused


@pytest.mark.asyncio
async def test_retrieval_refuses_without_evidence(db_session: AsyncSession) -> None:
    intent = IntentResult(
        raw_query="Is crypto halal?",
        intent_type=IntentType.SHARIAH_RULING,
        domain="islamic_finance",
        language="en",
        entities=["crypto"],
    )
    agent = _retrieval_agent(db_session)
    result = await agent.retrieve(intent)

    assert result.refused
    assert not result.has_evidence
