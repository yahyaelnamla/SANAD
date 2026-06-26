"""Retrieval Agent — searches authenticated sources via Fanar-Sadiq RAG."""

import logging
import os

from sqlalchemy.ext.asyncio import AsyncSession

from agents.common.fanar_client import FanarLLMClient
from agents.intent_agent.models import IntentResult, IntentType
from agents.retrieval_agent.models import RetrievalAgentResult
from agents.retrieval_agent.tools import build_search_query, evidence_from_rag
from backend.app.services.web_search_service import search_web
from rag.pipelines.retrieval_pipeline import RetrievalPipeline

logger = logging.getLogger(__name__)

ENABLE_CROSS_LANGUAGE_RETRIEVAL = os.getenv(
    "ENABLE_CROSS_LANGUAGE_RETRIEVAL", "false"
).lower() in {"1", "true", "yes"}


class RetrievalAgent:
    """Retrieve evidence from Fanar-Sadiq RAG and local hybrid search."""

    NO_EVIDENCE_REASON = (
        "No authenticated sources found. The system refuses to answer without evidence."
    )

    def __init__(
        self,
        session: AsyncSession,
        pipeline: RetrievalPipeline | None = None,
        fanar_client: FanarLLMClient | None = None,
    ) -> None:
        self.session = session
        self._fanar: FanarLLMClient | None = fanar_client
        self.pipeline = pipeline or RetrievalPipeline(session, fanar_client=fanar_client)

    async def retrieve(
        self,
        intent: IntentResult,
        *,
        top_k: int = 5,
        language: str | None = None,
    ) -> RetrievalAgentResult:
        """Retrieve ranked evidence chunks for the given intent."""
        search_query = build_search_query(intent)
        lang = language or intent.language
        result = await self.pipeline.retrieve(
            search_query,
            top_k=top_k,
            language=lang,
        )

        if len(result.chunks) < max(2, top_k // 2):
            try:
                web_hits = await search_web(search_query, limit=3)
                if web_hits:
                    expansion = " ".join(
                        hit.get("title", "") for hit in web_hits[:2] if hit.get("title")
                    )
                    expanded_query = f"{search_query} {expansion}".strip()
                    retry = await self.pipeline.retrieve(
                        expanded_query,
                        top_k=top_k,
                        language=lang,
                    )
                    if len(retry.chunks) > len(result.chunks):
                        result = retry
                        logger.info("Web search expanded retrieval to %d chunks", len(result.chunks))
            except Exception as exc:
                logger.debug("Web search enrichment skipped: %s", exc)

        cross_chunks = []
        if ENABLE_CROSS_LANGUAGE_RETRIEVAL and self._fanar and lang in {"ar", "en"}:
            other_lang = "en" if lang == "ar" else "ar"
            try:
                translated_query = await self._fanar.translate_text(
                    search_query,
                    target_language=other_lang,
                    source_language=lang,
                )
                cross_result = await self.pipeline.retrieve(
                    translated_query,
                    top_k=max(2, top_k // 2),
                    language=other_lang,
                )
                cross_chunks = evidence_from_rag(cross_result.to_evidence_list())
                logger.info(
                    "Cross-language (%s→%s) retrieval added %d chunks",
                    lang,
                    other_lang,
                    len(cross_chunks),
                )
            except Exception as exc:
                logger.debug("Cross-language retrieval skipped: %s", exc)

        pipeline_evidence = evidence_from_rag(result.to_evidence_list())
        merged = pipeline_evidence + cross_chunks

        if not merged:
            return RetrievalAgentResult(
                query=intent.raw_query,
                refused=True,
                reason=result.reason or self.NO_EVIDENCE_REASON,
            )

        return RetrievalAgentResult(
            query=intent.raw_query,
            chunks=merged,
        )

    async def retrieve_from_document(
        self,
        content: bytes,
        *,
        filename: str,
        language: str = "ar",
        top_k: int = 5,
    ) -> RetrievalAgentResult:
        """Extract and retrieve from uploaded PDF/image via Fanar-Oryx-IVU."""
        if not self._fanar:
            return RetrievalAgentResult(
                query=filename,
                refused=True,
                reason="Fanar client not configured for document extraction.",
            )
        try:
            extracted_text = await self._fanar.extract_document_text(
                content,
                filename=filename,
                language=language,
            )
        except (RuntimeError, ValueError) as exc:
            logger.warning("Fanar-Oryx document extraction failed: %s", exc)
            return RetrievalAgentResult(
                query=filename,
                refused=True,
                reason=f"Document extraction failed: {exc}",
            )
        synthetic_intent = IntentResult(
            raw_query=extracted_text[:500],
            intent_type=IntentType.GENERAL_INQUIRY,
            domain="islamic_finance",
            language=language,
            entities=[],
            keywords=[],
        )
        return await self.retrieve(synthetic_intent, top_k=top_k, language=language)
