"""Fanar API configuration — keys and model identifiers from environment."""

import os

FANAR_API_BASE_URL = os.getenv("FANAR_API_BASE_URL", "https://api.fanar.qa/v1")
FANAR_ORGANIZATION = os.getenv("FANAR_ORGANIZATION", "QCRI-Hackathon")

# Official Fanar API model identifiers (OpenAPI spec).
# Fanar-Sadiq-Agentic requires extra authorization; default agentic uses Fanar-Sadiq.
FANAR_MODELS = {
    "embedding": "Fanar",
    "agentic": os.getenv("FANAR_AGENTIC_MODEL", "Fanar-Sadiq"),
    "generation_ar": "Fanar-Sadiq",
    "reasoning": os.getenv("FANAR_REASONING_MODEL", "Fanar-C-2-27B"),
    "guard": "Fanar-Guard-2",
    "rag": "Fanar-Sadiq",
    "translation": "Fanar-Shaheen-MT-1",
    "stt": "Fanar-Aura-STT-1",
    "tts": "Fanar-Aura-TTS-2",
    "vision": os.getenv("FANAR_VISION_MODEL", "Fanar-Oryx-IVU-2"),
}

# FanarGuard moderation thresholds (0–1, higher = safer)
FANAR_GUARD_MIN_SAFETY = float(os.getenv("FANAR_GUARD_MIN_SAFETY", "0.7"))
FANAR_GUARD_MIN_CULTURAL = float(os.getenv("FANAR_GUARD_MIN_CULTURAL", "0.7"))


def get_fanar_api_key() -> str:
    """Return the Fanar API key from environment."""
    key = os.getenv("FANAR_API_KEY", "")
    if not key:
        raise ValueError(
            "FANAR_API_KEY environment variable is not set. "
            "See .env.example for configuration."
        )
    return key
