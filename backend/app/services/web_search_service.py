"""Web search enrichment via Serper, Tavily, or LangSearch."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from backend.app.config.settings import get_settings

logger = logging.getLogger(__name__)


async def _serper_search(query: str, limit: int = 5) -> list[dict[str, Any]]:
    settings = get_settings()
    if not settings.serper_api_key:
        return []

    async with httpx.AsyncClient(timeout=12.0) as client:
        response = await client.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": settings.serper_api_key, "Content-Type": "application/json"},
            json={"q": query, "num": limit},
        )
        response.raise_for_status()
        payload = response.json()

    results: list[dict[str, Any]] = []
    for item in payload.get("organic", [])[:limit]:
        results.append(
            {
                "title": item.get("title", ""),
                "snippet": item.get("snippet", ""),
                "url": item.get("link", ""),
                "provider": "serper",
            }
        )
    return results


async def _tavily_search(query: str, limit: int = 5) -> list[dict[str, Any]]:
    settings = get_settings()
    if not settings.tavily_api_key:
        return []

    async with httpx.AsyncClient(timeout=12.0) as client:
        response = await client.post(
            "https://api.tavily.com/search",
            json={
                "api_key": settings.tavily_api_key,
                "query": query,
                "max_results": limit,
                "search_depth": "basic",
            },
        )
        response.raise_for_status()
        payload = response.json()

    return [
        {
            "title": item.get("title", ""),
            "snippet": item.get("content", ""),
            "url": item.get("url", ""),
            "provider": "tavily",
        }
        for item in payload.get("results", [])[:limit]
    ]


async def _langsearch_search(query: str, limit: int = 5) -> list[dict[str, Any]]:
    settings = get_settings()
    if not settings.langsearch_api_key:
        return []

    async with httpx.AsyncClient(timeout=12.0) as client:
        response = await client.post(
            "https://api.langsearch.com/v1/search",
            headers={"Authorization": f"Bearer {settings.langsearch_api_key}"},
            json={"query": query, "limit": limit},
        )
        response.raise_for_status()
        payload = response.json()

    items = payload.get("data", payload.get("results", []))
    return [
        {
            "title": item.get("title", ""),
            "snippet": item.get("snippet", item.get("content", "")),
            "url": item.get("url", item.get("link", "")),
            "provider": "langsearch",
        }
        for item in items[:limit]
    ]


async def search_web(query: str, limit: int = 5) -> list[dict[str, Any]]:
    """Search the web using the first configured provider."""
    settings = get_settings()
    providers: list[Any] = []
    if settings.serper_api_key:
        providers.append(_serper_search)
    if settings.tavily_api_key:
        providers.append(_tavily_search)
    if settings.langsearch_api_key:
        providers.append(_langsearch_search)

    for provider in providers:
        try:
            results = await provider(query, limit=limit)
            if results:
                return results
        except Exception as exc:
            logger.warning("Web search provider failed: %s", exc)

    return []
