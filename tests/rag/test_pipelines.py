"""Integration tests for RAG ingestion and retrieval pipelines."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.enums import SourceType
from backend.app.rag.rag_connector import RAGConnector
from backend.app.rag.rag_schemas import RAGIngestRequest, RAGRetrieveRequest
from rag.ingestion.base import IngestedDocument
from rag.pipelines.main_rag_pipeline import MainRAGPipeline

AUTHENTICATED_RIBA_TEXT = (
    "Riba (usury) is categorically prohibited in Islamic law. "
    "Classical jurists from all major madhabs agree that any guaranteed increase "
    "on a loan constitutes riba. Source: Majallah al-Ahkam al-Adliyyah."
)


@pytest.mark.asyncio
async def test_ingestion_pipeline_stores_embedded_chunks(db_session: AsyncSession) -> None:
    pipeline = MainRAGPipeline(db_session)
    document = IngestedDocument(
        content=AUTHENTICATED_RIBA_TEXT,
        source_title="Majallah al-Ahkam",
        source_author="Ottoman Scholars",
        language="en",
    )
    source_id = await pipeline.ingest(
        document,
        SourceType.CLASSICAL,
        is_authenticated=True,
    )
    assert source_id


@pytest.mark.asyncio
async def test_retrieval_returns_cited_evidence(db_session: AsyncSession) -> None:
    pipeline = MainRAGPipeline(db_session)
    document = IngestedDocument(
        content=AUTHENTICATED_RIBA_TEXT,
        source_title="Majallah al-Ahkam",
        source_author="Ottoman Scholars",
        language="en",
    )
    await pipeline.ingest(document, SourceType.CLASSICAL, is_authenticated=True)

    result = await pipeline.retrieve("Is riba prohibited?", top_k=3, language="en")
    assert result.has_evidence
    assert not result.refused
    assert result.chunks[0].citation
    assert result.chunks[0].source_author == "Ottoman Scholars"
    evidence = result.to_evidence_list()
    assert evidence[0]["citation"]
    assert evidence[0]["source_id"]


@pytest.mark.asyncio
async def test_retrieval_refuses_without_authenticated_sources(db_session: AsyncSession) -> None:
    pipeline = MainRAGPipeline(db_session)
    document = IngestedDocument(
        content="Unverified opinion about crypto trading without citations.",
        source_title="Random Blog",
        source_author="Unknown",
        language="en",
    )
    await pipeline.ingest(document, SourceType.CONTEMPORARY, is_authenticated=False)

    result = await pipeline.retrieve("Is crypto halal?", language="en")
    assert result.refused
    assert not result.has_evidence
    assert result.reason is not None
    assert "authenticated" in result.reason.lower()


@pytest.mark.asyncio
async def test_rag_connector_retrieve_response(db_session: AsyncSession) -> None:
    connector = RAGConnector(db_session)
    await connector.ingest(
        RAGIngestRequest(
            content=AUTHENTICATED_RIBA_TEXT,
            source_title="Majallah al-Ahkam",
            source_author="Ottoman Scholars",
            source_type="classical",
            language="en",
            is_authenticated=True,
        )
    )
    response = await connector.retrieve(
        RAGRetrieveRequest(query="riba prohibition in Islam", language="en")
    )
    assert response.has_evidence
    assert response.evidence[0].citation
