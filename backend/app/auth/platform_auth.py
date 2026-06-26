"""Platform API key authentication for external integrations."""

from __future__ import annotations

from fastapi import Header, HTTPException

from backend.app.config.settings import get_settings


async def require_platform_api_key(
    x_platform_key: str | None = Header(default=None, alias="X-Platform-Key"),
) -> None:
    """Validate platform integration API key from header."""
    settings = get_settings()
    expected = (settings.platform_api_key or "").strip()
    if not expected:
        raise HTTPException(
            status_code=503,
            detail="Platform API is not configured on this deployment.",
        )
    if not x_platform_key or x_platform_key.strip() != expected:
        raise HTTPException(status_code=401, detail="Invalid platform API key.")
