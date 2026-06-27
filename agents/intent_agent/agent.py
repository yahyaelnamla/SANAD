"""Intent Agent — query understanding and entity extraction."""

from pathlib import Path

from agents.common.fanar_client import FanarLLMClient
from agents.intent_agent.models import IntentResult, IntentType
from agents.intent_agent.tools import (
    classify_intent,
    detect_language,
    extract_entities,
    extract_keywords,
)
from backend.app.services.conversation_memory_service import format_history_for_prompt
from config.fanar_api_keys import FANAR_MODELS

PROMPT_PATH = Path(__file__).parent / "prompt.md"


class IntentAgent:
    """Extract intent, entities, domain, and language from user queries."""

    def __init__(self, llm_client: FanarLLMClient | None = None) -> None:
        self.llm = llm_client or FanarLLMClient()
        self.system_prompt = PROMPT_PATH.read_text(encoding="utf-8")

    async def analyze(
        self,
        query: str,
        *,
        conversation_history: list[dict[str, str]] | None = None,
    ) -> IntentResult:
        """Analyze a user query and return structured intent."""
        language = detect_language(query)
        entities = extract_entities(query)
        keywords = extract_keywords(query)
        intent_type = classify_intent(query, entities)

        history_block = ""
        if conversation_history and len(conversation_history) >= 2:
            history_block = (
                "\n\nPrior conversation (resolve references like this/that/the previous ruling):\n"
                f"{format_history_for_prompt(conversation_history)}\n"
            )

        try:
            result = await self.llm.complete_json(
                model=FANAR_MODELS["agentic"],
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {
                        "role": "user",
                        "content": f"Analyze this query:\n{query}{history_block}",
                    },
                ],
            )
            return IntentResult(
                raw_query=query,
                intent_type=IntentType(result.get("intent_type", intent_type.value)),
                domain=result.get("domain", "islamic_finance"),
                language=result.get("language", language),
                entities=result.get("entities", entities),
                keywords=result.get("keywords", keywords),
            )
        except RuntimeError:
            return IntentResult(
                raw_query=query,
                intent_type=intent_type,
                domain="islamic_finance",
                language=language,
                entities=entities,
                keywords=keywords,
            )
