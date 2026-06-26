"""Tests for health and version API endpoints."""

from fastapi.testclient import TestClient


def test_health_endpoint_returns_healthy(client: TestClient) -> None:
    """Health check should return status healthy."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "sanad-backend"


def test_version_endpoint_returns_version(client: TestClient) -> None:
    """Version endpoint should return current API version."""
    response = client.get("/api/v1/version")
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "0.1.0"
    assert data["api"] == "v1"


def test_openapi_docs_available(client: TestClient) -> None:
    """OpenAPI schema should be accessible."""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "SANAD"
