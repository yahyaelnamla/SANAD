"""Server-Sent Events streaming for query progress and response delivery."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from typing import Any
from uuid import UUID

from backend.app.models.enums import QueryStatus
from backend.app.models.user import User
from backend.app.schemas.query_schemas import QueryResultSchema
from backend.app.services.query_service import QueryService

POLL_INTERVAL_SECONDS = 0.8
MAX_POLL_ATTEMPTS = 900
TOKEN_DELAY_SECONDS = 0.0
SECTION_DELAY_SECONDS = 0.0
DRAFT_TOKEN_DELAY_SECONDS = 0.0


def _active_agent(trace: list | None) -> str | None:
    """Return the agent currently marked running, if any."""
    if not trace:
        return None
    for step in reversed(trace):
        status = step.status if hasattr(step, "status") else step.get("status")
        agent = step.agent if hasattr(step, "agent") else step.get("agent")
        if status == "running" and agent:
            return agent
    return None


def format_sse(event: str, data: dict[str, Any]) -> str:
    """Format a single SSE frame."""
    return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"


def chunk_summary_text(text: str) -> list[str]:
    """Split summary into stream-friendly chunks for Arabic and English."""
    if not text.strip():
        return []

    chunks: list[str] = []
    buffer = ""
    for char in text:
        buffer += char
        if char in " \n" or len(buffer) >= 24:
            chunks.append(buffer)
            buffer = ""
    if buffer:
        chunks.append(buffer)
    return chunks


async def stream_query_events(
    service: QueryService,
    user: User,
    query_id: UUID,
) -> AsyncIterator[str]:
    """Yield SSE events for query status, draft tokens, final tokens, and completion."""
    result: QueryResultSchema | None = None
    seen_draft_len = 0

    for _ in range(MAX_POLL_ATTEMPTS):
        result = await service.get_query(user, query_id)
        yield format_sse(
            "status",
            {
                "query_id": str(result.query_id),
                "status": result.status.value,
                "agent_trace": [step.model_dump() for step in (result.agent_trace or [])],
                "pipeline_complete": result.status in (QueryStatus.COMPLETED, QueryStatus.FAILED),
                "active_agent": _active_agent(result.agent_trace),
                "draft_summary": result.draft_summary,
            },
        )

        if result.status == QueryStatus.PROCESSING:
            draft = result.draft_summary or ""
            if len(draft) > seen_draft_len:
                new_part = draft[seen_draft_len:]
                for chunk in chunk_summary_text(new_part):
                    yield format_sse("draft_token", {"text": chunk})
                    await asyncio.sleep(DRAFT_TOKEN_DELAY_SECONDS)
                seen_draft_len = len(draft)

        if result.status in (QueryStatus.COMPLETED, QueryStatus.FAILED):
            break
        await asyncio.sleep(POLL_INTERVAL_SECONDS)
    else:
        yield format_sse("error", {"message": "Query timed out while waiting for analysis."})
        return

    assert result is not None

    if result.refused or result.status == QueryStatus.FAILED:
        yield format_sse("complete", result.model_dump(mode="json"))
        return

    summary = result.summary or ""
    if seen_draft_len > 0 and len(summary) > seen_draft_len:
        chunks = chunk_summary_text(summary[seen_draft_len:])
    elif seen_draft_len > 0:
        chunks = []
    else:
        chunks = chunk_summary_text(summary)

    for chunk in chunks:
        yield format_sse("token", {"text": chunk})
        await asyncio.sleep(TOKEN_DELAY_SECONDS)

    section_payloads: list[tuple[str, dict[str, Any]]] = [
        ("summary", {"summary": result.summary}),
        ("evidence", {"evidence": [item.model_dump() for item in result.evidence]}),
        (
            "analysis",
            {
                "principles": [item.model_dump() for item in result.principles],
                "reasoning": result.reasoning,
            },
        ),
        ("opinions", {"opinions": [item.model_dump() for item in result.opinions]}),
        (
            "madhhab",
            {"madhhab_matrix": [item.model_dump() for item in result.madhhab_matrix]},
        ),
        (
            "financial",
            {
                "financial_context": (
                    result.financial_context.model_dump()
                    if result.financial_context
                    else None
                )
            },
        ),
        (
            "confidence",
            {
                "confidence": result.confidence,
                "confidence_breakdown": (
                    result.confidence_breakdown.model_dump()
                    if result.confidence_breakdown
                    else None
                ),
            },
        ),
        ("sources", {"sources": [item.model_dump() for item in result.sources]}),
    ]

    for section_name, payload in section_payloads:
        if section_name == "madhhab" and not result.madhhab_matrix:
            continue
        if section_name == "financial" and not result.financial_context:
            continue
        if section_name == "evidence" and not result.evidence:
            continue
        if section_name == "opinions" and not result.opinions:
            continue
        if section_name == "sources" and not result.sources:
            continue
        if section_name == "analysis" and not result.principles and not result.reasoning:
            continue

        yield format_sse("section", {"section": section_name, "data": payload})
        await asyncio.sleep(SECTION_DELAY_SECONDS)

    yield format_sse("complete", result.model_dump(mode="json"))
