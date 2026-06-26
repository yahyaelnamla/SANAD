"""Vector store exports."""

__all__ = ["PgVectorClient", "VectorStoreManager"]


def __getattr__(name: str):
    """Lazy-load vector store implementations to avoid circular imports."""
    if name == "PgVectorClient":
        from rag.vectorstore.pgvector_client import PgVectorClient

        return PgVectorClient
    if name == "VectorStoreManager":
        from rag.vectorstore.vector_store_manager import VectorStoreManager

        return VectorStoreManager
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
