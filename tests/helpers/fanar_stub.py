"""Deterministic Fanar client for unit/integration tests (no live HTTP)."""

import json
from typing import Any

from agents.common.fanar_client import FanarLLMClient


class DeterministicFanarClient(FanarLLMClient):
    """Test double returning predictable structured responses."""

    def __init__(self, api_key=None, timeout=None, **kwargs):
        super().__init__(api_key=api_key, base_url="https://test.fanar.local/v1")

    def _split_thinking(self, raw: str) -> tuple[str, str]:    # ← add this method
        """Split thinking tags from raw response."""
        import re
        thinking_match = re.search(r"<thinking>(.*?)</thinking>", raw, re.DOTALL)
        thinking = thinking_match.group(1).strip() if thinking_match else ""
        clean = re.sub(r"<thinking>.*?</thinking>", "", raw, flags=re.DOTALL).strip()
        return thinking, clean

    async def complete_json(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        enable_thinking: bool = False,
    ) -> dict[str, Any]:
        raw = await self.complete(
            model=model,
            messages=messages,
            temperature=temperature,
            enable_thinking=enable_thinking,
            response_format={"type": "json_object"},
        )
        text = raw.strip()
        if text.startswith("<thinking>"):
            text = text.split("</thinking>", 1)[-1].strip()
        if text.startswith("```"):
            import re

            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
        return json.loads(text)

    async def complete(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        response_format: dict[str, str] | None = None,
        enable_thinking: bool = False,
        max_tokens: int | None = None,
        extra: dict[str, Any] | None = None,
    ) -> str:
        user_text = " ".join(
            m.get("content", "") for m in messages if m.get("role") == "user"
        )
        self._record_usage({"usage": {"total_tokens": max(32, len(user_text) // 4)}})
        combined = user_text.lower()

        if enable_thinking or ("takyeef" in user_text and "analysis" in user_text):
            citation = "Scholars. Majallah."
            if "majallah" in combined:
                import re

                match = re.search(r"\[\d+\]\s*([^\n]+)", user_text)
                if match:
                    citation = match.group(1).strip()
            body = json.dumps(
                {
                    "principles_applied": ["Prohibition of Riba"],
                    "qawaid_fiqhiyya": ["Prohibition of Riba"],
                    "adilla": [citation],
                    "reasoning_steps": [
                        "Reviewed authenticated evidence on riba.",
                        "Applied classical fiqh principles across madhabs.",
                    ],
                    "analysis": (
                        "Based on authenticated evidence, riba is categorically prohibited "
                        "in Islamic law across all major madhabs."
                    ),
                    "opinions": [
                        {
                            "scholar": "Classical Consensus",
                            "position": "Riba is haram without exception for guaranteed loan increase.",
                            "citations": [citation],
                        }
                    ],
                    "confidence": 0.92,
                }
            )
            return f"<thinking>Applied qawa'id fiqhiyya on riba prohibition.</thinking>\n{body}"

        if "analyze this query" in combined:
            return json.dumps(
                {
                    "intent_type": "shariah_ruling",
                    "domain": "islamic_finance",
                    "language": "ar" if any("\u0600" <= c <= "\u06ff" for c in combined) else "en",
                    "entities": ["riba"] if "riba" in combined else ["crypto"] if "bitcoin" in combined else ["general_inquiry"],
                    "keywords": ["riba", "prohibition"] if "riba" in combined else ["finance"],
                }
            )

        if "plan execution" in combined or "decompose" in combined:
            return json.dumps(
                {
                    "steps": [
                        "intent",
                        "retrieval",
                        "knowledge",
                        "financial",
                        "reasoning",
                        "verification",
                        "response",
                    ],
                    "requires_financial_context": "stock" in combined or "tesla" in combined,
                    "rationale": "Standard Shariah financial reasoning pipeline.",
                }
            )

        if "extract applicable fiqh principles" in combined:
            return json.dumps(
                {
                    "principles": [
                        {
                            "name": "Prohibition of Riba",
                            "description": "Any guaranteed increase on a loan is prohibited.",
                            "citation": "Qur'an 2:275",
                        }
                    ]
                }
            )

        if "generate a concise summary" in combined:
            return json.dumps(
                {
                    "summary": "Riba is categorically prohibited in Islamic law.",
                    "confidence": 0.92,
                }
            )

        if "follow-up questions" in combined or '"questions"' in combined:
            return json.dumps(
                {
                    "questions": [
                        "What do scholars say about Shariah-compliant ETFs?",
                        "Is Tesla AAOIFI compliant?",
                    ]
                }
            )

        if "rewrite the user's follow-up" in combined:
            return "What is the Shariah ruling on the topic discussed in the prior answer?"

        return json.dumps({"result": "ok", "model": model})

    async def moderate(self, *, prompt: str, response: str) -> dict[str, Any]:
        return {"safety": 0.95, "cultural_awareness": 0.93}

    async def retrieve_knowledge(
        self,
        query: str,
        *,
        language: str | None = None,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        return []

    async def complete_with_thinking(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        temperature: float = 0.2,
        max_tokens: int = 4000,
    ) -> tuple[str | None, str]:
        raw = await self.complete(
            model=model,
            messages=messages,
            temperature=temperature,
            enable_thinking=True,
            max_tokens=max_tokens,
        )
        return self._split_thinking(raw)
