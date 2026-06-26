"""Application configuration loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """SANAD application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "SANAD"
    app_version: str = "0.1.0"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False

    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:3000"]

    database_url: str = "postgresql+asyncpg://sanad:sanad@localhost:5433/sanad"
    test_database_url: str = "postgresql+asyncpg://sanad:sanad@localhost:5433/sanad_test"
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    log_level: str = "INFO"

    fanar_api_key: str = ""
    fanar_api_base_url: str = "https://api.fanar.qa/v1"
    fanar_organization: str = "QCRI-Hackathon"

    # Market data providers
    alpha_vantage_api_key: str = ""
    massive_api_key: str = ""

    # Web search providers (retrieval enrichment)
    serper_api_key: str = ""
    tavily_api_key: str = ""
    langsearch_api_key: str = ""

    # Neo4j knowledge graph (optional)
    neo4j_uri: str = ""
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""
    neo4j_database: str = "neo4j"

    # Long Fanar pipelines exceed Next.js proxy timeouts; run async by default.
    query_async: bool = True

    platform_api_key: str = ""

    # SSO (OAuth2) — demo mode enabled when client secrets are absent
    sso_demo_mode: bool = True
    sso_redirect_uri: str = "http://localhost:3000/auth/sso/callback"
    google_client_id: str = ""
    google_client_secret: str = ""
    microsoft_client_id: str = ""
    microsoft_client_secret: str = ""


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
