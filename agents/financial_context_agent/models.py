"""Financial Context Agent data models."""

from typing import Any

from pydantic import BaseModel, Field


class FinancialProduct(BaseModel):
    """Basic financial product context."""

    name: str
    category: str
    description: str


class MarketQuote(BaseModel):
    """Live market quote for Shariah screening context."""

    symbol: str
    price: float | None = None
    currency: str | None = None
    market_cap: float | None = None
    exchange: str | None = None


class FinancialContext(BaseModel):
    """Financial context enriched for jurisprudential adaptation."""

    entities: list[str] = Field(default_factory=list)
    products: list[FinancialProduct] = Field(default_factory=list)
    market_quotes: list[MarketQuote] = Field(default_factory=list)
    notes: str = ""
    has_external_data: bool = False
    screening_notes: list[str] = Field(default_factory=list)

    def to_api_dict(self) -> dict[str, Any]:
        """Serialize for API responses."""
        return self.model_dump()
