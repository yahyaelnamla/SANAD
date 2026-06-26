"""Tests for Fanar embedding integration."""

import pytest

from backend.app.models.source_chunk import EMBEDDING_DIMENSION
from rag.embeddings.embedding_utils import deterministic_mock_embedding, normalize_embedding
from tests.helpers.embedding_stub import DeterministicEmbeddingModel


@pytest.mark.asyncio
async def test_deterministic_embedding_dimension() -> None:
    model = DeterministicEmbeddingModel()
    embedding = await model.embed_text("هل الربا حرام؟")
    assert len(embedding) == EMBEDDING_DIMENSION


@pytest.mark.asyncio
async def test_batch_embeddings_match_input_count() -> None:
    model = DeterministicEmbeddingModel()
    texts = ["Bitcoin trading", "Shariah compliance", "Murabaha contract"]
    embeddings = await model.embed_texts(texts)
    assert len(embeddings) == 3


def test_deterministic_mock_is_normalized() -> None:
    embedding = deterministic_mock_embedding("same text")
    normalized = normalize_embedding(embedding)
    magnitude = sum(value * value for value in normalized) ** 0.5
    assert abs(magnitude - 1.0) < 1e-6


def test_same_text_produces_same_mock_embedding() -> None:
    first = deterministic_mock_embedding("evidence")
    second = deterministic_mock_embedding("evidence")
    assert first == second
