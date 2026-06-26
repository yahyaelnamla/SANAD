"""Retrieval module exports."""

from rag.retrievers.base import RetrievedChunk, build_retrieved_chunk
from rag.retrievers.metadata_filter import MetadataFilter

__all__ = [
    "HybridRetriever",
    "KeywordRetriever",
    "MetadataFilter",
    "RetrievedChunk",
    "VectorRetriever",
    "build_retrieved_chunk",
]


def __getattr__(name: str):
    """Lazy-load retriever implementations to avoid circular imports."""
    if name == "VectorRetriever":
        from rag.retrievers.vector_retriever import VectorRetriever

        return VectorRetriever
    if name == "KeywordRetriever":
        from rag.retrievers.keyword_retriever import KeywordRetriever

        return KeywordRetriever
    if name == "HybridRetriever":
        from rag.retrievers.hybrid_retriever import HybridRetriever

        return HybridRetriever
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
