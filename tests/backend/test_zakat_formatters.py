"""Tests for Zakat quantity/unit display formatters."""

from backend.app.services.zakat_formatters import format_quantity_display, format_unit_price_display


def test_gold_quantity_uses_grams_not_currency() -> None:
    assert format_quantity_display(category="gold", amount=50, currency="USD", quantity=50) == "50 g"


def test_stock_quantity_uses_shares() -> None:
    assert (
        format_quantity_display(category="stock", amount=10, currency="USD", quantity=10, label="AAPL")
        == "10 shares"
    )


def test_crypto_quantity_uses_symbol() -> None:
    assert (
        format_quantity_display(category="crypto", amount=0.25, currency="USD", quantity=0.25, label="BTC")
        == "0.25 BTC"
    )


def test_cash_quantity_uses_currency_amount() -> None:
    assert format_quantity_display(category="cash", amount=10000, currency="USD") == "10,000.00 USD"


def test_gold_unit_price_per_gram() -> None:
    assert format_unit_price_display(category="gold", unit_price=75.5, currency="USD") == "75.50 USD/g"
