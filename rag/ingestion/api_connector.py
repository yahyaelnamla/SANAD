"""External API connector for structured knowledge ingestion."""

from typing import Any

import httpx

from rag.ingestion.base import IngestedDocument


def fetch_from_api(
    url: str,
    source_title: str,
    source_author: str,
    content_field: str = "content",
    language: str = "en",
    headers: dict[str, str] | None = None,
    timeout: float = 30.0,
) -> IngestedDocument:
    """Fetch JSON content from an external API endpoint."""
    response = httpx.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    payload: dict[str, Any] = response.json()

    content = payload.get(content_field)
    if not isinstance(content, str) or not content.strip():
        raise ValueError(f"API response missing text field '{content_field}'")

    return IngestedDocument(
        content=content.strip(),
        source_title=source_title,
        source_author=source_author,
        language=language,
        metadata={"format": "api", "url": url, "content_field": content_field},
    )
