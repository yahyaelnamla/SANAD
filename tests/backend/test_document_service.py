"""Unit tests for document analysis service."""

import io

import pytest
from pypdf import PdfReader

from backend.app.exceptions import ValidationError
from backend.app.services.document_service import analyze_pdf


def _build_sample_pdf(text: str) -> bytes:
    content = (
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
        b"4 0 obj\n<< /Length "
        + str(len(text) + 50).encode()
        + b" >>\nstream\nBT /F1 12 Tf 72 720 Td ("
        + text.encode()
        + b") Tj ET\nendstream\nendobj\n"
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
        b"xref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n"
        b"0000000115 00000 n \n0000000260 00000 n \n0000000400 00000 n \n"
        b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n500\n%%EOF"
    )
    return content


def test_analyze_pdf_detects_interest_keywords() -> None:
    pdf_bytes = _build_sample_pdf("Annual report with interest income and revenue: 1,250,000")
    result, search_text = analyze_pdf(pdf_bytes, "report.pdf", language="en")

    assert result.page_count >= 1
    assert result.summary
    assert search_text
    assert any("interest" in finding.label.lower() for finding in result.riba_findings)
    assert result.key_findings


def test_analyze_pdf_rejects_non_pdf() -> None:
    with pytest.raises(ValidationError):
        analyze_pdf(b"hello", "notes.txt")
