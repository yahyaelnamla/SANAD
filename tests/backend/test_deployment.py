"""Tests for deployment configuration and infrastructure."""

from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.workers.celery_app import celery_app
from backend.app.workers.tasks import ping

ROOT = Path(__file__).resolve().parents[2]


def test_docker_compose_prod_exists() -> None:
    assert (ROOT / "docker-compose.prod.yml").is_file()


def test_docker_compose_prod_parses() -> None:
    text = (ROOT / "docker-compose.prod.yml").read_text(encoding="utf-8")
    for service in ("nginx", "backend", "frontend", "celery-worker", "postgres", "redis"):
        assert f"{service}:" in text


def test_nginx_config_exists() -> None:
    nginx_conf = ROOT / "deploy" / "nginx" / "nginx.conf"
    assert nginx_conf.is_file()
    text = nginx_conf.read_text(encoding="utf-8")
    assert "sanad_backend" in text
    assert "sanad_frontend" in text


def test_frontend_dockerfile_exists() -> None:
    assert (ROOT / "frontend" / "Dockerfile").is_file()


def test_docker_entrypoint_exists() -> None:
    entrypoint = ROOT / "scripts" / "docker-entrypoint.sh"
    assert entrypoint.is_file()
    assert "alembic upgrade head" in entrypoint.read_text(encoding="utf-8")


def test_celery_app_configured() -> None:
    assert celery_app.main == "sanad"
    assert "backend.app.workers.tasks" in celery_app.conf.include


def test_celery_ping_task_registered() -> None:
    assert ping.name == "sanad.ping"


def test_liveness_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"


def test_metrics_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/health/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "sanad-backend"
    assert "uptime_seconds" in data
    assert data["version"] == "0.1.0"


def test_readiness_endpoint_schema(client: TestClient) -> None:
    response = client.get("/api/v1/health/ready")
    data = response.json()
    assert "status" in data
    assert "checks" in data
    assert "database" in data["checks"]
    assert "redis" in data["checks"]
    assert response.status_code in (200, 503)
