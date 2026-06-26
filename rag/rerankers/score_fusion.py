"""Score fusion utilities for hybrid retrieval."""

from rag.retrievers.base import RetrievedChunk


def reciprocal_rank_fusion(
    ranked_lists: list[list[RetrievedChunk]],
    top_k: int = 10,
    k: int = 60,
) -> list[RetrievedChunk]:
    """Fuse multiple ranked lists using Reciprocal Rank Fusion (RRF)."""
    scores: dict[str, float] = {}
    chunk_map: dict[str, RetrievedChunk] = {}

    for results in ranked_lists:
        for rank, chunk in enumerate(results, start=1):
            key = str(chunk.chunk_id)
            scores[key] = scores.get(key, 0.0) + 1.0 / (k + rank)
            chunk_map[key] = chunk

    fused = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:top_k]
    fused_chunks: list[RetrievedChunk] = []
    for key, fused_score in fused:
        chunk = chunk_map[key]
        fused_chunks.append(
            RetrievedChunk(
                chunk_id=chunk.chunk_id,
                source_id=chunk.source_id,
                content=chunk.content,
                score=fused_score,
                source_title=chunk.source_title,
                source_author=chunk.source_author,
                source_type=chunk.source_type,
                language=chunk.language,
                citation=chunk.citation,
                metadata={**chunk.metadata, "fusion": "rrf"},
            )
        )
    return fused_chunks
