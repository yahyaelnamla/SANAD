"""Backend interface to the multi-agent system.

Import ONLY from this module. Do not reach into agents.* sub-packages directly.
This file is the public contract.
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from agents.common.state import AgentPipelineState
from agents.response_builder.models import FinalResponse

__all__ = ["AgentPipelineState", "FinalResponse", "AgentOrchestratorProtocol"]


@runtime_checkable
class AgentOrchestratorProtocol(Protocol):
    """Structural type for the orchestrator — use for DI and testing."""

    async def process_query(
        self,
        query: str,
        *,
        user_id: object | None = None,
        top_k: int = 5,
        advanced_analysis: bool = False,
        preferred_language: str | None = None,
        fanar_model: str = "auto",
        session_id: str | None = None,
        conversation_history: list[dict[str, str]] | None = None,
        query_id: object | None = None,
    ) -> FinalResponse: ...
