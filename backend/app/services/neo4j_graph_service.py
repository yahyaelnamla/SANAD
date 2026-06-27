"""Neo4j knowledge graph integration (optional)."""

from __future__ import annotations

import logging
import math
import random

from backend.app.config.settings import get_settings
from backend.app.schemas.feature_schemas import (
    GraphEdgeSchema,
    GraphNodeSchema,
    KnowledgeGraphResponse,
)

logger = logging.getLogger(__name__)


def _layout_nodes(nodes: list[GraphNodeSchema]) -> list[GraphNodeSchema]:
    """Assign force-like coordinates when nodes lack positions."""
    count = len(nodes)
    if count == 0:
        return nodes

    positioned = [n for n in nodes if n.x is not None and n.y is not None]
    if len(positioned) >= count // 2:
        return nodes

    laid_out: list[GraphNodeSchema] = []
    for index, node in enumerate(nodes):
        angle = (2 * math.pi * index) / max(count, 1)
        radius = 0.28 + (index % 3) * 0.06
        laid_out.append(
            GraphNodeSchema(
                id=node.id,
                label=node.label,
                type=node.type,
                x=0.5 + radius * math.cos(angle),
                y=0.5 + radius * math.sin(angle),
            )
        )
    return laid_out


def _fetch_from_neo4j() -> KnowledgeGraphResponse | None:
    settings = get_settings()
    if not settings.neo4j_uri:
        return None

    try:
        from neo4j import GraphDatabase
    except ImportError:
        logger.warning("neo4j package not installed; skipping Neo4j graph")
        return None

    try:
        driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
        with driver.session(database=settings.neo4j_database) as session:
            node_rows = session.run(
                """
                MATCH (n)
                WHERE n:Concept OR n:Source OR n:Topic OR n:Principle OR n:Entity
                RETURN coalesce(n.id, elementId(n)) AS id,
                       coalesce(n.label, n.name, n.title, 'Node') AS label,
                       coalesce(n.type, labels(n)[0], 'concept') AS type,
                       coalesce(n.x, rand()) AS x,
                       coalesce(n.y, rand()) AS y
                LIMIT 120
                """
            ).data()
            edge_rows = session.run(
                """
                MATCH (a)-[r]->(b)
                RETURN coalesce(a.id, elementId(a)) AS source,
                       coalesce(b.id, elementId(b)) AS target,
                       coalesce(type(r), 'related') AS label
                LIMIT 200
                """
            ).data()
        driver.close()

        if not node_rows:
            return None

        nodes = [
            GraphNodeSchema(
                id=str(row["id"]),
                label=str(row["label"])[:80],
                type=str(row["type"]).lower(),
                x=float(row.get("x") or random.random()),
                y=float(row.get("y") or random.random()),
            )
            for row in node_rows
        ]
        edges = [
            GraphEdgeSchema(
                source=str(row["source"]),
                target=str(row["target"]),
                label=str(row.get("label", "related")),
            )
            for row in edge_rows
        ]
        return KnowledgeGraphResponse(nodes=_layout_nodes(nodes), edges=edges)
    except Exception as exc:
        logger.warning("Neo4j graph fetch failed: %s", exc)
        return None


def seed_neo4j_from_graph(graph: KnowledgeGraphResponse) -> None:
    """Upsert seed graph nodes and edges into Neo4j when configured."""
    settings = get_settings()
    if not settings.neo4j_uri:
        return

    try:
        from neo4j import GraphDatabase
    except ImportError:
        return

    try:
        driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
        with driver.session(database=settings.neo4j_database) as session:
            for node in graph.nodes:
                session.run(
                    """
                    MERGE (n:Entity {id: $id})
                    SET n.label = $label, n.type = $type, n.x = $x, n.y = $y
                    """,
                    id=node.id,
                    label=node.label,
                    type=node.type,
                    x=node.x if node.x is not None else random.random(),
                    y=node.y if node.y is not None else random.random(),
                )
            for edge in graph.edges:
                session.run(
                    """
                    MATCH (a:Entity {id: $source}), (b:Entity {id: $target})
                    MERGE (a)-[r:RELATED {label: $label}]->(b)
                    """,
                    source=edge.source,
                    target=edge.target,
                    label=edge.label,
                )
        driver.close()
        logger.info("Seeded Neo4j with %d nodes", len(graph.nodes))
    except Exception as exc:
        logger.warning("Neo4j seed failed: %s", exc)


async def get_graph_from_neo4j_or_none() -> KnowledgeGraphResponse | None:
    return _fetch_from_neo4j()
