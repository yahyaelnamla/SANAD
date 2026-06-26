"""Batch embedding generation for text chunks."""

from rag.chunking.base import TextChunk
from rag.embeddings.fanar_embedding_model import FanarEmbeddingModel


class EmbeddingGenerator:
    """Generates embeddings for chunked documents."""

    def __init__(self, model: FanarEmbeddingModel | None = None) -> None:
        self.model = model or FanarEmbeddingModel()

    async def embed_chunks(
        self,
        chunks: list[TextChunk],
        batch_size: int = 32,
    ) -> list[list[float]]:
        """Embed all chunks in batches."""
        embeddings: list[list[float]] = []
        for start in range(0, len(chunks), batch_size):
            batch = chunks[start : start + batch_size]
            batch_embeddings = await self.model.embed_texts([chunk.content for chunk in batch])
            embeddings.extend(batch_embeddings)
        return embeddings

    async def embed_query(self, query: str) -> list[float]:
        """Embed a user query for retrieval."""
        return await self.model.embed_text(query)
