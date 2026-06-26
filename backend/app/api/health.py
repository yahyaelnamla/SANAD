"""Health and meta API endpoints."""

from fastapi import APIRouter, Response

from backend.app.services.health_service import HealthService

router = APIRouter(tags=["Health"])
_health = HealthService()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Return basic service health status."""
    return {"status": "healthy", "service": "sanad-backend"}


@router.get("/health/live")
async def liveness() -> dict[str, str]:
    """Kubernetes-style liveness probe — process is running."""
    return {"status": "alive", "service": "sanad-backend"}


@router.get("/health/ready")
async def readiness(response: Response) -> dict:
    """Readiness probe — database and Redis must be reachable."""
    report = await _health.readiness()
    if report["status"] != "ready":
        response.status_code = 503
    return report


@router.get("/health/metrics")
async def metrics() -> dict:
    """Lightweight runtime metrics for monitoring."""
    return _health.metrics()


@router.get("/version")
async def version_info() -> dict[str, str]:
    """Return API version information."""
    from backend.app.config.settings import get_settings

    settings = get_settings()
    return {"version": settings.app_version, "api": "v1"}
