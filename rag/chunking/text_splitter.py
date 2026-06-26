"""Recursive character-based text splitter."""

from rag.chunking.base import TextChunk


def split_text(
    text: str,
    chunk_size: int = 800,
    chunk_overlap: int = 120,
    metadata: dict | None = None,
) -> list[TextChunk]:
    """Split text into overlapping chunks by character count."""
    if chunk_size <= chunk_overlap:
        raise ValueError("chunk_size must be greater than chunk_overlap")

    base_metadata = metadata or {}
    chunks: list[TextChunk] = []
    start = 0
    index = 0

    while start < len(text):
        end = start + chunk_size
        piece = text[start:end].strip()
        if piece:
            chunks.append(
                TextChunk(
                    content=piece,
                    chunk_index=index,
                    metadata={**base_metadata, "start_char": start, "end_char": end},
                )
            )
            index += 1
        if end >= len(text):
            break
        start = end - chunk_overlap

    if not chunks:
        raise ValueError("No chunks produced from input text")

    return chunks
