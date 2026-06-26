"""Health check service with dependency probes."""

from __future__ import annotations

import time
from typing import Any

import redis
from sqlalchemy import text

from backend.app.config.database import engine
from backend.app.config.settings import get_settings

_START_TIME = time.monotonic()


class HealthService:
    """Probe application dependencies for liveness and readiness."""

    async def check_database(self) -> dict[str, Any]:
        """Verify PostgreSQL connectivity."""
        try:
            async with engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
            return {"status": "healthy", "message": "Database connection OK."}
        except Exception as exc:  # noqa: BLE001 — health probe must not raise
            return {"status": "unhealthy", "message": str(exc)}

    def check_redis(self) -> dict[str, Any]:
        """Verify Redis connectivity."""
        settings = get_settings()
        try:
            client = redis.from_url(settings.redis_url, socket_connect_timeout=2)
            client.ping()
            return {"status": "healthy", "message": "Redis connection OK."}
        except Exception as exc:  # noqa: BLE001
            return {"status": "unhealthy", "message": str(exc)}

    async def readiness(self) -> dict[str, Any]:
        """Aggregate readiness status for orchestrators."""
        database = await self.check_database()
        redis_status = self.check_redis()
        checks = {"database": database, "redis": redis_status}
        healthy = all(check["status"] == "healthy" for check in checks.values())
        return {
            "status": "ready" if healthy else "not_ready",
            "checks": checks,
        }

    def metrics(self) -> dict[str, Any]:
        """Return lightweight runtime metrics."""
        settings = get_settings()
        uptime_seconds = round(time.monotonic() - _START_TIME, 2)
        return {
            "service": "sanad-backend",
            "version": settings.app_version,
            "environment": settings.environment,
            "uptime_seconds": uptime_seconds,
        }
