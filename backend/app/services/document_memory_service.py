"""Retrieve persisted user PDF context for document Q&A in chat."""

from __future__ import annotations

import re
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from agents.common.evidence import EvidenceItem
from backend.app.repositories.user_document_repository import UserDocumentRepository
from backend.app.services.query_depth import is_document_question

SNIPPET_LIMIT = 700

DOCUMENT_QUERY_STOPWORDS = {
    "what",
    "did",
    "my",
    "the",
    "about",
    "mention",
    "mentioned",
    "document",
    "report",
    "uploaded",
    "pdf",
    "page",
    "chapter",
    "summarize",
    "annual",
    "file",
    "ماذا",
    "ذكر",
    "تقرير",
    "مستند",
    "صفحة",
    "فصل",
    "ملف",
    "الخاص",
    "بي",
}


def _document_search_terms(question: str) -> list[str]:
    words = re.findall(r"[\w\u0600-\u06ff]+", question.lower())
    terms = [word for word in words if len(word) > 2 and word not in DOCUMENT_QUERY_STOPWORDS]
    if not terms:
        return [question.strip()[:48]]
    return terms[:6]


async def fetch_document_evidence(
    session: AsyncSession,
    user_id: uuid.UUID,
    question: str,
    *,
    limit: int = 3,
) -> list[EvidenceItem]:
    """Load relevant uploaded document excerpts as retrieval evidence."""
    if not is_document_question(question):
        return []

    repo = UserDocumentRepository(session)
    documents = []
    seen_ids: set[uuid.UUID] = set()
    for term in _document_search_terms(question):
        for document in await repo.search_by_user(user_id, term, limit=limit):
            if document.id in seen_ids:
                continue
            seen_ids.add(document.id)
            documents.append(document)
            if len(documents) >= limit:
                break
        if len(documents) >= limit:
            break

    if not documents:
        documents = await repo.list_by_user(user_id, limit=limit)

    evidence: list[EvidenceItem] = []
    for document in documents[:limit]:
        snippet = (document.search_text or document.summary or "").strip()
        if not snippet:
            continue
        evidence.append(
            EvidenceItem(
                text=snippet[:SNIPPET_LIMIT],
                source_id=str(document.id),
                chunk_id=f"user-doc-{document.id}",
                citation=f"{document.filename} (uploaded document, p.1–{document.page_count})",
                source_title=document.filename,
                source_author="User upload",
                source_type="document",
                language="en",
                score=0.93,
                metadata={
                    "document_id": str(document.id),
                    "page_count": document.page_count,
                    "origin": "user_document",
                },
            )
        )
    return evidence
