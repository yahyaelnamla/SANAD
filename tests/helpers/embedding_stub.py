"""Deterministic embedding model for tests (no live HTTP)."""

from typing import Sequence

from rag.embeddings.embedding_utils import deterministic_mock_embedding
from rag.embeddings.fanar_embedding_model import FanarEmbeddingModel


class DeterministicEmbeddingModel(FanarEmbeddingModel):
    """Test double returning deterministic local embeddings."""

    def __init__(self, api_key: str = "test-key") -> None:
        super().__init__(api_key=api_key, base_url="https://test.fanar.local/v1")

    async def embed_texts(self, texts: Sequence[str]) -> list[list[float]]:
        return [deterministic_mock_embedding(text) for text in texts]
