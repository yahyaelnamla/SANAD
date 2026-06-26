"""Retrieval pipeline: Fanar-Sadiq RAG + optional local hybrid search."""

import hashlib
import logging
import uuid as _uuid
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from agents.common.fanar_client import FanarLLMClient
from rag.embeddings.embedding_generator import EmbeddingGenerator
from rag.rerankers.cross_encoder_reranker import CrossEncoderReranker
from rag.rerankers.diversity_reranker import DiversityReranker
from rag.retrievers.base import RetrievedChunk
from rag.retrievers.hybrid_retriever import HybridRetriever
from rag.retrievers.metadata_filter import MetadataFilter

logger = logging.getLogger(__name__)


def _stable_uuid(text: str) -> _uuid.UUID:
    """Generate a deterministic UUID-v5 from text content."""
    return _uuid.uuid5(_uuid.NAMESPACE_URL, f"fanar-sadiq:{text[:512]}")


@dataclass
class RetrievalResult:
    """Result of a RAG retrieval operation."""

    query: str
    chunks: list[RetrievedChunk] = field(default_factory=list)
    refused: bool = False
    reason: str | None = None
    retrieval_source: str = "hybrid"

    @property
    def has_evidence(self) -> bool:
        return bool(self.chunks) and not self.refused

    def to_evidence_list(self) -> list[dict[str, Any]]:
        """Convert retrieved chunks to evidence dicts for downstream agents."""
        return [chunk.to_evidence_dict() for chunk in self.chunks]


class RetrievalPipeline:
    """Retrieve authenticated evidence via Fanar-Sadiq RAG and local hybrid search."""

    NO_EVIDENCE_REASON = (
        "No authenticated sources found. The system refuses to answer without evidence."
    )

    def __init__(
        self,
        session: AsyncSession,
        embedding_generator: EmbeddingGenerator | None = None,
        fanar_client: FanarLLMClient | None = None,
    ) -> None:
        self.session = session
        self.embedding_generator = embedding_generator or EmbeddingGenerator()
        self.fanar = fanar_client or FanarLLMClient()
        self.retriever = HybridRetriever(session)
        self.cross_encoder = CrossEncoderReranker()
        self.diversity = DiversityReranker()
        self.metadata_filter = MetadataFilter(authenticated_only=True)

    async def retrieve(
        self,
        query: str,
        *,
        top_k: int = 5,
        language: str | None = None,
    ) -> RetrievalResult:
        """Retrieve, rerank, and filter evidence via Fanar-Sadiq RAG + local DB."""
        if not query.strip():
            return RetrievalResult(
                query=query,
                refused=True,
                reason="Empty query provided.",
            )

        fanar_chunks = await self._retrieve_fanar_sadiq(query, top_k=top_k, language=language)
        local_chunks = await self._retrieve_local(query, top_k=top_k, language=language)

        merged = self._merge_chunks(fanar_chunks, local_chunks, top_k=top_k, language=language)
        if not merged:
            return RetrievalResult(
                query=query,
                refused=True,
                reason=self.NO_EVIDENCE_REASON,
            )

        source = "fanar_sadiq" if fanar_chunks and not local_chunks else "hybrid"
        if fanar_chunks and local_chunks:
            source = "hybrid"
        elif fanar_chunks:
            source = "fanar_sadiq"

        return RetrievalResult(query=query, chunks=merged, retrieval_source=source)

    async def _retrieve_fanar_sadiq(
        self,
        query: str,
        *,
        top_k: int,
        language: str | None,
    ) -> list[RetrievedChunk]:
        """Call Fanar-Sadiq for grounded Islamic content retrieval."""
        try:
            references = await self.fanar.retrieve_knowledge(
                query,
                language=language,
                top_k=top_k,
            )
        except RuntimeError as exc:
            logger.warning("Fanar-Sadiq retrieval failed: %s", exc)
            return []

        chunks: list[RetrievedChunk] = []
        for ref in references:
            metadata = dict(ref.get("metadata") or {})
            text = ref.get("text", "")
            if not text.strip():
                continue
            if "verification_hash" not in metadata:
                metadata["verification_hash"] = hashlib.sha256(text.encode()).hexdigest()[:16]
            source = ref.get("source_title") or ref.get("source") or "Fanar-Sadiq"
            chunks.append(
                RetrievedChunk(
                    chunk_id=_stable_uuid(text),
                    source_id=_stable_uuid(str(source)),
                    content=text,
                    score=float(ref.get("score", 1.0)),
                    source_title=ref.get("source_title", "Fanar-Sadiq"),
                    source_author=ref.get("source_author", "Fanar-Sadiq"),
                    source_type=ref.get("source_type", "fanar_sadiq"),
                    language=ref.get("language", language or "ar"),
                    citation=ref.get("citation", "Fanar-Sadiq"),
                    metadata=metadata,
                )
            )
        return chunks

    async def _retrieve_local(
        self,
        query: str,
        *,
        top_k: int,
        language: str | None,
    ) -> list[RetrievedChunk]:
        """Retrieve from local pgvector hybrid index (optional supplement to Fanar-Sadiq)."""
        try:
            query_embedding = await self.embedding_generator.embed_query(query)
        except RuntimeError as exc:
            logger.warning("Local embedding unavailable, using Fanar-Sadiq RAG only: %s", exc)
            return []

        try:
            candidates = await self.retriever.retrieve(
                query=query,
                query_embedding=query_embedding,
                top_k=top_k * 2,
                language=language,
            )
        except Exception as exc:
            logger.warning("Local vector retrieval failed: %s", exc)
            return []

        candidates = self.metadata_filter.apply(candidates)
        if not candidates:
            return []

        reranked = self.cross_encoder.rerank(query, candidates, top_k=top_k * 2)
        return self.diversity.rerank(reranked, top_k=top_k)

    @staticmethod
    def _merge_chunks(
        fanar: list[RetrievedChunk],
        local: list[RetrievedChunk],
        *,
        top_k: int,
        language: str | None = None,
    ) -> list[RetrievedChunk]:
        """Merge Fanar-Sadiq and local chunks, deduplicating by content prefix."""
        seen: set[str] = set()
        merged: list[RetrievedChunk] = []
        candidates = fanar + local
        if language in {"ar", "en"}:
            candidates = sorted(
                candidates,
                key=lambda chunk: 0 if chunk.language == language else 1,
            )
        for chunk in candidates:
            key = f"{chunk.source_title[:40]}::{chunk.content[:200]}".lower()
            if key in seen:
                continue
            seen.add(key)
            merged.append(chunk)
            if len(merged) >= top_k:
                break
        return merged
