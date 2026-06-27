"""Tests for query SSE streaming."""

import json

import httpx
import pytest

from backend.app.services.query_stream import chunk_summary_text, format_sse


def test_chunk_summary_text_splits_words() -> None:
    chunks = chunk_summary_text("Riba is prohibited in Islam.")
    assert chunks == ["Riba ", "is ", "prohibited ", "in ", "Islam."]


def test_format_sse_event() -> None:
    frame = format_sse("token", {"text": "Hello "})
    assert frame.startswith("event: token\n")
    assert '"Hello "' in frame


@pytest.mark.asyncio
async def test_stream_query_returns_sse_events(
    async_client: httpx.AsyncClient,
    auth_headers: dict[str, str],
    seeded_knowledge: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """GET /queries/{id}/stream should emit status, token, section, and complete events."""
    monkeypatch.setattr("backend.app.services.query_stream.TOKEN_DELAY_SECONDS", 0)
    monkeypatch.setattr("backend.app.services.query_stream.SECTION_DELAY_SECONDS", 0)

    create_resp = await async_client.post(
        "/api/v1/queries",
        json={"question": "Is riba prohibited in Islam?", "language": "en"},
        headers=auth_headers,
    )
    assert create_resp.status_code == 201, create_resp.json()
    query_id = create_resp.json()["query_id"]

    async with async_client.stream(
        "GET",
        f"/api/v1/queries/{query_id}/stream",
        headers={**auth_headers, "Accept": "text/event-stream"},
    ) as response:
        assert response.status_code == 200
        body = ""
        async for chunk in response.aiter_text():
            body += chunk

    events = []
    for block in body.strip().split("\n\n"):
        if not block.strip():
            continue
        event_name = "message"
        data_line = ""
        for line in block.split("\n"):
            if line.startswith("event:"):
                event_name = line.split(":", 1)[1].strip()
            elif line.startswith("data:"):
                data_line = line.split(":", 1)[1].strip()
        events.append((event_name, json.loads(data_line)))

    event_names = [name for name, _ in events]
    assert "status" in event_names
    assert "token" in event_names
    assert "section" in event_names
    assert "complete" in event_names

    complete_payload = next(payload for name, payload in events if name == "complete")
    assert complete_payload["summary"]
    assert complete_payload["evidence"]
