"""Ingestion pipeline: load → chunk → embed → store."""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.enums import SourceType
from rag.chunking.text_splitter import split_text
from rag.embeddings.embedding_generator import EmbeddingGenerator
from rag.ingestion.base import IngestedDocument
from rag.vectorstore.vector_store_manager import VectorStoreManager


class IngestionPipeline:
    """Orchestrates document ingestion into the vector store."""

    def __init__(
        self,
        session: AsyncSession,
        embedding_generator: EmbeddingGenerator | None = None,
    ) -> None:
        self.session = session
        self.embedding_generator = embedding_generator or EmbeddingGenerator()
        self.store = VectorStoreManager(session)

    async def ingest_document(
        self,
        document: IngestedDocument,
        source_type: SourceType,
        *,
        is_authenticated: bool = False,
        url: str | None = None,
        chunk_size: int = 800,
        chunk_overlap: int = 120,
    ) -> str:
        """Chunk, embed, and persist a document. Returns source ID."""
        chunks = split_text(
            document.content,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            metadata=document.metadata,
        )
        embeddings = await self.embedding_generator.embed_chunks(chunks)
        source_id = await self.store.upsert_source_with_chunks(
            title=document.source_title,
            author=document.source_author,
            source_type=source_type,
            language=document.language,
            chunks=chunks,
            embeddings=embeddings,
            url=url or document.metadata.get("url"),
            is_authenticated=is_authenticated,
        )
        return str(source_id)
