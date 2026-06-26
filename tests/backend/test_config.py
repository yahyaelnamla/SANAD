"""Tests for application configuration."""

import pytest

from backend.app.config.settings import Settings, get_settings
from config.fanar_api_keys import FANAR_MODELS, get_fanar_api_key


def test_settings_defaults() -> None:
    """Settings should have sensible defaults."""
    settings = Settings()
    assert settings.app_name == "SANAD"
    assert settings.api_prefix == "/api/v1"
    assert settings.environment == "development"


def test_settings_cors_origins() -> None:
    """CORS origins should default to localhost frontend."""
    settings = Settings()
    assert "http://localhost:3000" in settings.cors_origins


def test_get_settings_is_cached() -> None:
    """get_settings should return the same cached instance."""
    get_settings.cache_clear()
    first = get_settings()
    second = get_settings()
    assert first is second


def test_fanar_models_defined() -> None:
    """All required Fanar models should be mapped."""
    expected = {
        "embedding",
        "agentic",
        "generation_ar",
        "reasoning",
        "guard",
        "rag",
        "translation",
        "stt",
        "tts",
        "vision",
    }
    assert expected == set(FANAR_MODELS.keys())


def test_fanar_api_key_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fanar API key should load from environment variable."""
    monkeypatch.setenv("FANAR_API_KEY", "test-key-123")
    assert get_fanar_api_key() == "test-key-123"


def test_fanar_api_key_missing_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    """Missing Fanar API key should raise ValueError."""
    monkeypatch.delenv("FANAR_API_KEY", raising=False)
    with pytest.raises(ValueError, match="FANAR_API_KEY"):
        get_fanar_api_key()
