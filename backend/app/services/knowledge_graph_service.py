"""Knowledge graph and public knowledge browse services."""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.repositories.source_repository import SourceRepository
from backend.app.schemas.feature_schemas import (
    GraphEdgeSchema,
    GraphNodeSchema,
    KnowledgeBrowseResponse,
    KnowledgeGraphResponse,
    KnowledgeSourceItem,
)
from backend.app.services.neo4j_graph_service import (
    get_graph_from_neo4j_or_none,
    seed_neo4j_from_graph,
)

# (id, label_en, label_ar, type, x, y)
SEED_NODES: list[tuple[str, str, str, str, float, float]] = [
    ("quran", "Quran", "القرآن الكريم", "quran", 0.15, 0.35),
    ("hadith", "Hadith", "الحديث النبوي", "hadith", 0.35, 0.25),
    ("aaoifi", "AAOIFI", "AAOIFI", "standard", 0.65, 0.35),
    ("fiqh_academy", "International Fiqh Academy", "مجمع الفقه الإسلامي الدولي", "institution", 0.85, 0.25),
    ("riba", "Riba", "الربا", "topic", 0.25, 0.65),
    ("stocks", "Equities", "الأسهم", "topic", 0.55, 0.65),
    ("zakat", "Zakat", "الزكاة", "topic", 0.75, 0.65),
    ("sukuk", "Sukuk", "الصكوك", "concept", 0.45, 0.85),
    ("murabaha", "Murabaha", "المرابحة", "concept", 0.65, 0.85),
    ("crypto", "Crypto / DeFi", "العملات الرقمية / DeFi", "concept", 0.35, 0.85),
    ("listed_equity", "Listed company", "شركة مدرجة", "company", 0.55, 0.15),
]

SEED_EDGES: list[tuple[str, str, str]] = [
    ("quran", "riba", "prohibits"),
    ("hadith", "riba", "warns"),
    ("aaoifi", "stocks", "screens"),
    ("fiqh_academy", "stocks", "guidance"),
    ("aaoifi", "zakat", "standards"),
    ("quran", "zakat", "mandates"),
    ("aaoifi", "sukuk", "standards"),
    ("fiqh_academy", "murabaha", "guidance"),
    ("aaoifi", "crypto", "reviews"),
    ("stocks", "listed_equity", "screens"),
    ("sukuk", "murabaha", "related"),
]


def _node_label(_node_id: str, label_en: str, label_ar: str, language: str) -> str:
    return label_ar if language == "ar" else label_en


async def browse_authenticated_sources(session: AsyncSession, limit: int = 50) -> KnowledgeBrowseResponse:
    """Return authenticated sources for the public knowledge base."""
    repo = SourceRepository(session)
    sources = await repo.list_filtered(is_authenticated=True, limit=limit, offset=0)
    items = [
        KnowledgeSourceItem(
            id=str(source.id),
            title=source.title,
            author=source.author,
            source_type=source.source_type.value,
            language=source.language,
        )
        for source in sources
    ]
    return KnowledgeBrowseResponse(items=items, total=len(items))


def _build_seed_graph(session_sources: list, *, language: str = "en") -> KnowledgeGraphResponse:
    nodes = [
        GraphNodeSchema(
            id=node_id,
            label=_node_label(node_id, label_en, label_ar, language),
            type=node_type,
            x=x,
            y=y,
        )
        for node_id, label_en, label_ar, node_type, x, y in SEED_NODES
    ]
    edges = [
        GraphEdgeSchema(source=source, target=target, label=label)
        for source, target, label in SEED_EDGES
    ]

    for index, source in enumerate(session_sources):
        node_id = f"source-{source.id}"
        nodes.append(
            GraphNodeSchema(
                id=node_id,
                label=source.title[:60],
                type=source.source_type.value,
                x=0.5 + 0.35 * (index % 3) * 0.2,
                y=0.15 + (index % 4) * 0.18,
            )
        )
        edges.append(
            GraphEdgeSchema(
                source="aaoifi" if source.source_type.value == "standard" else "fiqh_academy",
                target=node_id,
                label="references",
            )
        )

    return KnowledgeGraphResponse(nodes=nodes, edges=edges)


async def build_knowledge_graph(session: AsyncSession, *, language: str = "en") -> KnowledgeGraphResponse:
    """Build an explorable graph from Neo4j when available, else seeds + Postgres sources."""
    neo4j_graph = await get_graph_from_neo4j_or_none()
    if neo4j_graph and len(neo4j_graph.nodes) >= 4:
        if language == "ar":
            seed_by_id = {row[0]: row for row in SEED_NODES}
            for node in neo4j_graph.nodes:
                seed = seed_by_id.get(node.id)
                if seed:
                    node.label = seed[2]
        return neo4j_graph

    repo = SourceRepository(session)
    sources = await repo.list_filtered(is_authenticated=True, limit=24, offset=0)
    graph = _build_seed_graph(sources, language=language)
    seed_neo4j_from_graph(graph)
    return graph
