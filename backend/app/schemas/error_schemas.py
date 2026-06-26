"""Standardized API error response schemas."""

from typing import Any

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Consistent error payload for all API failures."""

    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
