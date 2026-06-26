"""User preferences schemas — madhhab, scholars, saved items, bookmarks."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

MadhhabChoice = Literal["hanafi", "maliki", "shafii", "hanbali", "general"]


class SavedBookmarkSchema(BaseModel):
    """Persisted bookmark with optional note and folder."""

    query_id: str = Field(..., max_length=64)
    question: str = Field(..., max_length=5000)
    summary: str | None = Field(default=None, max_length=8000)
    note: str | None = Field(default=None, max_length=2000)
    folder: str | None = Field(default=None, max_length=120)
    is_favorite: bool = False
    saved_at: str | None = None


class SavedPortfolioHoldingSchema(BaseModel):
    symbol: str = Field(..., max_length=12)
    quantity: float = Field(..., gt=0)
    asset_type: Literal["stock", "crypto", "etf", "fund", "reit"] = "stock"
    purchase_price: float | None = Field(default=None, ge=0)
    manual_price: float | None = Field(default=None, ge=0)
    use_market_price: bool = True


class SavedPortfolioSchema(BaseModel):
    id: str = Field(..., max_length=64)
    name: str = Field(..., max_length=120)
    holdings: list[SavedPortfolioHoldingSchema] = Field(default_factory=list, max_length=50)
    created_at: str
    last_scanned_at: str | None = None


class UserPreferencesSchema(BaseModel):
    """Full user preference profile."""

    display_name: str | None = Field(default=None, max_length=80)
    preferred_madhhab: MadhhabChoice | None = None
    favorite_scholars: list[str] = Field(default_factory=list, max_length=20)
    saved_companies: list[str] = Field(default_factory=list, max_length=50)
    saved_portfolios: list[str] = Field(default_factory=list, max_length=20)
    saved_portfolio_profiles: list[SavedPortfolioSchema] = Field(default_factory=list, max_length=10)
    recent_topics: list[str] = Field(default_factory=list, max_length=30)
    bookmarks: list[SavedBookmarkSchema] = Field(default_factory=list, max_length=200)


class UserPreferencesUpdateRequest(BaseModel):
    """Partial update for user preferences."""

    display_name: str | None = Field(default=None, max_length=80)
    preferred_madhhab: MadhhabChoice | None = None
    favorite_scholars: list[str] | None = Field(default=None, max_length=20)
    saved_companies: list[str] | None = Field(default=None, max_length=50)
    saved_portfolios: list[str] | None = Field(default=None, max_length=20)
    saved_portfolio_profiles: list[SavedPortfolioSchema] | None = Field(default=None, max_length=10)
    recent_topics: list[str] | None = Field(default=None, max_length=30)
    bookmarks: list[SavedBookmarkSchema] | None = Field(default=None, max_length=200)
