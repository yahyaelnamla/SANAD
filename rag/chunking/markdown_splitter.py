"""Markdown-aware text splitter."""

import re

from rag.chunking.base import TextChunk
from rag.chunking.text_splitter import split_text


def split_markdown(
    markdown: str,
    chunk_size: int = 800,
    chunk_overlap: int = 120,
    metadata: dict | None = None,
) -> list[TextChunk]:
    """Split markdown by headings, then apply character splitting per section."""
    sections = re.split(r"(?=^#{1,6}\s)", markdown, flags=re.MULTILINE)
    base_metadata = metadata or {}
    chunks: list[TextChunk] = []
    index = 0

    for section in sections:
        section = section.strip()
        if not section:
            continue
        heading_match = re.match(r"^(#{1,6})\s+(.+)$", section, flags=re.MULTILINE)
        section_meta = {**base_metadata, "format": "markdown"}
        if heading_match:
            section_meta["heading"] = heading_match.group(2).strip()
            section_meta["heading_level"] = len(heading_match.group(1))

        section_chunks = split_text(
            section,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            metadata=section_meta,
        )
        for chunk in section_chunks:
            chunks.append(
                TextChunk(
                    content=chunk.content,
                    chunk_index=index,
                    metadata=chunk.metadata,
                )
            )
            index += 1

    if not chunks:
        return split_text(markdown, chunk_size, chunk_overlap, base_metadata)

    return chunks
