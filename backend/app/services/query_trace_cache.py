"""In-memory live agent trace and draft answer for queries in progress."""

from __future__ import annotations

import threading
from typing import Any
from uuid import UUID

_lock = threading.Lock()
_entries: dict[str, dict[str, Any]] = {}


def publish(
    query_id: UUID | str,
    trace: list[dict[str, Any]],
    *,
    draft_answer: str | None = None,
) -> None:
    """Store live trace and optional draft answer text after reasoning."""
    key = str(query_id)
    with _lock:
        entry = _entries.get(key, {"trace": [], "draft_answer": None})
        entry["trace"] = trace
        if draft_answer is not None:
            entry["draft_answer"] = draft_answer
        _entries[key] = entry


def get_trace(query_id: UUID | str) -> list[dict[str, Any]] | None:
    with _lock:
        entry = _entries.get(str(query_id))
        if entry is None:
            return None
        return list(entry.get("trace") or [])


def get_draft_answer(query_id: UUID | str) -> str | None:
    with _lock:
        entry = _entries.get(str(query_id))
        if entry is None:
            return None
        draft = entry.get("draft_answer")
        return draft if isinstance(draft, str) and draft.strip() else None


def clear(query_id: UUID | str) -> None:
    with _lock:
        _entries.pop(str(query_id), None)


# Backward-compatible alias
def get(query_id: UUID | str) -> list[dict[str, Any]] | None:
    return get_trace(query_id)
