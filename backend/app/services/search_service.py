"""Global search across chats, sources, scholars, and tools."""

from urllib.parse import quote

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.repositories.query_repository import QueryRepository
from backend.app.repositories.response_repository import ResponseRepository
from backend.app.repositories.source_repository import SourceRepository
from backend.app.repositories.user_document_repository import UserDocumentRepository
from backend.app.schemas.feature_schemas import GlobalSearchResponse, SearchResultItem
from backend.app.utils.slugify import slugify

COMPANY_HINTS = ("tesla", "nvidia", "apple", "microsoft", "amazon", "google", "meta", "bitcoin", "ethereum")


async def global_search(
    session: AsyncSession,
    user_id,
    query_text: str,
    *,
    limit: int = 20,
) -> GlobalSearchResponse:
    """Search chats, knowledge sources, scholars, and company-related queries."""
    needle = query_text.strip()
    if len(needle) < 2:
        return GlobalSearchResponse(query=needle, results=[], total=0)

    results: list[SearchResultItem] = []
    query_repo = QueryRepository(session)
    source_repo = SourceRepository(session)
    response_repo = ResponseRepository(session)
    document_repo = UserDocumentRepository(session)

    chats = await query_repo.search_by_user(user_id, needle, limit=8)
    for chat in chats:
        response = await response_repo.get_by_query_id(chat.id)
        results.append(
            SearchResultItem(
                type="chat",
                id=str(chat.id),
                title=chat.title,
                subtitle=response.summary if response else None,
                href=f"/history/{chat.id}",
                score=1.0,
            )
        )

    sources = await source_repo.search_authenticated(needle, limit=6)
    for source in sources:
        result_type = "source"
        href = "/knowledge"
        if source.source_type.value == "fatwa":
            result_type = "scholar"
            href = f"/scholars/{slugify(source.author)}"
        results.append(
            SearchResultItem(
                type=result_type,
                id=str(source.id),
                title=source.title,
                subtitle=source.author,
                href=href,
                score=0.9,
            )
        )

    documents = await document_repo.search_by_user(user_id, needle, limit=5)
    for document in documents:
        results.append(
            SearchResultItem(
                type="document",
                id=str(document.id),
                title=document.filename,
                subtitle=document.summary,
                href="/documents",
                score=0.95,
            )
        )

    lowered = needle.lower()
    if any(company in lowered for company in COMPANY_HINTS):
        results.append(
            SearchResultItem(
                type="company",
                id=f"company-{lowered.replace(' ', '-')}",
                title=needle,
                subtitle="Open company Shariah scanner",
                href=f"/scanner/company?q={quote(needle)}",
                score=0.85,
            )
        )

    if "document" in lowered or "pdf" in lowered or "report" in lowered:
        if not any(item.type == "document" for item in results):
            results.append(
                SearchResultItem(
                    type="document",
                    id="documents",
                    title="Document Analyzer",
                    subtitle="Upload and analyze PDF reports",
                    href="/documents",
                    score=0.8,
                )
            )

    # Web search enrichment when internal results are sparse
    if len(results) < 5:
        from backend.app.services.web_search_service import search_web

        web_hits = await search_web(needle, limit=min(5, limit))
        for hit in web_hits:
            results.append(
                SearchResultItem(
                    type="web",
                    id=hit.get("url", hit.get("title", "web")),
                    title=hit.get("title", "Web result"),
                    subtitle=hit.get("snippet", ""),
                    href=hit.get("url", "https://google.com/search?q=" + quote(needle)),
                    score=0.55,
                )
            )

    trimmed = results[:limit]
    return GlobalSearchResponse(query=needle, results=trimmed, total=len(trimmed))
