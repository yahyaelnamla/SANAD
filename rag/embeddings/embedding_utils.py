"""Embedding utility functions."""

import hashlib
import math

from backend.app.models.source_chunk import EMBEDDING_DIMENSION


def validate_embedding(embedding: list[float]) -> list[float]:
    """Validate embedding dimension and numeric values."""
    if len(embedding) != EMBEDDING_DIMENSION:
        raise ValueError(
            f"Expected embedding dimension {EMBEDDING_DIMENSION}, got {len(embedding)}"
        )
    if not all(isinstance(value, (int, float)) and math.isfinite(value) for value in embedding):
        raise ValueError("Embedding must contain finite numeric values")
    return embedding


def normalize_embedding(embedding: list[float]) -> list[float]:
    """L2-normalize an embedding vector."""
    validated = validate_embedding(embedding)
    norm = math.sqrt(sum(value * value for value in validated))
    if norm == 0:
        return validated
    return [value / norm for value in validated]


def deterministic_mock_embedding(text: str) -> list[float]:
    """Generate a deterministic mock embedding for tests."""
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    values: list[float] = []
    while len(values) < EMBEDDING_DIMENSION:
        for byte in digest:
            values.append((byte / 255.0) * 2 - 1)
            if len(values) == EMBEDDING_DIMENSION:
                break
        digest = hashlib.sha256(digest).digest()
    return normalize_embedding(values)
