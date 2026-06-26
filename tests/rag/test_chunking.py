"""Tests for text chunking strategies."""

from rag.chunking.html_splitter import split_html
from rag.chunking.markdown_splitter import split_markdown
from rag.chunking.text_splitter import split_text


def test_split_text_produces_overlapping_chunks() -> None:
    text = "word " * 500
    chunks = split_text(text, chunk_size=200, chunk_overlap=50)
    assert len(chunks) > 1
    assert chunks[0].chunk_index == 0
    assert all(chunk.content for chunk in chunks)


def test_split_markdown_respects_headings() -> None:
    markdown = "# Fiqh\n\nRiba is prohibited.\n\n## Evidence\n\nClassical sources agree."
    chunks = split_markdown(markdown, chunk_size=100, chunk_overlap=20)
    assert chunks
    assert any("heading" in chunk.metadata for chunk in chunks)


def test_split_html_strips_tags() -> None:
    html = "<html><body><p>Islamic finance</p><script>ignore</script></body></html>"
    chunks = split_html(html, chunk_size=100, chunk_overlap=10)
    assert len(chunks) == 1
    assert "Islamic finance" in chunks[0].content
    assert "ignore" not in chunks[0].content
