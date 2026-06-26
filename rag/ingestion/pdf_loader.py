"""PDF text extraction for SANAD knowledge ingestion."""

from pathlib import Path

from pypdf import PdfReader

from rag.ingestion.base import IngestedDocument


def load_pdf(
    file_path: str | Path,
    source_title: str,
    source_author: str,
    language: str = "ar",
) -> IngestedDocument:
    """Extract text from a PDF file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    reader = PdfReader(str(path))
    pages: list[str] = []
    for index, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            pages.append(text.strip())

    content = "\n\n".join(pages)
    if not content.strip():
        raise ValueError(f"No extractable text in PDF: {path}")

    return IngestedDocument(
        content=content,
        source_title=source_title,
        source_author=source_author,
        language=language,
        metadata={"format": "pdf", "page_count": len(reader.pages), "file_name": path.name},
    )
