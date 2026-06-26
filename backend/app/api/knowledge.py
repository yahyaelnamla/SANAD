"""Public knowledge base endpoints for authenticated users."""

from fastapi import APIRouter, Query

from backend.app.api.deps import CurrentUser, DbSession
from backend.app.schemas.feature_schemas import KnowledgeBrowseResponse, KnowledgeGraphResponse
from backend.app.services.knowledge_graph_service import browse_authenticated_sources, build_knowledge_graph

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])


@router.get("/sources", response_model=KnowledgeBrowseResponse, summary="Browse authenticated sources")
async def list_public_sources(
    session: DbSession,
    user: CurrentUser,
    limit: int = Query(default=50, ge=1, le=100),
) -> KnowledgeBrowseResponse:
    """Return authenticated knowledge sources available to SANAD users."""
    _ = user
    return await browse_authenticated_sources(session, limit=limit)


@router.get("/graph", response_model=KnowledgeGraphResponse, summary="Knowledge graph data")
async def get_knowledge_graph(
    session: DbSession,
    user: CurrentUser,
    language: str = Query(default="en", pattern="^(ar|en)$"),
) -> KnowledgeGraphResponse:
    """Return nodes and edges for the interactive knowledge graph."""
    _ = user
    return await build_knowledge_graph(session, language=language)
