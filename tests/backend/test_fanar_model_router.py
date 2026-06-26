"""Tests for Fanar model routing."""

from backend.app.services.fanar_model_router import fanar_capabilities_manifest, model_for_task
from config.fanar_api_keys import FANAR_MODELS


def test_model_for_task_reasoning_uses_c27b_on_deep():
    assert model_for_task("reasoning", depth="deep") == FANAR_MODELS["reasoning"]


def test_model_for_task_verification_always_guard():
    assert model_for_task("verification") == FANAR_MODELS["guard"]


def test_fanar_capabilities_manifest_lists_products():
    manifest = fanar_capabilities_manifest()
    assert "Fanar-Sadiq" in manifest
    assert "Fanar-Guard-2" in manifest
    assert "Fanar-Oryx-IVU-2" in manifest


def test_model_for_task_sadiq_preference():
    assert model_for_task("reasoning", depth="deep", preference="sadiq") == FANAR_MODELS["generation_ar"]
    assert model_for_task("reasoning", depth="deep", preference="c2") == FANAR_MODELS["reasoning"]
