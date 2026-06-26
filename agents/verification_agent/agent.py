"""Verification Agent — FanarGuard citation check and hallucination guard."""

from pathlib import Path

from config.fanar_api_keys import FANAR_MODELS
from agents.common.fanar_client import FanarLLMClient
from agents.knowledge_agent.models import EvidenceBundle
from agents.reasoning_agent.models import ReasoningResult
from agents.verification_agent.models import VerificationIssue, VerificationResult
from agents.verification_agent.tools import (
    check_analysis_content,
    check_citations,
    check_hallucination_risk,
    check_opinion_citations,
)

PROMPT_PATH = Path(__file__).parent / "prompt.md"


class VerificationAgent:
    """Validate reasoning output against integrity rules and FanarGuard."""

    def __init__(self, llm_client: FanarLLMClient | None = None) -> None:
        self.llm = llm_client or FanarLLMClient()
        self.system_prompt = PROMPT_PATH.read_text(encoding="utf-8")

    async def verify(
        self,
        reasoning: ReasoningResult,
        bundle: EvidenceBundle,
        *,
        user_query: str = "",
        depth: str = "standard",
    ) -> VerificationResult:
        """Run integrity checks and FanarGuard moderation on the reasoning output."""
        issues: list[VerificationIssue] = []
        issues.extend(check_citations(reasoning, bundle))
        issues.extend(check_analysis_content(reasoning))
        issues.extend(check_opinion_citations(reasoning, bundle))
        issues.extend(check_hallucination_risk(reasoning, bundle))

        blocking_codes = {
            "EMPTY_ANALYSIS",
            "ZERO_CONFIDENCE",
            "UNGROUNDED_ADILLA",
            "MISSING_CITATIONS",
        }
        blocking = [issue for issue in issues if issue.code in blocking_codes]
        if blocking:
            return VerificationResult(
                approved=False,
                issues=issues,
                reason="; ".join(i.message for i in blocking),
            )

        non_blocking = [issue for issue in issues if issue.code not in blocking_codes]
        if non_blocking and depth == "deep":
            try:
                _, judgment = await self.llm.complete_with_thinking(
                    model=FANAR_MODELS["reasoning"],
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {
                            "role": "user",
                            "content": (
                                f"User query: {user_query}\n"
                                f"Analysis to verify:\n{reasoning.analysis[:1500]}\n"
                                f"Warnings: {[i.message for i in non_blocking]}\n"
                                "Is this analysis still correct and safe? Reply YES or NO with reason."
                            ),
                        },
                    ],
                    max_tokens=1000,
                )
                if judgment.strip().upper().startswith("NO"):
                    return VerificationResult(
                        approved=False,
                        issues=non_blocking,
                        reason=judgment[:300],
                    )
            except RuntimeError:
                pass

        moderation = await self.llm.moderate(
            prompt=user_query or reasoning.analysis[:500],
            response=reasoning.analysis,
        )
        passes, guard_reason = self.llm.passes_guard(moderation)
        if not passes:
            return VerificationResult(
                approved=False,
                issues=[
                    VerificationIssue(
                        code="GUARD_REJECTION",
                        message=guard_reason or "FanarGuard rejected the response.",
                    )
                ],
                reason=guard_reason,
                guard_scores=moderation,
            )

        return VerificationResult(approved=True, guard_scores=moderation)
