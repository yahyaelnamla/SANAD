"""Optional Docling-based PDF text extraction."""

from __future__ import annotations

import logging
import sys
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

DOCLING_ROOT = Path(__file__).resolve().parent.parent / "tools" / "docling-main"


def _ensure_docling_path() -> None:
    root = str(DOCLING_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)


def extract_pdf_text_with_docling(content: bytes, filename: str = "document.pdf") -> str | None:
    """Extract text from a PDF using vendored Docling when dependencies are available."""
    if not DOCLING_ROOT.is_dir():
        return None

    try:
        _ensure_docling_path()
        from docling.document_converter import DocumentConverter

        suffix = Path(filename).suffix or ".pdf"
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(content)
            tmp_path = Path(tmp.name)

        converter = DocumentConverter()
        result = converter.convert(str(tmp_path))
        text = result.document.export_to_markdown() or ""
        tmp_path.unlink(missing_ok=True)

        cleaned = text.strip()
        if len(cleaned) < 40:
            return None
        logger.info("Docling extracted %d chars from %s", len(cleaned), filename)
        return cleaned
    except Exception as exc:
        logger.warning("Docling extraction unavailable for %s: %s", filename, exc)
        return None
