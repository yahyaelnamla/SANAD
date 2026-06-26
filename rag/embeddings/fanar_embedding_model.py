"""Fanar embedding model client."""

import asyncio
import logging
from typing import Sequence

import httpx

from config.fanar_api_keys import (
    FANAR_API_BASE_URL,
    FANAR_MODELS,
    FANAR_ORGANIZATION,
    get_fanar_api_key,
)
from rag.embeddings.embedding_utils import validate_embedding

logger = logging.getLogger(__name__)


class FanarEmbeddingModel:
    """Client for Fanar embedding API with retry."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        organization: str | None = None,
        model: str | None = None,
        max_retries: int = 3,
        timeout: float = 60.0,
    ) -> None:
        self.api_key = api_key or get_fanar_api_key()
        self.base_url = (base_url or FANAR_API_BASE_URL).rstrip("/")
        self.organization = organization or FANAR_ORGANIZATION
        self.model = model or FANAR_MODELS["embedding"]
        self.max_retries = max_retries
        self.timeout = timeout
        self._http_client: httpx.AsyncClient | None = None

    def _client(self) -> httpx.AsyncClient:
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(timeout=self.timeout)
        return self._http_client

    async def close(self) -> None:
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()
            self._http_client = None

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "X-Fanar-Key": self.api_key,
            "X-Organization": self.organization,
            "Content-Type": "application/json",
        }

    async def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        """Generate embeddings for a batch of texts."""
        if not texts:
            return []

        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                return await self._call_api(texts)
            except (httpx.HTTPError, ValueError) as exc:
                last_error = exc
                logger.warning("Fanar embedding attempt %s failed: %s", attempt, exc)
                if attempt < self.max_retries:
                    await asyncio.sleep(2 ** (attempt - 1))

        msg = f"Fanar embedding failed after {self.max_retries} attempts"
        raise RuntimeError(msg) from last_error

    async def embed_text(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        embeddings = await self.embed_texts([text])
        return embeddings[0]

    async def _call_api(self, texts: Sequence[str]) -> list[list[float]]:
        """Call the Fanar embeddings endpoint."""
        url = f"{self.base_url}/embeddings"
        payload = {"model": self.model, "queries": list(texts)}

        response = await self._client().post(url, headers=self._headers(), json=payload)
        if response.status_code in {401, 403, 404, 422}:
            detail = response.text[:300]
            raise ValueError(f"Fanar embedding HTTP {response.status_code}: {detail}")
        response.raise_for_status()
        data = response.json()

        if isinstance(data, list):
            embeddings = [validate_embedding(row) for row in data]
            if len(embeddings) != len(texts):
                raise ValueError("Fanar API returned unexpected embedding count")
            return embeddings

        items = data.get("data", [])
        if len(items) != len(texts):
            raise ValueError("Fanar API returned unexpected embedding count")

        embeddings: list[list[float]] = []
        for item in sorted(items, key=lambda row: row.get("index", 0)):
            embedding = item.get("embedding")
            if not isinstance(embedding, list):
                raise ValueError("Invalid embedding payload from Fanar API")
            embeddings.append(validate_embedding(embedding))

        return embeddings
