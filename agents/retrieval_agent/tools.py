"""Retrieval Agent tools — RAG pipeline interface."""

import hashlib
from typing import Any

from agents.common.evidence import EvidenceItem
from agents.common.evidence_enrichment import enrich_evidence_list
from agents.intent_agent.models import IntentResult
from backend.app.services.islamic_finance_topics import enrich_retrieval_query


def build_search_query(intent: IntentResult) -> str:
    """Combine raw query with Islamic finance topic enrichment for retrieval."""
    return enrich_retrieval_query(intent)


def evidence_from_rag(items: list[dict[str, Any]]) -> list[EvidenceItem]:
    """Convert RAG evidence dicts to EvidenceItem models."""
    raw = [
        EvidenceItem(
            text=item["text"],
            source_id=item["source_id"],
            chunk_id=item["chunk_id"],
            citation=item["citation"],
            source_title=item["source_title"],
            source_author=item["source_author"],
            source_type=item["source_type"],
            language=item["language"],
            score=item.get("score", 0.0),
            metadata=item.get("metadata", {}),
        )
        for item in items
    ]
    return enrich_evidence_list(raw)


def evidence_from_fanar_rag(items: list[dict[str, Any]]) -> list[EvidenceItem]:
    """Convert Fanar retrieve_knowledge() output to EvidenceItem models."""
    raw: list[EvidenceItem] = []
    for item in items:
        try:
            raw.append(
                EvidenceItem(
                    text=item["text"],
                    source_id=(
                        item.get("metadata", {}).get("fanar_reference_number")
                        or hashlib.sha256(item["text"].encode()).hexdigest()[:16]
                    ),
                    chunk_id=item.get("metadata", {}).get("verification_hash", ""),
                    citation=item.get("citation", item.get("source_title", "Fanar-Sadiq")),
                    source_title=item.get("source_title", "Fanar-Sadiq"),
                    source_author=item.get("source_author", "Fanar-Sadiq"),
                    source_type=item.get("source_type", "fiqh"),
                    language=item.get("language", "ar"),
                    score=float(item.get("score", 0.9)),
                    metadata=item.get("metadata", {}),
                )
            )
        except Exception:
            continue
    return enrich_evidence_list(raw)
