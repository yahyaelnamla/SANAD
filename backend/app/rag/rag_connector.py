"""Backend connector to the SANAD RAG pipeline."""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from agents.common.fanar_client import FanarLLMClient
from backend.app.models.enums import SourceType
from backend.app.rag.rag_schemas import (
    RAGEvidenceItem,
    RAGIngestRequest,
    RAGIngestResponse,
    RAGRetrieveRequest,
    RAGRetrieveResponse,
)
from rag.ingestion.base import IngestedDocument
from rag.pipelines.main_rag_pipeline import MainRAGPipeline

logger = logging.getLogger(__name__)


class RAGConnector:
    """Interface between FastAPI backend services and the RAG pipeline."""

    def __init__(
        self,
        session: AsyncSession,
        fanar_client: FanarLLMClient | None = None,
    ) -> None:
        self.pipeline = MainRAGPipeline(session, fanar_client=fanar_client)

    async def ingest(self, request: RAGIngestRequest) -> RAGIngestResponse:
        """Ingest content into the vector store."""
        try:
            document = IngestedDocument(
                content=request.content,
                source_title=request.source_title,
                source_author=request.source_author,
                language=request.language,
                metadata=request.metadata,
            )
            source_type = SourceType(request.source_type)
            source_id = await self.pipeline.ingest(
                document,
                source_type,
                is_authenticated=request.is_authenticated,
                url=request.url,
            )
            return RAGIngestResponse(source_id=source_id)
        except Exception as exc:
            logger.error("RAGConnector.ingest failed: %s", exc, exc_info=True)
            raise

    async def retrieve(self, request: RAGRetrieveRequest) -> RAGRetrieveResponse:
        """Retrieve authenticated evidence for a query."""
        try:
            result = await self.pipeline.retrieve(
                request.query,
                top_k=request.top_k,
                language=request.language,
            )
            evidence = [
                RAGEvidenceItem(**item)
                for item in result.to_evidence_list()
            ]
            return RAGRetrieveResponse(
                query=result.query,
                refused=result.refused,
                reason=result.reason,
                evidence=evidence,
            )
        except Exception as exc:
            logger.error("RAGConnector.retrieve failed: %s", exc, exc_info=True)
            raise
