"""Tests for auto mode detection."""

from backend.app.services.auto_mode_service import (
    auto_mode_requires_financial,
    detect_auto_mode,
)


def test_detect_company_mode():
    assert detect_auto_mode("Is Tesla halal according to AAOIFI?") == "company"


def test_detect_portfolio_mode():
    assert detect_auto_mode("Screen my portfolio for halal compliance") == "portfolio"


def test_detect_document_mode():
    assert detect_auto_mode("What did my uploaded PDF report say about debt?") == "document"


def test_detect_fast_mode():
    assert detect_auto_mode("Is riba haram?") == "fast"


def test_company_requires_financial():
    assert auto_mode_requires_financial("company") is True
