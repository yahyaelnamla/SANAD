"""Tests for reranking and score fusion."""

from uuid import uuid4

from rag.rerankers.cross_encoder_reranker import CrossEncoderReranker
from rag.rerankers.diversity_reranker import DiversityReranker
from rag.rerankers.score_fusion import reciprocal_rank_fusion
from rag.retrievers.base import RetrievedChunk


def _chunk(content: str, score: float) -> RetrievedChunk:
    chunk_id = uuid4()
    source_id = uuid4()
    return RetrievedChunk(
        chunk_id=chunk_id,
        source_id=source_id,
        content=content,
        score=score,
        source_title="Title",
        source_author="Author",
        source_type="classical",
        language="ar",
        citation="Author. Title.",
        metadata={"is_authenticated": True},
    )


def test_reciprocal_rank_fusion_merges_lists() -> None:
    list_a = [_chunk("riba prohibition", 0.9), _chunk("other topic", 0.5)]
    list_b = [_chunk("other topic", 0.8), _chunk("riba prohibition", 0.6)]
    fused = reciprocal_rank_fusion([list_a, list_b], top_k=2)
    assert len(fused) == 2
    contents = {chunk.content for chunk in fused}
    assert "riba prohibition" in contents


def test_cross_encoder_prefers_lexical_overlap() -> None:
    reranker = CrossEncoderReranker()
    chunks = [
        _chunk("Unrelated economic theory", 0.9),
        _chunk("Riba is prohibited in Islam", 0.4),
    ]
    reranked = reranker.rerank("riba prohibition", chunks, top_k=2)
    assert reranked[0].content == "Riba is prohibited in Islam"


def test_diversity_reranker_limits_redundancy() -> None:
    reranker = DiversityReranker()
    chunks = [
        _chunk("Riba is haram in Islamic law", 0.9),
        _chunk("Riba is forbidden under Shariah", 0.85),
        _chunk("Murabaha is a valid contract", 0.7),
    ]
    reranked = reranker.rerank(chunks, top_k=2)
    assert len(reranked) == 2
    contents = [chunk.content for chunk in reranked]
    assert any("Murabaha" in text for text in contents)
