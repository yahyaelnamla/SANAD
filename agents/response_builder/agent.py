"""Response Builder — formats verified analysis into structured output."""

import os
from pathlib import Path
from typing import Any

from agents.common.fanar_client import FanarLLMClient
from agents.intent_agent.models import IntentResult
from agents.knowledge_agent.models import EvidenceBundle
from agents.reasoning_agent.models import ReasoningResult
from agents.response_builder.models import FinalResponse
from agents.response_builder.tools import build_final_response, build_refusal_response
from config.fanar_api_keys import FANAR_MODELS

PROMPT_PATH = Path(__file__).parent / "prompt.md"

SKIP_RESPONSE_SUMMARY_LLM = os.getenv("SKIP_RESPONSE_SUMMARY_LLM", "true").lower() in {
    "1",
    "true",
    "yes",
}


class ResponseBuilder:
    """Build the final structured response for the user."""

    def __init__(self, llm_client: FanarLLMClient | None = None) -> None:
        self.llm = llm_client or FanarLLMClient()
        self.system_prompt = PROMPT_PATH.read_text(encoding="utf-8")

    async def build(
        self,
        bundle: EvidenceBundle,
        reasoning: ReasoningResult,
        intent: IntentResult,
        agent_trace: list[dict[str, Any]] | None = None,
        confidence_breakdown: dict[str, float] | None = None,
        financial_context: dict[str, Any] | None = None,
        execution_metrics: dict[str, Any] | None = None,
    ) -> FinalResponse:
        """Format verified analysis into FinalResponse."""
        if not bundle.has_valid_evidence:
            return build_refusal_response(
                "No authenticated evidence available.",
                language=intent.language,
                agent_trace=agent_trace,
            )

        summary: str | None = None
        if not SKIP_RESPONSE_SUMMARY_LLM:
            try:
                depth_hint = ""
                if execution_metrics and execution_metrics.get("pipeline_depth") == "fast":
                    depth_hint = (
                        "\nUse a natural, conversational tone. "
                        "The brief summary field should be 2–3 sentences only."
                    )
                elif execution_metrics and execution_metrics.get("pipeline_depth") == "deep":
                    depth_hint = (
                        "\nThe analysis is comprehensive — your summary field is only "
                        "a 3–4 sentence wrap-up conclusion, not a shortened version."
                    )
                elif execution_metrics and execution_metrics.get("pipeline_depth") == "standard":
                    depth_hint = (
                        "\nThe analysis is concise — your summary field is a 2–3 sentence "
                        "closing only. Do not repeat the full answer."
                    )
                else:
                    depth_hint = (
                        "\nYour summary field is ONLY a brief closing conclusion (2–4 sentences). "
                        "Do not shorten or repeat the full analysis."
                    )

                result = await self.llm.complete_json(
                    model=FANAR_MODELS["generation_ar"],
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {
                            "role": "user",
                            "content": (
                                f"Language: {intent.language}\n"
                                f"Analysis: {reasoning.analysis}\n"
                                f"Write the brief conclusion in {'Arabic' if intent.language == 'ar' else 'English'} only.\n"
                                "Generate ONLY a brief closing conclusion (2–4 sentences). "
                                "Do not include citations or URLs."
                                f"{depth_hint}"
                            ),
                        },
                    ],
                )
                summary = result.get("summary")
            except RuntimeError:
                summary = None

        return build_final_response(
            bundle=bundle,
            reasoning=reasoning,
            language=intent.language,
            summary=summary,
            agent_trace=agent_trace,
            confidence_breakdown=confidence_breakdown,
            financial_context=financial_context,
            execution_metrics=execution_metrics,
        )
