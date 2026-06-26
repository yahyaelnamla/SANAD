"""Format human-readable quantity and unit price labels for Zakat breakdown rows."""

from __future__ import annotations


def format_quantity_display(
    *,
    category: str,
    amount: float,
    currency: str,
    quantity: float | None = None,
    label: str = "",
) -> str:
    """Return a category-correct quantity string (not conflated with currency)."""
    if category == "gold":
        grams = quantity if quantity is not None else amount
        return f"{grams:g} g"
    if category == "cash":
        return f"{amount:,.2f} {currency}"
    if category == "debt":
        return f"{amount:,.2f} {currency}"
    if category == "stock":
        shares = quantity if quantity is not None else amount
        return f"{shares:g} shares"
    if category == "crypto":
        coins = quantity if quantity is not None else amount
        symbol = label.strip().upper() or "coins"
        return f"{coins:g} {symbol}"
    if quantity is not None:
        return f"{quantity:g}"
    return f"{amount:,.2f}"


def format_unit_price_display(
    *,
    category: str,
    unit_price: float | None,
    currency: str,
) -> str | None:
    """Return unit price with correct unit suffix per asset class."""
    if unit_price is None:
        return None
    if category == "gold":
        return f"{unit_price:,.2f} {currency}/g"
    if category in {"stock", "crypto"}:
        return f"{unit_price:,.2f} {currency}"
    return None
