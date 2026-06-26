"""Diversity-aware reranker using Maximal Marginal Relevance."""

from rag.retrievers.base import RetrievedChunk


def _jaccard(a: str, b: str) -> float:
    tokens_a = set(a.lower().split())
    tokens_b = set(b.lower().split())
    if not tokens_a or not tokens_b:
        return 0.0
    return len(tokens_a & tokens_b) / len(tokens_a | tokens_b)


class DiversityReranker:
    """Promote diverse evidence while preserving relevance."""

    def rerank(
        self,
        chunks: list[RetrievedChunk],
        top_k: int = 5,
        lambda_mult: float = 0.4,
    ) -> list[RetrievedChunk]:
        """Apply MMR-style diversity reranking."""
        if not chunks:
            return []

        selected: list[RetrievedChunk] = []
        remaining = chunks.copy()

        while remaining and len(selected) < top_k:
            best_score = -1.0
            best_index = 0
            for index, candidate in enumerate(remaining):
                relevance = candidate.score
                redundancy = max(
                    (_jaccard(candidate.content, chosen.content) for chosen in selected),
                    default=0.0,
                )
                mmr_score = (lambda_mult * relevance) - ((1 - lambda_mult) * redundancy)
                if mmr_score > best_score:
                    best_score = mmr_score
                    best_index = index

            chosen = remaining.pop(best_index)
            selected.append(
                RetrievedChunk(
                    chunk_id=chosen.chunk_id,
                    source_id=chosen.source_id,
                    content=chosen.content,
                    score=best_score,
                    source_title=chosen.source_title,
                    source_author=chosen.source_author,
                    source_type=chosen.source_type,
                    language=chosen.language,
                    citation=chosen.citation,
                    metadata={**chosen.metadata, "reranker": "diversity_mmr"},
                )
            )

        return selected
