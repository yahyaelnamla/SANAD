"""Markdown export for query responses."""

from backend.app.models.query import Query
from backend.app.models.response import Response


def build_query_markdown(query: Query, response: Response | None) -> str:
    """Build a user-facing markdown export without internal traces."""
    title = query.title
    lines = [
        f"# SANAD — {title}",
        "",
        f"_Exported {query.created_at.isoformat()}_",
        "",
    ]

    if response is None:
        lines.append("_No response stored for this query._")
        return "\n".join(lines).strip()

    if response.summary:
        lines.extend(["## Summary", "", response.summary.strip(), ""])

    if response.evidence:
        lines.append("## Evidence")
        lines.append("")
        for index, item in enumerate(response.evidence, start=1):
            text = item.get("text", "")
            citation = item.get("citation", "")
            source_title = item.get("source_title", "")
            source_author = item.get("source_author", "")
            lines.append(f"### Evidence {index}")
            lines.append(text.strip())
            lines.append("")
            lines.append(f"**Citation:** {citation}")
            lines.append(f"**Source:** {source_author} — {source_title}")
            lines.append("")

    if response.reasoning:
        lines.extend(["## Jurisprudential Analysis", "", response.reasoning.strip(), ""])

    if response.opinions:
        lines.append("## Scholarly Opinions")
        lines.append("")
        for opinion in response.opinions:
            scholar = opinion.get("scholar", "Unknown")
            institution = opinion.get("institution")
            position = opinion.get("position", "")
            suffix = f" ({institution})" if institution else ""
            lines.append(f"- **{scholar}**{suffix}: {position}")
        lines.append("")

    lines.append(f"**Confidence:** {round(float(response.confidence or 0) * 100)}%")
    lines.append("")

    if response.sources:
        lines.append("## Sources")
        lines.append("")
        for source in response.sources:
            author = source.get("author", "")
            title_text = source.get("title", "")
            citation = source.get("citation", "")
            lines.append(f"- {author} — {title_text} ({citation})")

    return "\n".join(lines).strip()
