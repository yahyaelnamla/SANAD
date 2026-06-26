"""HTML text splitter."""

from bs4 import BeautifulSoup

from rag.chunking.base import TextChunk
from rag.chunking.text_splitter import split_text


def split_html(
    html: str,
    chunk_size: int = 800,
    chunk_overlap: int = 120,
    metadata: dict | None = None,
) -> list[TextChunk]:
    """Strip HTML tags and split the extracted text."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    base_metadata = {**(metadata or {}), "format": "html"}
    return split_text(text, chunk_size, chunk_overlap, base_metadata)
