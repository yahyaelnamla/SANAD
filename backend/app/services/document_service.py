"""Document analysis service — PDF upload and Shariah finance screening."""

from __future__ import annotations

import io
import logging
import re
import uuid
from collections.abc import Iterable
from typing import Any

from pypdf import PdfReader
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.exceptions import ValidationError
from backend.app.models.user_document import UserDocument
from backend.app.repositories.user_document_repository import UserDocumentRepository
from backend.app.schemas.feature_schemas import (
    DocumentAnalysisResponse,
    DocumentCitation,
    DocumentCompareItem,
    DocumentCompareResponse,
    DocumentFinding,
    DocumentListItem,
    DocumentListResponse,
    DocumentPageHighlight,
    DocumentRevenueRow,
)
from backend.app.services.docling_extractor import extract_pdf_text_with_docling

RIBA_KEYWORDS = (
    "riba",
    "interest",
    "usury",
    "interest income",
    "interest-bearing",
    "ربا",
    "فائدة",
    "فوائد",
    "دين ربوي",
)
FINANCE_KEYWORDS = (
    "debt",
    "loan",
    "revenue",
    "profit",
    "income",
    "sharia",
    "halal",
    "haram",
    "compliance",
    "دين",
    "إيراد",
    "ربح",
    "شرعي",
)
MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_PAGES = 100
SUMMARY_MAX_CHARS = 4000
SEARCH_TEXT_LIMIT = 50000

logger = logging.getLogger(__name__)


async def analyze_pdf_async(
    content: bytes,
    filename: str,
    language: str = "en",
    fanar_client: Any | None = None,
) -> tuple[DocumentAnalysisResponse, str]:
    """Extract and analyze a PDF, with Docling then pypdf, Fanar OCR as fallback."""
    docling_text = extract_pdf_text_with_docling(content, filename)
    if docling_text:
        return analyze_extracted_text(docling_text, filename, language=language)

    try:
        return analyze_pdf(content, filename, language=language)
    except ValidationError as exc:
        if fanar_client is None or "No extractable text" not in str(exc):
            raise
        logger.info("pypdf extraction failed; attempting Fanar-Oryx-IVU OCR for %s", filename)
        ocr_text = await fanar_client.extract_document_text(
            content,
            filename=filename,
            language=language,
        )
        return analyze_extracted_text(ocr_text, filename, language=language)


def analyze_extracted_text(
    full_text: str,
    filename: str,
    language: str = "en",
) -> tuple[DocumentAnalysisResponse, str]:
    """Analyze pre-extracted document text."""
    _ = language
    if not full_text.strip():
        raise ValidationError("No extractable text found in PDF.")
    pages_text: list[tuple[int, str]] = [(1, full_text.strip())]
    return _build_analysis_from_pages(pages_text, filename, page_count=1, full_text=full_text)


async def analyze_and_store_pdf(
    session: AsyncSession,
    user_id: uuid.UUID,
    content: bytes,
    filename: str,
    language: str = "en",
    fanar_client: Any | None = None,
) -> DocumentAnalysisResponse:
    """Analyze a PDF and persist it for document memory and search."""
    analysis, search_text = await analyze_pdf_async(
        content,
        filename,
        language=language,
        fanar_client=fanar_client,
    )
    repo = UserDocumentRepository(session)
    document = UserDocument(
        user_id=user_id,
        filename=filename,
        page_count=analysis.page_count,
        summary=analysis.summary,
        search_text=search_text,
        analysis=analysis.model_dump(mode="json"),
    )
    await repo.create(document)
    return analysis.model_copy(update={"document_id": document.id})


def analyze_pdf(content: bytes, filename: str, language: str = "en") -> tuple[DocumentAnalysisResponse, str]:
    """Extract and analyze a PDF for Shariah finance signals."""
    _ = language
    if len(content) < 100:
        raise ValidationError("PDF file is too small.")
    if len(content) > MAX_FILE_SIZE:
        raise ValidationError("PDF file exceeds the 10MB limit.")
    if not filename.lower().endswith(".pdf"):
        raise ValidationError("Upload must be a PDF file.")

    docling_text = extract_pdf_text_with_docling(content, filename)
    if docling_text:
        pages_text: list[tuple[int, str]] = [(1, docling_text)]
        return _build_analysis_from_pages(
            pages_text,
            filename,
            page_count=max(1, docling_text.count("\n\n") // 3),
            full_text=docling_text,
        )

    try:
        reader = PdfReader(io.BytesIO(content))
    except Exception as exc:
        raise ValidationError("Could not read PDF file.") from exc

    if len(reader.pages) > MAX_PAGES:
        raise ValidationError(f"PDF exceeds the {MAX_PAGES} page limit.")

    pages_text: list[tuple[int, str]] = []
    for index, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages_text.append((index, text))

    if not pages_text:
        raise ValidationError("No extractable text found in PDF.")

    full_text = "\n\n".join(text for _, text in pages_text)
    return _build_analysis_from_pages(
        pages_text,
        filename,
        page_count=len(reader.pages),
        full_text=full_text,
    )


async def list_user_documents(session: AsyncSession, user_id: uuid.UUID) -> DocumentListResponse:
    """Return persisted documents for the current user."""
    repo = UserDocumentRepository(session)
    documents = await repo.list_by_user(user_id)
    items = [
        DocumentListItem(
            document_id=doc.id,
            filename=doc.filename,
            page_count=doc.page_count,
            summary=doc.summary,
            created_at=doc.created_at,
        )
        for doc in documents
    ]
    return DocumentListResponse(items=items, total=len(items))


async def delete_user_document(
    session: AsyncSession,
    user_id: uuid.UUID,
    document_id: uuid.UUID,
) -> None:
    """Delete a persisted user document."""
    from backend.app.exceptions import NotFoundError

    repo = UserDocumentRepository(session)
    owned = await repo.get_owned(user_id, document_id)
    if owned is None:
        raise NotFoundError("Document not found.")
    await repo.delete(owned)


async def compare_user_documents(
    session: AsyncSession,
    user_id: uuid.UUID,
    document_ids: list[uuid.UUID],
) -> DocumentCompareResponse:
    """Compare two to four saved PDF analyses side-by-side."""
    if len(document_ids) < 2 or len(document_ids) > 4:
        raise ValidationError("Select between 2 and 4 documents to compare.")

    repo = UserDocumentRepository(session)
    documents: list[UserDocument] = []
    for doc_id in document_ids:
        owned = await repo.get_owned(user_id, doc_id)
        if owned is None:
            raise ValidationError(f"Document {doc_id} was not found.")
        documents.append(owned)

    items: list[DocumentCompareItem] = []
    riba_by_doc: dict[str, set[str]] = {}

    for doc in documents:
        analysis_data = doc.analysis if isinstance(doc.analysis, dict) else {}
        riba_findings = analysis_data.get("riba_findings") or []
        revenue_rows = analysis_data.get("revenue_analysis") or []
        riba_labels = sorted(
            {
                str(item.get("label", "")).strip().lower()
                for item in riba_findings
                if isinstance(item, dict) and item.get("label")
            }
        )
        riba_by_doc[str(doc.id)] = set(riba_labels)
        items.append(
            DocumentCompareItem(
                document_id=doc.id,
                filename=doc.filename,
                page_count=doc.page_count,
                summary=doc.summary,
                riba_signal_count=len(riba_findings),
                revenue_signal_count=len(revenue_rows),
                key_findings=list(analysis_data.get("key_findings") or [])[:5],
                riba_labels=riba_labels[:8],
            )
        )

    all_sets = list(riba_by_doc.values())
    shared = sorted(set.intersection(*all_sets)) if all_sets else []
    unique: dict[str, list[str]] = {}
    union = set.union(*all_sets) if all_sets else set()
    for doc in documents:
        unique_labels = sorted(riba_by_doc[str(doc.id)] - set(shared))
        if unique_labels:
            unique[doc.filename] = unique_labels

    notes: list[str] = []
    if shared:
        notes.append(f"Shared riba-related signals across all documents: {', '.join(shared)}.")
    elif union:
        notes.append("No riba signals are shared across every selected document.")
    else:
        notes.append("No riba keywords detected in the selected documents.")

    page_counts = [item.page_count for item in items]
    if max(page_counts) - min(page_counts) > 10:
        notes.append(
            f"Document length varies significantly ({min(page_counts)}–{max(page_counts)} pages)."
        )

    revenue_counts = [item.revenue_signal_count for item in items]
    if any(revenue_counts) and not all(revenue_counts):
        notes.append("Revenue figures appear in some documents but not all — review individually.")

    return DocumentCompareResponse(
        documents=items,
        shared_riba_signals=shared,
        unique_riba_by_document=unique,
        comparison_notes=notes,
    )


def _build_analysis_from_pages(
    pages_text: list[tuple[int, str]],
    filename: str,
    *,
    page_count: int,
    full_text: str,
) -> tuple[DocumentAnalysisResponse, str]:
    riba_findings = _scan_keywords(pages_text, RIBA_KEYWORDS, "riba")
    finance_findings = _scan_keywords(pages_text, FINANCE_KEYWORDS, "finance")
    revenue_rows = _extract_revenue(pages_text)
    highlights = _page_highlights(pages_text, RIBA_KEYWORDS + FINANCE_KEYWORDS)

    key_findings = _build_key_findings(riba_findings, finance_findings, revenue_rows)
    citations = [
        DocumentCitation(
            page=page,
            snippet=_truncate(snippet, 280),
            topic=topic,
        )
        for page, snippet, topic in highlights[:8]
    ]

    return (
        DocumentAnalysisResponse(
            filename=filename,
            page_count=page_count,
            summary=_build_summary(full_text),
            key_findings=key_findings,
            riba_findings=riba_findings,
            revenue_analysis=revenue_rows,
            highlighted_pages=[
                DocumentPageHighlight(page=page, snippet=_truncate(snippet, 320), topic=topic)
                for page, snippet, topic in highlights[:10]
            ],
            citations=citations,
        ),
        _truncate(full_text, SEARCH_TEXT_LIMIT),
    )


def _truncate(text: str, limit: int) -> str:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1].rstrip() + "…"


def _build_summary(full_text: str) -> str:
    normalized = re.sub(r"\s+", " ", full_text).strip()
    sentences = re.split(r"(?<=[.!?])\s+", normalized)
    summary = " ".join(sentence for sentence in sentences[:2] if sentence).strip()
    if not summary:
        summary = normalized[:SUMMARY_MAX_CHARS]
    return _truncate(summary, SUMMARY_MAX_CHARS)


def _scan_keywords(
    pages_text: Iterable[tuple[int, str]],
    keywords: tuple[str, ...],
    category: str,
) -> list[DocumentFinding]:
    findings: list[DocumentFinding] = []
    seen: set[str] = set()
    for page, text in pages_text:
        lowered = text.lower()
        for keyword in keywords:
            if keyword.lower() not in lowered:
                continue
            marker = f"{page}:{keyword.lower()}"
            if marker in seen:
                continue
            seen.add(marker)
            match = re.search(re.escape(keyword), text, flags=re.IGNORECASE)
            snippet = text[max(0, (match.start() if match else 0) - 80) : (match.end() if match else 0) + 120]
            findings.append(
                DocumentFinding(
                    category=category,
                    label=keyword,
                    page=page,
                    snippet=_truncate(snippet, 220),
                    severity="high" if category == "riba" else "medium",
                )
            )
    return findings[:12]


def _extract_revenue(pages_text: Iterable[tuple[int, str]]) -> list[DocumentRevenueRow]:
    patterns = (
        re.compile(r"(?:total\s+)?revenue[:\s]+[\$€£]?([\d,]+(?:\.\d+)?)", re.IGNORECASE),
        re.compile(r"net\s+income[:\s]+[\$€£]?([\d,]+(?:\.\d+)?)", re.IGNORECASE),
        re.compile(r"الإيرادات[:\s]+([\d,]+(?:\.\d+)?)"),
    )
    rows: list[DocumentRevenueRow] = []
    seen: set[str] = set()
    for page, text in pages_text:
        for pattern in patterns:
            for match in pattern.finditer(text):
                amount = match.group(1).replace(",", "")
                key = f"{page}:{match.group(0).lower()}"
                if key in seen:
                    continue
                seen.add(key)
                rows.append(
                    DocumentRevenueRow(
                        page=page,
                        metric=match.group(0).split(":")[0].strip(),
                        amount=amount,
                        snippet=_truncate(text[max(0, match.start() - 40) : match.end() + 40], 180),
                    )
                )
    return rows[:8]


def _page_highlights(
    pages_text: Iterable[tuple[int, str]],
    keywords: tuple[str, ...],
) -> list[tuple[int, str, str]]:
    highlights: list[tuple[int, str, str]] = []
    for page, text in pages_text:
        lowered = text.lower()
        for keyword in keywords:
            if keyword.lower() not in lowered:
                continue
            match = re.search(re.escape(keyword), text, flags=re.IGNORECASE)
            start = max(0, (match.start() if match else 0) - 90)
            end = min(len(text), (match.end() if match else 0) + 120)
            highlights.append((page, text[start:end], keyword))
            break
    return highlights


def _build_key_findings(
    riba_findings: list[DocumentFinding],
    finance_findings: list[DocumentFinding],
    revenue_rows: list[DocumentRevenueRow],
) -> list[str]:
    findings: list[str] = []
    if riba_findings:
        pages = sorted({item.page for item in riba_findings})
        findings.append(
            f"Potential riba or interest references detected on page(s): {', '.join(map(str, pages))}."
        )
    else:
        findings.append("No explicit riba or interest keywords were detected in extracted text.")

    if revenue_rows:
        findings.append(f"Revenue or income figures found on {len(revenue_rows)} section(s).")
    else:
        findings.append("No structured revenue figures were detected — manual review may be required.")

    if finance_findings:
        findings.append(
            f"Additional finance/compliance terms found across {len({item.page for item in finance_findings})} page(s)."
        )

    return findings
