"""Main RAG pipeline orchestrator."""

from sqlalchemy.ext.asyncio import AsyncSession

from agents.common.fanar_client import FanarLLMClient
from backend.app.models.enums import SourceType
from rag.ingestion.base import IngestedDocument
from rag.pipelines.ingestion_pipeline import IngestionPipeline
from rag.pipelines.retrieval_pipeline import RetrievalPipeline, RetrievalResult


class MainRAGPipeline:
    """End-to-end RAG pipeline for ingestion and retrieval."""

    def __init__(
        self,
        session: AsyncSession,
        fanar_client: FanarLLMClient | None = None,
    ) -> None:
        self.fanar = fanar_client
        self.ingestion = IngestionPipeline(session)
        self.retrieval = RetrievalPipeline(session, fanar_client=fanar_client)

    async def ingest(
        self,
        document: IngestedDocument,
        source_type: SourceType,
        *,
        is_authenticated: bool = False,
        url: str | None = None,
    ) -> str:
        """Ingest a document into the knowledge base."""
        return await self.ingestion.ingest_document(
            document,
            source_type,
            is_authenticated=is_authenticated,
            url=url,
        )

    async def retrieve(
        self,
        query: str,
        *,
        top_k: int = 5,
        language: str | None = None,
    ) -> RetrievalResult:
        """Retrieve authenticated evidence for a query."""
        return await self.retrieval.retrieve(query, top_k=top_k, language=language)
