"""Lexical reranker combining vector score with keyword overlap."""

import re

from rag.retrievers.base import RetrievedChunk


def _tokenize(text: str) -> set[str]:
    return {token for token in re.findall(r"\w+", text.lower()) if len(token) > 2}


class CrossEncoderReranker:
    """Lightweight reranker using lexical overlap (Phase 2 stand-in)."""

    def rerank(
        self,
        query: str,
        chunks: list[RetrievedChunk],
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        """Rerank chunks by combining retrieval score with lexical overlap."""
        query_tokens = _tokenize(query)
        if not query_tokens:
            return chunks[:top_k]

        scored: list[tuple[float, RetrievedChunk]] = []
        for chunk in chunks:
            chunk_tokens = _tokenize(chunk.content)
            overlap = len(query_tokens & chunk_tokens) / max(len(query_tokens), 1)
            combined = (0.4 * chunk.score) + (0.6 * overlap)
            scored.append((combined, chunk))

        scored.sort(key=lambda item: item[0], reverse=True)
        reranked: list[RetrievedChunk] = []
        for combined_score, chunk in scored[:top_k]:
            reranked.append(
                RetrievedChunk(
                    chunk_id=chunk.chunk_id,
                    source_id=chunk.source_id,
                    content=chunk.content,
                    score=combined_score,
                    source_title=chunk.source_title,
                    source_author=chunk.source_author,
                    source_type=chunk.source_type,
                    language=chunk.language,
                    citation=chunk.citation,
                    metadata={**chunk.metadata, "reranker": "cross_encoder_lexical"},
                )
            )
        return reranked
