"""Mandatory Fanar-Guard-2 gate for all user-facing text outputs."""

from __future__ import annotations

from agents.common.fanar_client import FanarLLMClient


class OutputGuardService:
    """Run Fanar-Guard-2 with retries; fail closed when the guard API is unavailable."""

    def __init__(self, llm_client: FanarLLMClient | None = None) -> None:
        self.llm = llm_client or FanarLLMClient()

    async def guard_output(
        self,
        *,
        prompt: str,
        response: str,
    ) -> tuple[bool, str | None, dict]:
        """Return (passes, rejection_reason, moderation_scores)."""
        moderation = await self.llm.moderate(prompt=prompt, response=response)
        passes, reason = self.llm.passes_guard(moderation)
        return passes, reason, moderation
